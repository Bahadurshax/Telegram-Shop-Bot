"""
AI-консультант по подбору систем видеонаблюдения.

Логика построена на методологии скилла cctv-solution-advisor:
1) анкета переводится в технические параметры,
2) объём архива считается детерминированно в Python (cctv_advisor.storage_calc),
3) Claude проектирует решение по зонам и подбирает товары из каталога
   через strict tool use (никакого парсинга текста),
4) позиции, которых нет в каталоге, честно попадают в unmatched —
   для них бот предлагает подбор менеджером.
"""
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

from ..config import settings
from ..models.product import Product
from ..utils.logger import setup_logger
from .cctv_advisor import (
    CCTV_ADVISOR_SYSTEM_PROMPT,
    CameraGroup,
    StorageEstimate,
    calculate_storage,
)
from .product_service import ProductService

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Коды ответов анкеты (используются ботом и мини-аппом)
# ---------------------------------------------------------------------------

LOCATION_LABELS = {
    "home": "Дом / квартира",
    "office": "Офис",
    "shop": "Магазин / торговая точка",
    "warehouse": "Склад / производство",
    "organization": "Организация",  # legacy-код старой анкеты
}

PURPOSE_LABELS = {
    "theft": "Защита от краж и проникновений",
    "staff": "Контроль сотрудников и процессов",
    "identify": "Распознавание лиц / номеров авто",
    "general": "Общий контроль обстановки",
}

CAMERAS_LABELS = {
    "1_4": "1-4 камеры",
    "5_8": "5-8 камер",
    "9_16": "9-16 камер",
    "more": "Более 16 камер",
}

PLACEMENT_LABELS = {
    "indoor": "Внутри помещения",
    "outdoor": "На улице",
    "both": "И внутри, и на улице",
}

DISTANCE_LABELS = {
    "10m": "До 10 метров",
    "30m": "До 30 метров",
    "50m": "До 50 метров",
    "100m": "Более 50 метров",
}

RETENTION_LABELS = {
    "7d": "1 неделя",
    "14d": "2 недели",
    "30d": "1 месяц",
    "60d": "2 месяца",
}

BUDGET_LABELS = {
    "500k": "До 500 тыс сум",
    "1m": "500 тыс - 1 млн сум",
    "2m": "1-2 млн сум",
    "more": "Более 2 млн сум",
}

# Оценка числа камер по коду ответа (для расчёта архива и каналов регистратора)
_CAMERAS_ESTIMATE = {"1_4": 4, "5_8": 8, "9_16": 16, "more": 24}
_RETENTION_DAYS = {"7d": 7, "14d": 14, "30d": 30, "60d": 60}

# ---------------------------------------------------------------------------
# Инструмент структурированного ответа консультанта
# ---------------------------------------------------------------------------

SOLUTION_TOOL = {
    "name": "submit_solution",
    "description": "Отдать клиенту готовое решение: зоны, оборудование, подбор товаров из каталога.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "2-4 предложения: какое решение и почему оно закрывает цели клиента.",
            },
            "zones": {
                "type": "array",
                "description": "Карта зон наблюдения с требованиями к камерам.",
                "items": {
                    "type": "object",
                    "properties": {
                        "zone": {"type": "string", "description": "Название зоны, например 'Вход'"},
                        "spec": {"type": "string", "description": "Спецификация камеры: тип, разрешение, ИК и т.п."},
                        "count": {"type": "integer", "description": "Сколько камер в зоне"},
                        "reason": {"type": "string", "description": "Зачем такая камера именно здесь"},
                    },
                    "required": ["zone", "spec", "count", "reason"],
                    "additionalProperties": False,
                },
            },
            "equipment": {
                "type": "array",
                "description": "Прочее оборудование решения: регистратор, диск, питание, сеть.",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string", "description": "Что это: 'Регистратор', 'Жёсткий диск'..."},
                        "spec": {"type": "string", "description": "Требуемая спецификация"},
                        "reason": {"type": "string", "description": "Краткое обоснование"},
                    },
                    "required": ["item", "spec", "reason"],
                    "additionalProperties": False,
                },
            },
            "picks": {
                "type": "array",
                "description": "Подобранные товары из каталога. Только реальные ID из списка.",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "ID товара из каталога"},
                        "quantity": {"type": "integer", "description": "Количество, минимум 1"},
                        "reason": {"type": "string", "description": "Какую позицию решения закрывает"},
                    },
                    "required": ["product_id", "quantity", "reason"],
                    "additionalProperties": False,
                },
            },
            "unmatched": {
                "type": "array",
                "description": "Позиции решения, для которых в каталоге нет подходящего товара.",
                "items": {"type": "string"},
            },
        },
        "required": ["summary", "zones", "equipment", "picks", "unmatched"],
        "additionalProperties": False,
    },
}


