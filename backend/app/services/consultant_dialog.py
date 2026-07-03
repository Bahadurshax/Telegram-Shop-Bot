"""
Свободный диалог с AI-консультантом в чате Telegram (этап 2).

Клиент после анкеты может задавать уточняющие вопросы обычным текстом:
«а можно дешевле?», «зачем два диска?», «замени купольные на буллеты».

Принципы:
- контекст анкеты и выданного решения наследуется из последнего отчёта,
- история диалога хранится в MongoDB (переживает рестарт бота),
- факты о товарах и ценах Claude берёт только через инструмент search_products,
- объём архива считается только инструментом calc_storage (детерминированно).
"""
import re
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

from ..config import settings
from ..models.product import Product
from ..utils.logger import setup_logger
from .ai_consultant import (
    BUDGET_LABELS,
    CAMERAS_LABELS,
    DISTANCE_LABELS,
    LOCATION_LABELS,
    PLACEMENT_LABELS,
    PURPOSE_LABELS,
    RETENTION_LABELS,
)
from .cctv_advisor import CCTV_ADVISOR_SYSTEM_PROMPT, CameraGroup, calculate_storage
from .cctv_advisor.storage_calc import DEFAULT_BITRATE_BY_RESOLUTION_MBPS
from .product_service import ProductService
from .user_service import UserService

logger = setup_logger(__name__)

# Сколько сообщений истории храним в MongoDB и сколько отдаём в промпт
_HISTORY_STORE_LIMIT = 30
_HISTORY_PROMPT_LIMIT = 12
# Максимум циклов tool use на один ответ
_MAX_TOOL_ROUNDS = 5

DIALOG_MODE_PROMPT = """
РЕЖИМ ДИАЛОГА:
Ты общаешься с клиентом в чате Telegram после выдачи решения по анкете
(анкета и решение — в контексте ниже). Правила:
- Отвечай кратко и по делу: 2-6 предложений, без длинных перечислений.
- Форматирование: обычный текст, можно выделять <b>жирным</b> и <i>курсивом</i>.
  Никакого Markdown (**, ##, списки с -). Символы < и > используй только
  в тегах <b></b> и <i></i>.
- Любые факты о товарах, наличии и ценах бери ТОЛЬКО из инструмента
  search_products. Никогда не выдумывай товары, модели и цены.
- Объём архива и размер диска считай ТОЛЬКО инструментом calc_storage.
- Если подходящего товара нет в каталоге — честно скажи об этом и предложи
  запросить подбор у менеджера (кнопка есть под сообщением).
- Цены называй в сумах.
- Если клиент готов к покупке — напомни, что добавить товары в корзину можно
  кнопками под сообщением с решением или через каталог.
"""

SEARCH_PRODUCTS_TOOL = {
    "name": "search_products",
    "description": (
        "Поиск товаров в каталоге магазина. Возвращает список позиций с ID, "
        "названием, характеристиками и ценой. Все фильтры необязательны (null = не фильтровать)."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": ["string", "null"],
                "description": "Подстрока для поиска по названию и описанию (например 'купольная' или 'WD')",
            },
            "device_type": {
                "type": ["string", "null"],
                "description": "Тип устройства: camera_ip, camera_analog, nvr, dvr, hdd, accessory",
            },
            "outdoor": {
                "type": ["boolean", "null"],
                "description": "true — только уличные камеры, false — только для помещений",
            },
            "min_channels": {
                "type": ["integer", "null"],
                "description": "Минимальное число каналов регистратора",
            },
            "max_price_uzs": {
                "type": ["number", "null"],
                "description": "Максимальная цена в сумах",
            },
        },
        "required": ["query", "device_type", "outdoor", "min_channels", "max_price_uzs"],
        "additionalProperties": False,
    },
}

CALC_STORAGE_TOOL = {
    "name": "calc_storage",
    "description": (
        "Точный расчёт объёма видеоархива и рекомендуемого диска. "
        "Используй для любых вопросов про объём хранения, диски и глубину архива."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "groups": {
                "type": "array",
                "description": "Группы камер с одинаковым разрешением",
                "items": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Число камер в группе"},
                        "resolution_mp": {
                            "type": "number",
                            "description": "Разрешение в мегапикселях: 2, 4, 5 или 8",
                        },
                    },
                    "required": ["count", "resolution_mp"],
                    "additionalProperties": False,
                },
            },
            "retention_days": {"type": "integer", "description": "Сколько дней хранить архив"},
        },
        "required": ["groups", "retention_days"],
        "additionalProperties": False,
    },
}

