"""
CCTV Solution Advisor — техническая логика подбора систем видеонаблюдения.

Пакет адаптирует скилл cctv-solution-advisor под API-консультанта бота:
- system_prompt.py — системный промпт (методология + технический справочник)
- storage_calc.py — детерминированный расчёт объёма архива
"""
from .system_prompt import CCTV_ADVISOR_SYSTEM_PROMPT
from .storage_calc import CameraGroup, StorageEstimate, calculate_storage, suggest_disk_size_tb

__all__ = [
    "CCTV_ADVISOR_SYSTEM_PROMPT",
    "CameraGroup",
    "StorageEstimate",
    "calculate_storage",
    "suggest_disk_size_tb",
]
