"""
Калькулятор объёма архива видеонаблюдения.

Портирован из скилла cctv-solution-advisor (scripts/storage_calculator.py).
Считается детерминированно в Python — консультант-LLM получает готовые цифры
и не занимается арифметикой.

Формула:
    Объём (ГБ) = (Битрейт[Мбит/с] * 3600 * Часы_записи_в_сутки * Дни) / (8 * 1024)
"""
from dataclasses import dataclass, field
from typing import List

CODEC_SAVINGS = {
    "h264": 1.0,
    "h265": 0.6,   # ~40% экономии относительно H.264
    "h265+": 0.5,  # ~50% экономии
}

# Ориентировочный практический битрейт (Мбит/с) при 25 fps, H.264, средняя сцена
DEFAULT_BITRATE_BY_RESOLUTION_MBPS = {
    2: 4.0,   # 1080p
    4: 6.0,
    5: 7.5,
    8: 12.0,  # 4K
}


@dataclass
class CameraGroup:
    name: str
    bitrate_mbps: float
    hours_recording_per_day: float = 24.0
    codec: str = "h265"
    count: int = 1

    def daily_gb(self) -> float:
        savings = CODEC_SAVINGS.get(self.codec.lower(), 1.0)
        effective_bitrate = self.bitrate_mbps * savings
        gb_per_camera = (effective_bitrate * 3600 * self.hours_recording_per_day) / (8 * 1024)
        return gb_per_camera * self.count


@dataclass
class StorageEstimate:
    total_daily_gb: float
    total_for_period_gb: float
    total_for_period_tb: float
    recommended_disk_tb: float
    retention_days: int
    per_group: List[dict] = field(default_factory=list)

    def human_summary(self) -> str:
        return (
            f"~{self.total_daily_gb:.0f} ГБ/сутки, за {self.retention_days} дней хранения "
            f"~{self.total_for_period_gb:.0f} ГБ ({self.total_for_period_tb:.1f} ТБ); "
            f"рекомендуемый диск с запасом ~25%: {self.recommended_disk_tb:g} ТБ"
        )


def suggest_disk_size_tb(total_tb: float, safety_margin: float = 1.25) -> float:
    """Ближайший стандартный размер диска вверх с запасом (по умолчанию +25%)"""
    standard_sizes_tb = [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    needed = total_tb * safety_margin
    for size in standard_sizes_tb:
        if size >= needed:
            return size
    # Превышает максимум — нужен RAID/несколько дисков
    return standard_sizes_tb[-1]


def calculate_storage(cameras: List[CameraGroup], retention_days: int) -> StorageEstimate:
    per_group = []
    total_daily = 0.0
    for cam in cameras:
        daily = cam.daily_gb()
        total_daily += daily
        per_group.append({
            "name": cam.name,
            "count": cam.count,
            "codec": cam.codec,
            "daily_gb": round(daily, 2),
            "period_gb": round(daily * retention_days, 2),
        })

    total_for_period = total_daily * retention_days
    total_tb = total_for_period / 1024
    return StorageEstimate(
        total_daily_gb=round(total_daily, 2),
        total_for_period_gb=round(total_for_period, 2),
        total_for_period_tb=round(total_tb, 3),
        recommended_disk_tb=suggest_disk_size_tb(total_tb),
        retention_days=retention_days,
        per_group=per_group,
    )