class AIConsultantService:
    """Сервис AI-консультанта"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else None
        self.product_service = ProductService()

    async def generate_recommendations(self, consultation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация решения и подбора товаров на основе ответов анкеты"""

        products = await self.product_service.get_products(is_active=True, limit=200)
        storage = self._estimate_storage(consultation_data)

        if not self.client:
            return self._generate_fallback_recommendations(consultation_data, products, storage)

        try:
            candidates = self._select_candidates(products, consultation_data)
            solution = await self._ask_claude(consultation_data, candidates, storage)
            return self._build_result(solution, products, consultation_data, storage)
        except Exception as e:
            logger.error(f"Ошибка AI консультанта: {e}")
            return self._generate_fallback_recommendations(consultation_data, products, storage)

    # ------------------------------------------------------------------
    # Расчёт архива (детерминированный, без LLM)
    # ------------------------------------------------------------------

    def _estimate_storage(self, data: Dict[str, Any]) -> StorageEstimate:
        cameras_total = _CAMERAS_ESTIMATE.get(data.get("cameras_count", ""), 4)
        retention_days = _RETENTION_DAYS.get(data.get("retention", ""), 14)

        # Для задач идентификации закладываем более высокое разрешение
        # (и более тяжёлый поток) на часть камер
        if data.get("purpose") == "identify":
            identify_count = max(1, round(cameras_total / 3))
            groups = [
                CameraGroup(name="Зоны идентификации (4Мп)", bitrate_mbps=6.0, count=identify_count),
            ]
            rest = cameras_total - identify_count
            if rest > 0:
                groups.append(CameraGroup(name="Обзорные зоны (2Мп)", bitrate_mbps=4.0, count=rest))
        else:
            groups = [CameraGroup(name="Камеры наблюдения (2Мп)", bitrate_mbps=4.0, count=cameras_total)]

        return calculate_storage(groups, retention_days)

    # ------------------------------------------------------------------
    # Префильтр каталога по атрибутам
    # ------------------------------------------------------------------

    def _select_candidates(self, products: List[Product], data: Dict[str, Any]) -> List[Product]:
        """Отсекаем заведомо неподходящие товары, чтобы не раздувать промпт.

        Товары без извлечённых атрибутов не отсеиваем — по ним решает Claude
        на основе названия и описания.
        """
        placement = data.get("placement")
        cameras_total = _CAMERAS_ESTIMATE.get(data.get("cameras_count", ""), 4)

        candidates: List[Product] = []
        for product in products:
            attrs = product.attrs
            if attrs is None:
                candidates.append(product)
                continue

            if attrs.device_type in ("camera_ip", "camera_analog"):
                # Камеры, противоречащие размещению, отбрасываем
                if placement == "indoor" and attrs.outdoor is True:
                    continue
                if placement == "outdoor" and attrs.outdoor is False:
                    continue
            elif attrs.device_type in ("nvr", "dvr"):
                # Регистраторы с заведомо недостаточным числом каналов
                if attrs.channels is not None and attrs.channels < cameras_total:
                    continue

            candidates.append(product)

        return candidates

    # ------------------------------------------------------------------
    # Запрос к Claude
    # ------------------------------------------------------------------

    async def _ask_claude(
        self,
        data: Dict[str, Any],
        candidates: List[Product],
        storage: StorageEstimate,
    ) -> Dict[str, Any]:
        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4000,
            system=[{
                "type": "text",
                "text": CCTV_ADVISOR_SYSTEM_PROMPT,
                # Промпт статичен — кешируем, чтобы не платить за него на каждой консультации
                "cache_control": {"type": "ephemeral"},
            }],
            tools=[SOLUTION_TOOL],
            tool_choice={"type": "tool", "name": "submit_solution"},
            messages=[{
                "role": "user",
                "content": self._build_user_prompt(data, candidates, storage),
            }],
        )

        tool_input = next(
            (block.input for block in response.content if block.type == "tool_use"),
            None,
        )
        if tool_input is None:
            raise ValueError("Claude не вернул вызов submit_solution")
        return tool_input

    def _build_user_prompt(
        self,
        data: Dict[str, Any],
        candidates: List[Product],
        storage: StorageEstimate,
    ) -> str:
        products_lines = []
        for product in candidates:
            attrs_summary = product.attrs.human_summary() if product.attrs else ""
            details = attrs_summary or (product.description or "")[:120]
            products_lines.append(
                f"ID {product.id} | {product.name} | {details} | "
                f"{product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)"
            )

        legacy_audio = ""
        if data.get("need_audio") is not None:
            legacy_audio = f"\n- Запись звука: {'нужна' if data.get('need_audio') else 'не нужна'}"

        return f"""АНКЕТА КЛИЕНТА:
- Объект: {LOCATION_LABELS.get(data.get('location_type', ''), 'не указано')}
- Цель наблюдения: {PURPOSE_LABELS.get(data.get('purpose', ''), 'не указана')}
- Количество камер: {CAMERAS_LABELS.get(data.get('cameras_count', ''), 'не указано')}
- Размещение камер: {PLACEMENT_LABELS.get(data.get('placement', ''), 'не указано')}
- Дальность обзора: {DISTANCE_LABELS.get(data.get('distance', ''), 'не указана')}
- Глубина архива: {RETENTION_LABELS.get(data.get('retention', ''), 'не указана')}
- Удалённый доступ с телефона: {'нужен' if data.get('remote_access') else 'не обязателен'}
- Бюджет: {BUDGET_LABELS.get(data.get('budget', ''), 'не указан')}{legacy_audio}

РАСЧЁТ АРХИВА (уже выполнен, используй эти цифры):
{storage.human_summary()}

КАТАЛОГ МАГАЗИНА ({len(products_lines)} позиций):
{chr(10).join(products_lines)}

Составь решение и подбери товары через submit_solution."""

    # ------------------------------------------------------------------
    # Сборка результата
    # ------------------------------------------------------------------

    def _build_result(
        self,
        solution: Dict[str, Any],
        products: List[Product],
        consultation_data: Dict[str, Any],
        storage: StorageEstimate,
    ) -> Dict[str, Any]:
        products_by_id = {p.id: p for p in products}

        items = []
        total_uzs = 0.0
        total_usd = 0.0
        for pick in solution.get("picks", []):
            product = products_by_id.get(pick.get("product_id"))
            if product is None:
                # Claude сослался на несуществующий ID — пропускаем позицию
                logger.warning(f"Консультант вернул неизвестный product_id: {pick.get('product_id')}")
                continue
            quantity = max(1, int(pick.get("quantity") or 1))
            items.append({
                "product": product,
                "quantity": quantity,
                "reason": pick.get("reason", ""),
            })
            total_uzs += product.price_uzs * quantity
            total_usd += product.price_usd * quantity

        return {
            "products": [item["product"] for item in items],
            "product_ids": [item["product"].id for item in items],
            "items": items,
            "explanation": solution.get("summary", ""),
            "zones": solution.get("zones", []),
            "equipment": solution.get("equipment", []),
            "unmatched": solution.get("unmatched", []),
            "storage": {
                "daily_gb": storage.total_daily_gb,
                "period_gb": storage.total_for_period_gb,
                "period_tb": storage.total_for_period_tb,
                "recommended_disk_tb": storage.recommended_disk_tb,
                "retention_days": storage.retention_days,
                "summary": storage.human_summary(),
            },
            "total_uzs": total_uzs,
            "total_usd": total_usd,
            "consultation_summary": self._generate_consultation_summary(consultation_data),
            "ai_response": solution.get("summary", ""),
        }

    # ------------------------------------------------------------------
    # Fallback без AI (нет ключа или ошибка API)
    # ------------------------------------------------------------------

    def _generate_fallback_recommendations(
        self,
        consultation_data: Dict[str, Any],
        products: List[Product],
        storage: StorageEstimate,
    ) -> Dict[str, Any]:
        placement = consultation_data.get("placement")
        cameras_total = _CAMERAS_ESTIMATE.get(consultation_data.get("cameras_count", ""), 4)

        def _is_camera(p: Product) -> bool:
            if p.attrs and p.attrs.device_type:
                return p.attrs.device_type in ("camera_ip", "camera_analog")
            return p.category in ("ip_cameras", "analog")

        def _placement_ok(p: Product) -> bool:
            if not p.attrs or p.attrs.outdoor is None:
                return True
            if placement == "indoor":
                return not p.attrs.outdoor
            if placement == "outdoor":
                return p.attrs.outdoor
            return True

        cameras = [p for p in products if _is_camera(p) and _placement_ok(p)]
        # Предпочитаем IP-камеры
        cameras.sort(key=lambda p: 0 if p.category == "ip_cameras" else 1)

        items = []
        if cameras:
            items.append({
                "product": cameras[0],
                "quantity": cameras_total,
                "reason": "Базовая камера для вашего объекта",
            })

        def _is_recorder(p: Product) -> bool:
            if p.attrs and p.attrs.device_type:
                return p.attrs.device_type in ("nvr", "dvr")
            return p.category in ("nvr", "dvr")

        recorders = [
            p for p in products
            if _is_recorder(p) and (not p.attrs or p.attrs.channels is None or p.attrs.channels >= cameras_total)
        ]
        if recorders:
            items.append({
                "product": recorders[0],
                "quantity": 1,
                "reason": "Регистратор с достаточным числом каналов",
            })

        total_uzs = sum(i["product"].price_uzs * i["quantity"] for i in items)
        total_usd = sum(i["product"].price_usd * i["quantity"] for i in items)

        return {
            "products": [i["product"] for i in items],
            "product_ids": [i["product"].id for i in items],
            "items": items,
            "explanation": (
                "Подбор выполнен по базовым правилам. Для точной конфигурации "
                "рекомендуем связаться с менеджером."
            ),
            "zones": [],
            "equipment": [],
            "unmatched": [],
            "storage": {
                "daily_gb": storage.total_daily_gb,
                "period_gb": storage.total_for_period_gb,
                "period_tb": storage.total_for_period_tb,
                "recommended_disk_tb": storage.recommended_disk_tb,
                "retention_days": storage.retention_days,
                "summary": storage.human_summary(),
            },
            "total_uzs": total_uzs,
            "total_usd": total_usd,
            "consultation_summary": self._generate_consultation_summary(consultation_data),
            "ai_response": "Рекомендации сгенерированы автоматически",
        }

    # ------------------------------------------------------------------
    # Сводка анкеты
    # ------------------------------------------------------------------

    def _generate_consultation_summary(self, data: Dict[str, Any]) -> str:
        lines = [
            f"Объект: {LOCATION_LABELS.get(data.get('location_type', ''), 'Не указано')}",
            f"Цель: {PURPOSE_LABELS.get(data.get('purpose', ''), 'Не указана')}",
            f"Камер: {CAMERAS_LABELS.get(data.get('cameras_count', ''), 'Не указано')}",
            f"Размещение: {PLACEMENT_LABELS.get(data.get('placement', ''), 'Не указано')}",
            f"Дальность: {DISTANCE_LABELS.get(data.get('distance', ''), 'Не указана')}",
            f"Архив: {RETENTION_LABELS.get(data.get('retention', ''), 'Не указан')}",
            f"Удалённый доступ: {'Да' if data.get('remote_access') else 'Нет'}",
            f"Бюджет: {BUDGET_LABELS.get(data.get('budget', ''), 'Не указан')}",
        ]
        return "\n".join(lines)