_KNOWN_DEVICE_TYPES = {"camera_ip", "camera_analog", "nvr", "dvr", "hdd", "accessory"}


def _sanitize_telegram_html(text: str) -> str:
    """Модель иногда игнорирует запрет Markdown — конвертируем в HTML Telegram"""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"^#{1,4}\s+", "", text, flags=re.M)
    return text.strip()


def build_dialog_context(report: Optional[Dict[str, Any]]) -> str:
    """Собрать контекст диалога из последнего отчёта консультации"""
    if not report:
        return (
            "КОНТЕКСТ: клиент ещё не проходил анкету. Сначала выясни вопросами, "
            "что за объект, сколько камер и какие задачи, — потом советуй."
        )

    data = report.get("consultation_data", {})
    rec = report.get("recommendations", {})

    lines = ["КОНТЕКСТ — анкета клиента:"]
    answers = [
        ("Объект", LOCATION_LABELS.get(data.get("location_type", ""))),
        ("Цель", PURPOSE_LABELS.get(data.get("purpose", ""))),
        ("Камер", CAMERAS_LABELS.get(data.get("cameras_count", ""))),
        ("Размещение", PLACEMENT_LABELS.get(data.get("placement", ""))),
        ("Дальность", DISTANCE_LABELS.get(data.get("distance", ""))),
        ("Архив", RETENTION_LABELS.get(data.get("retention", ""))),
        ("Бюджет", BUDGET_LABELS.get(data.get("budget", ""))),
    ]
    lines += [f"- {name}: {value}" for name, value in answers if value]
    if data.get("remote_access") is not None:
        lines.append(f"- Удалённый доступ: {'нужен' if data.get('remote_access') else 'не обязателен'}")

    lines.append("\nВЫДАННОЕ РЕШЕНИЕ:")
    if rec.get("explanation"):
        lines.append(rec["explanation"])
    for zone in rec.get("zones") or []:
        lines.append(f"- Зона «{zone.get('zone', '')}»: {zone.get('spec', '')} × {zone.get('count', 1)}")
    for eq in rec.get("equipment") or []:
        lines.append(f"- {eq.get('item', '')}: {eq.get('spec', '')}")
    if rec.get("storage_summary"):
        lines.append(f"- Архив: {rec['storage_summary']}")

    items = rec.get("items") or []
    if items:
        lines.append("\nПОДОБРАННЫЕ ТОВАРЫ:")
        for item in items:
            lines.append(
                f"- ID {item.get('product_id', '?')} | {item.get('name', '')} × {item.get('quantity', 1)}"
                + (f" — {item['reason']}" if item.get("reason") else "")
            )
    if rec.get("unmatched"):
        lines.append("\nНЕ НАШЛОСЬ В КАТАЛОГЕ: " + "; ".join(rec["unmatched"]))

    return "\n".join(lines)


