from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class OrderStatus(str, Enum):
  NEW = "new"
  PROCESSING = "processing"
  COMPLETED = "completed"
  CANCELLED = "cancelled"


class OrderItem(BaseModel):
  """Товар в заказе"""
  product_id: str = Field(..., description="ID товара")
  product_name: str = Field(..., description="Название товара")
  quantity: int = Field(..., gt=0, description="Количество")
  price_uzs: float = Field(..., description="Цена за единицу в сумах")
  price_usd: float = Field(..., description="Цена за единицу в долларах")


class Order(BaseModel):
  id: Optional[str] = Field(alias="_id", default=None)
  telegram_user_id: int = Field(..., description="ID пользователя в Telegram")
  user_name: str = Field(..., description="Имя клиента")
  user_phone: str = Field(..., description="Телефон клиента")
  user_address: Optional[str] = Field(None, description="Адрес клиента")
  items: List[OrderItem] = Field(..., description="Товары в заказе")
  total_amount_uzs: float = Field(..., description="Общая сумма в сумах")
  total_amount_usd: float = Field(..., description="Общая сумма в долларах")
  consultation_report: Optional[str] = Field(None, description="Отчет AI-консультанта")
  status: OrderStatus = Field(default=OrderStatus.NEW, description="Статус заказа")
  created_at: datetime = Field(default_factory=datetime.utcnow)

  class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "user_name": "Иван Иванов",
                "user_phone": "+998901234567",
                "user_address": "г. Ташкент, ул. Амира Тимура, 1",
                "items": [
                    {
                        "product_id": "507f1f77bcf86cd799439011",
                        "product_name": "IP камера Hikvision",
                        "quantity": 2,
                        "price_uzs": 850000,
                        "price_usd": 75.0
                    }
                ],
                "total_amount_uzs": 1700000,
                "total_amount_usd": 150.0,
                "status": "new"
            }
        }
      