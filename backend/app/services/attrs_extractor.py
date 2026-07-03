"""
AI-извлечение структурированных атрибутов товара из названия и характеристики.

Выполняется один раз при импорте прайса (или по кнопке в админке),
а не на каждой консультации — поэтому стоимость на товар копеечная.
"""
import asyncio
from typing import List, Optional, Tuple

from anthropic import AsyncAnthropic

from ..config import settings
from ..models.product import ProductAttrs
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Сколько товаров обогащаем параллельно при импорте прайса
_CONCURRENCY = 4

# device_type -> категория каталога бота
DEVICE_TYPE_TO_CATEGORY = {
    "camera_ip": "ip_cameras",
    "camera_analog": "analog",
    "nvr": "nvr",
    "dvr": "dvr",
    "hdd": "hdd",
    "accessory": "accessories",
}

_NULLABLE_NUMBER = {"type": ["number", "null"]}
_NULLABLE_INTEGER = {"type": ["integer", "null"]}
_NULLABLE_BOOLEAN = {"type": ["boolean", "null"]}

ATTRS_TOOL = {
    "name": "save_product_attrs",
    "description": (
        "Сохранить структурированные характеристики товара видеонаблюдения, "
        "извлечённые из его названия и описания. Если характеристика не указана "
        "в тексте — передай null, ничего не выдумывай."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "device_type": {
                "type": "string",
                "enum": ["camera_ip", "camera_analog", "nvr", "dvr", "hdd", "accessory"],
                "description": (
                    "Тип устройства. camera_analog — AHD/TVI/CVI/Turbo HD камеры. "
                    "hdd — жёсткие диски. accessory — всё прочее (кабели, БП, кронштейны, коммутаторы, микрофоны)."
                ),
            },
            "resolution_mp": {**_NULLABLE_NUMBER, "description": "Разрешение камеры в мегапикселях (2, 4, 5, 8...)"},
            "outdoor": {**_NULLABLE_BOOLEAN, "description": "true — уличное исполнение (IP66/IP67, металлический корпус, буллет), false — для помещений"},
            "ir_range_m": {**_NULLABLE_INTEGER, "description": "Дальность ИК-подсветки в метрах"},
            "focal_length_mm": {"type": ["string", "null"], "description": "Фокусное расстояние объектива: '2.8' или '2.8-12' для вариофокального"},
            "poe": {**_NULLABLE_BOOLEAN, "description": "Поддержка питания PoE"},
            "has_audio": {**_NULLABLE_BOOLEAN, "description": "Встроенный микрофон / поддержка записи звука"},
            "wdr": {**_NULLABLE_BOOLEAN, "description": "Аппаратный WDR (не DWDR)"},
            "channels": {**_NULLABLE_INTEGER, "description": "Число каналов регистратора (4/8/16/32)"},
            "poe_ports": {**_NULLABLE_INTEGER, "description": "Число PoE-портов регистратора"},
            "max_hdd_count": {**_NULLABLE_INTEGER, "description": "Максимальное число HDD в регистраторе"},
            "capacity_tb": {**_NULLABLE_NUMBER, "description": "Объём жёсткого диска в терабайтах"},
        },
        "required": [
            "device_type", "resolution_mp", "outdoor", "ir_range_m", "focal_length_mm",
            "poe", "has_audio", "wdr", "channels", "poe_ports", "max_hdd_count", "capacity_tb",
        ],
        "additionalProperties": False,
    },
}

_SYSTEM = (
    "Ты — парсер прайс-листов оборудования видеонаблюдения. По названию и описанию товара "
    "извлекаешь его характеристики строго из текста: чего в тексте нет — то null. "
    "Не путай DWDR с аппаратным WDR. Тип камеры определяй по технологии: "
    "IP/сетевая — camera_ip; AHD/TVI/CVI/Turbo HD/аналоговая — camera_analog."
)


class AttrsExtractor:
    """Извлечение ProductAttrs через Claude (strict tool use)"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY) if settings.CLAUDE_API_KEY else None

    @property
    def available(self) -> bool:
        return self.client is not None

    async def extract(self, name: str, description: str) -> Optional[ProductAttrs]:
        """Извлечь атрибуты одного товара. None — если API недоступен или произошла ошибка."""
        if not self.client:
            return None

        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_ATTRS_MODEL,
                max_tokens=1024,
                system=_SYSTEM,
                tools=[ATTRS_TOOL],
                tool_choice={"type": "tool", "name": "save_product_attrs"},
                messages=[{
                    "role": "user",
                    "content": f"Название: {name}\nХарактеристика: {description or '(пусто)'}",
                }],
            )
            tool_input = next(
                (block.input for block in response.content if block.type == "tool_use"),
                None,
            )
            if tool_input is None:
                logger.warning(f"Извлечение атрибутов: нет tool_use в ответе для '{name}'")
                return None
            return ProductAttrs(**tool_input)
        except Exception as e:
            logger.warning(f"Ошибка извлечения атрибутов для '{name}': {e}")
            return None

    async def extract_many(
        self, items: List[Tuple[str, str]]
    ) -> List[Optional[ProductAttrs]]:
        """Обогатить список (name, description) с ограничением параллелизма.

        Возвращает список той же длины, ошибки отдельных товаров -> None.
        """
        if not self.client or not items:
            return [None] * len(items)

        semaphore = asyncio.Semaphore(_CONCURRENCY)

        async def _one(name: str, description: str) -> Optional[ProductAttrs]:
            async with semaphore:
                return await self.extract(name, description)

        return list(await asyncio.gather(*(_one(n, d) for n, d in items)))