class ConsultantDialogService:
    """Диалоговый AI-консультант с tool use по каталогу и калькулятору"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else None
        self.product_service = ProductService()
        self.user_service = UserService()

    async def respond(self, telegram_user_id: int, user_text: str) -> str:
        """Ответить на сообщение клиента с учётом контекста и истории"""
        if not self.client:
            return (
                "Диалог с ИИ временно недоступен. Напишите ваш вопрос — "
                "менеджер ответит вам в ближайшее время."
            )

        dialog = await self.user_service.get_consultant_dialog(telegram_user_id) or {}
        context = dialog.get("context") or build_dialog_context(None)
        history = (dialog.get("messages") or [])[-_HISTORY_PROMPT_LIMIT:]

        messages: List[Dict[str, Any]] = [
            {"role": m["role"], "content": m["text"]}
            for m in history
            if m.get("text") and m.get("role") in ("user", "assistant")
        ]
        messages.append({"role": "user", "content": user_text})

        products = await self.product_service.get_products(is_active=True, limit=200)

        try:
            answer = await self._run_tool_loop(context, messages, products)
        except Exception as e:
            logger.error(f"Ошибка диалогового консультанта: {e}")
            return (
                "Не получилось обработать вопрос, попробуйте переформулировать. "
                "Если вопрос срочный — запросите подбор у менеджера кнопкой ниже."
            )

        answer = _sanitize_telegram_html(answer)
        # Страховка от лимита Telegram на длину сообщения (4096)
        if len(answer) > 4000:
            answer = answer[:4000] + "…"

        await self.user_service.append_consultant_dialog(
            telegram_user_id, user_text, answer, limit=_HISTORY_STORE_LIMIT
        )
        return answer

    # ------------------------------------------------------------------
    # Цикл tool use
    # ------------------------------------------------------------------

    async def _run_tool_loop(
        self,
        context: str,
        messages: List[Dict[str, Any]],
        products: List[Product],
    ) -> str:
        system = [
            {
                "type": "text",
                "text": CCTV_ADVISOR_SYSTEM_PROMPT + DIALOG_MODE_PROMPT,
                # Статичная часть промпта — кешируем
                "cache_control": {"type": "ephemeral"},
            },
            {"type": "text", "text": context},
        ]
        tools = [SEARCH_PRODUCTS_TOOL, CALC_STORAGE_TOOL]

        for _ in range(_MAX_TOOL_ROUNDS):
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1200,
                system=system,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                text = "".join(b.text for b in response.content if b.type == "text").strip()
                return text or "Не смог сформулировать ответ, попробуйте спросить иначе."

            # Выполняем запрошенные инструменты и продолжаем диалог
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": self._execute_tool(block.name, block.input, products),
                })
            messages.append({"role": "user", "content": results})

        return (
            "Вопрос оказался сложнее, чем я могу разобрать в чате. "
            "Запросите подбор у менеджера кнопкой ниже — он поможет."
        )

    # ------------------------------------------------------------------
    # Инструменты
    # ------------------------------------------------------------------

    def _execute_tool(self, name: str, args: Dict[str, Any], products: List[Product]) -> str:
        try:
            if name == "search_products":
                return self._search_products(products, args)
            if name == "calc_storage":
                return self._calc_storage(args)
        except Exception as e:
            logger.warning(f"Ошибка инструмента {name}: {e}")
            return f"Ошибка выполнения инструмента: {e}"
        return f"Неизвестный инструмент: {name}"

    def _search_products(self, products: List[Product], args: Dict[str, Any]) -> str:
        query = (args.get("query") or "").strip().lower()
        device_type = args.get("device_type")
        if device_type not in _KNOWN_DEVICE_TYPES:
            device_type = None
        outdoor = args.get("outdoor")
        min_channels = args.get("min_channels")
        max_price = args.get("max_price_uzs")

        matched = []
        for p in products:
            attrs = p.attrs
            if query and query not in f"{p.name} {p.description or ''}".lower():
                continue
            if device_type and (attrs is None or attrs.device_type != device_type):
                continue
            if outdoor is not None and attrs is not None and attrs.outdoor is not None \
                    and attrs.outdoor != outdoor:
                continue
            if min_channels and attrs is not None and attrs.channels is not None \
                    and attrs.channels < min_channels:
                continue
            if max_price and p.price_uzs > max_price:
                continue
            matched.append(p)

        if not matched:
            return "По заданным фильтрам товаров в каталоге не найдено."

        matched.sort(key=lambda p: p.price_uzs)
        lines = []
        for p in matched[:15]:
            details = p.attrs.human_summary() if p.attrs else (p.description or "")[:100]
            lines.append(f"ID {p.id} | {p.name} | {details} | {p.price_uzs:,.0f} сум")
        suffix = f"\n(показаны первые 15 из {len(matched)})" if len(matched) > 15 else ""
        return "\n".join(lines) + suffix

    def _calc_storage(self, args: Dict[str, Any]) -> str:
        groups = []
        for g in args.get("groups", []):
            resolution = float(g.get("resolution_mp") or 2)
            # Ближайшее известное разрешение из таблицы битрейтов
            nearest = min(DEFAULT_BITRATE_BY_RESOLUTION_MBPS, key=lambda r: abs(r - resolution))
            groups.append(CameraGroup(
                name=f"{g.get('count', 1)} камер {nearest}Мп",
                bitrate_mbps=DEFAULT_BITRATE_BY_RESOLUTION_MBPS[nearest],
                count=max(1, int(g.get("count") or 1)),
            ))
        if not groups:
            return "Не переданы группы камер для расчёта."

        retention_days = max(1, int(args.get("retention_days") or 14))
        estimate = calculate_storage(groups, retention_days)
        per_group = "; ".join(
            f"{g['name']}: {g['daily_gb']:.0f} ГБ/сутки" for g in estimate.per_group
        )
        return f"{estimate.human_summary()}. По группам: {per_group}."
