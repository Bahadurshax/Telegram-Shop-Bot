"""
Middleware для автоматического создания пользователей
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from ...services.user_service import UserService



class UserMiddleware(BaseMiddleware):
    """Middleware для работы с пользователями"""
    
    def __init__(self):
        self.user_service = UserService()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем пользователя из события
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if user and not user.is_bot:
            try:
                # Создаем или обновляем пользователя
                await self.user_service.create_or_update_user(
                    telegram_user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                
                # Добавляем пользователя в данные
                data["user"] = user
                
            except Exception as e:
                # Логируем ошибку, но не прерываем обработку
                print(f"Ошибка в UserMiddleware: {e}")
        
        # Продолжаем обработку
        return await handler(event, data)
        