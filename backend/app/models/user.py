from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CartItem(BaseModel):
    """Товар в корзине"""
    product_id: str
    quantity: int = Field(..., gt=0)


class ConsultationData(BaseModel):
    """Данные консультации"""
    location_type: Optional[str] = None  # Дом/Офис/Организация
    cameras_count: Optional[int] = None
    need_audio: Optional[bool] = None
    distance: Optional[str] = None
    budget: Optional[str] = None
    current_step: int = 0
    completed: bool = False


class ConsultationReport(BaseModel):
    """Отчет консультации"""
    date: datetime
    consultation_data: Dict[str, Any]
    recommendations: Dict[str, Any]


class User(BaseModel):
    """Модель пользователя"""
    id: Optional[str] = Field(alias="_id", default=None)
    telegram_user_id: int = Field(..., unique=True, description="ID в Telegram")
    username: Optional[str] = Field(None, description="Username в Telegram")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone: Optional[str] = Field(None, description="Номер телефона")
    cart: List[CartItem] = Field(default_factory=list, description="Корзина")
    consultation_data: ConsultationData = Field(default_factory=ConsultationData)
    consultation_reports: List[Dict[str, Any]] = Field(default_factory=list, description="Отчеты консультаций")
    consultations_count: int = Field(default=0, description="Количество консультаций")
    last_consultation: Optional[datetime] = Field(None, description="Последняя консультация")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "username": "john_doe",
                "first_name": "Иван",
                "last_name": "Иванов",
                "cart": [
                    {
                        "product_id": "507f1f77bcf86cd799439011",
                        "quantity": 2
                    }
                ]
            }
        }


class UserCreate(BaseModel):
    """Модель для создания пользователя"""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None