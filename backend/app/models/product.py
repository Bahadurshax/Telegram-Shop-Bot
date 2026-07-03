from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from bson import ObjectId


# Какие поля attrs применимы к какому типу устройства.
# Валидатор обнуляет неприменимые поля, чтобы в базе не появлялись
# бессмысленные комбинации (например, камера с channels=16).
_ATTRS_APPLICABILITY = {
  "camera_ip": {"resolution_mp", "outdoor", "ir_range_m", "focal_length_mm", "poe", "has_audio", "wdr"},
  "camera_analog": {"resolution_mp", "outdoor", "ir_range_m", "focal_length_mm", "has_audio", "wdr"},
  "nvr": {"channels", "poe_ports", "max_hdd_count"},
  "dvr": {"channels", "max_hdd_count"},
  "hdd": {"capacity_tb"},
  "accessory": {"poe"},
}

_ALL_ATTR_FIELDS = {
  "resolution_mp", "outdoor", "ir_range_m", "focal_length_mm", "poe",
  "has_audio", "wdr", "channels", "poe_ports", "max_hdd_count", "capacity_tb",
}


class ProductAttrs(BaseModel):
  """Структурированные характеристики товара, извлекаются AI при импорте прайса.

  Плоская схема-надмножество: у каждого товара заполнены только поля,
  применимые к его device_type, остальные — None (и не пишутся в MongoDB).
  """
  device_type: Optional[str] = Field(None, description="camera_ip / camera_analog / nvr / dvr / hdd / accessory")

  # Камеры
  resolution_mp: Optional[float] = Field(None, description="Разрешение, Мп")
  outdoor: Optional[bool] = Field(None, description="Уличное исполнение (IP66+)")
  ir_range_m: Optional[int] = Field(None, description="Дальность ИК-подсветки, м")
  focal_length_mm: Optional[str] = Field(None, description="Объектив, мм: '2.8' или '2.8-12'")
  poe: Optional[bool] = Field(None, description="Питание PoE")
  has_audio: Optional[bool] = Field(None, description="Встроенный микрофон / запись звука")
  wdr: Optional[bool] = Field(None, description="Аппаратный WDR")

  # Регистраторы
  channels: Optional[int] = Field(None, description="Число каналов")
  poe_ports: Optional[int] = Field(None, description="Число PoE-портов")
  max_hdd_count: Optional[int] = Field(None, description="Максимум HDD")

  # Диски
  capacity_tb: Optional[float] = Field(None, description="Объём, ТБ")

  @model_validator(mode="after")
  def _drop_inapplicable_fields(self):
    if self.device_type in _ATTRS_APPLICABILITY:
      allowed = _ATTRS_APPLICABILITY[self.device_type]
      for field_name in _ALL_ATTR_FIELDS - allowed:
        object.__setattr__(self, field_name, None)
    return self

  def compact(self) -> dict:
    """Словарь без None-полей — в таком виде attrs хранятся в MongoDB"""
    return self.model_dump(exclude_none=True)

  def human_summary(self) -> str:
    """Однострочное описание для промптов консультанта"""
    parts = []
    type_names = {
      "camera_ip": "IP-камера",
      "camera_analog": "аналоговая камера",
      "nvr": "NVR",
      "dvr": "DVR",
      "hdd": "HDD",
      "accessory": "аксессуар",
    }
    if self.device_type:
      parts.append(type_names.get(self.device_type, self.device_type))
    if self.resolution_mp:
      parts.append(f"{self.resolution_mp:g}Мп")
    if self.outdoor is not None:
      parts.append("улица" if self.outdoor else "помещение")
    if self.ir_range_m:
      parts.append(f"ИК {self.ir_range_m}м")
    if self.focal_length_mm:
      parts.append(f"объектив {self.focal_length_mm}мм")
    if self.poe:
      parts.append("PoE")
    if self.has_audio:
      parts.append("звук")
    if self.wdr:
      parts.append("WDR")
    if self.channels:
      parts.append(f"{self.channels} каналов")
    if self.poe_ports:
      parts.append(f"{self.poe_ports} PoE-портов")
    if self.max_hdd_count:
      parts.append(f"до {self.max_hdd_count} HDD")
    if self.capacity_tb:
      parts.append(f"{self.capacity_tb:g}ТБ")
    return ", ".join(parts)


class Product(BaseModel):
  id: Optional[str] = Field(alias="_id", default=None)
  name: str = Field(..., description="Название товара")
  description: str = Field(..., description="Характеристика товара")
  price_uzs: float = Field(..., description="Цена в сумах")
  price_usd: float = Field(..., description="Цена в долларах")
  usd_rate: float = Field(..., description="Курс доллара")
  image_url: Optional[str] = Field(None, description="Публичный URL изображения в Supabase Storage")
  category: str = Field(default="general", description="Категория товара")
  attrs: Optional[ProductAttrs] = Field(None, description="Структурированные характеристики (AI-извлечение)")
  is_active: bool = Field(default=True, description="Активность товара")
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)

  class Config:
    populate_by_name = True
    json_encoders = {ObjectId: str}
    json_schema_extra = {
      "example": {
        "name": "IP камера Hikvision DS-2CD1043G0-I",
        "description": "4Мп IP камера, ИК подсветка 30м, объектив 2.8мм",
        "price_uzs": 850000,
        "price_usd": 75.0,
        "usd_rate": 11333.33,
        "category": "ip_cameras",
        "is_active": True
      }
    }


class ProductCreate(BaseModel):
  """Модель для создания товара"""
  name: str
  description: str
  price_uzs: float
  price_usd: float
  usd_rate: float
  category: str = "general"
  attrs: Optional[ProductAttrs] = None
  is_active: bool = True
  image_url: Optional[str] = None


class ProductUpdate(BaseModel):
  """Модель для обновления товара"""
  name: Optional[str] = None
  description: Optional[str] = None
  price_uzs: Optional[float] = None
  price_usd: Optional[float] = None
  usd_rate: Optional[float] = None
  category: Optional[str] = None
  attrs: Optional[ProductAttrs] = None
  is_active: Optional[bool] = None
  image_url: Optional[str] = None
