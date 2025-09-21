"""
Сервис для работы с пользователями
"""
from typing import Optional
from ..models.user import User
from ..repositories.user_repo import UserRepository


class UserService:
    """Сервис пользователей"""
    def __init__(self):
        self.user_repo = UserRepository()
    
    async def create_or_update_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Создать или обновить пользователя"""
        return await self.user_repo.create_or_update_user(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
       
    
    async def get_user(self, telegram_user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return await self.user_repo.get_user(telegram_user_id)
    
    async def can_use_consultant(self, telegram_user_id: int) -> bool:
        """Проверить, может ли пользователь использовать консультанта"""
        # Лимиты убраны - консультант доступен всегда
        return True
    
    async def add_to_cart(self, telegram_user_id: int, product_id: str, quantity: int = 1) -> bool:
        """Добавить товар в корзину"""
        return await self.user_repo.add_to_cart(
            telegram_user_id=telegram_user_id,
            product_id=product_id,
            quantity=quantity
        )
    
    async def remove_from_cart(self, telegram_user_id: int, product_id: str, quantity: int = 1) -> bool:
        """Убрать товар из корзины"""
        return await self.user_repo.remove_from_cart(
            telegram_user_id=telegram_user_id,
            product_id=product_id,
            quantity=quantity
        )
    
    async def clear_cart(self, telegram_user_id: int) -> bool:
        """Очистить корзину"""
        return await self.user_repo.clear_cart(telegram_user_id)
    
    async def update_consultation_data(
        self, 
        telegram_user_id: int, 
        consultation_data: dict
    ) -> bool:
        """Обновить данные консультации"""
        return await self.user_repo.update_consultation_data(
            telegram_user_id=telegram_user_id,
            consultation_data=consultation_data
        )
    
    async def complete_consultation(self, telegram_user_id: int) -> bool:
        """Завершить консультацию"""
        return await self.user_repo.complete_consultation(telegram_user_id)
    

    async def save_consultation_report(
        self,
        telegram_user_id: int,
        consultation_data: dict,
        recommendations: dict
    ) -> bool:
        """Сохранить отчет консультации"""
        return await self.user_repo.save_consultation_report(
            telegram_user_id=telegram_user_id,
            consultation_data=consultation_data,
            recommendations=recommendations
        )