"""
Регистрация всех обработчиков бота
"""
from aiogram import Dispatcher
from .start import register_start_handlers
from .catalog import register_catalog_handlers
from .consultant import register_consultant_handlers
from .cart import register_cart_handlers
from .order import register_order_handlers
from .user_orders import register_user_order_handlers


def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    register_start_handlers(dp)
    register_catalog_handlers(dp)
    register_consultant_handlers(dp)
    register_cart_handlers(dp)
    register_order_handlers(dp)
    register_user_order_handlers(dp)