from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class Product(BaseModel):
  id: Optional[str] = Field(alias="_id", default=None)
  name: str = Field(..., description="Название товара")
  description: str = Field(..., description="Характеристика товара")
  price_uzs: float = Field(..., description="Цена в сумах")
  price_usd: float = Field(..., description="Цена в долларах")
  usd_rate: float = Field(..., description="Курс доллара")
  image_url: Optional[str] = Field(None, description="Публичный URL изображения в Supabase Storage")
  category: str = Field(default="general", description="Категория товара")
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
  is_active: Optional[bool] = None
  image_url: Optional[str] = None