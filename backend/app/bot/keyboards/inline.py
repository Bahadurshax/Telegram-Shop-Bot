from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

from ..utils.messages import *


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_CATALOG, callback_data="catalog"),
        InlineKeyboardButton(text=BUTTON_CONSULTANT, callback_data="consultant")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_CART, callback_data="cart"),
        InlineKeyboardButton(text=BUTTON_HELP, callback_data="help")
    )
    
    return keyboard.as_markup()


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в меню"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    return keyboard.as_markup()


def get_catalog_keyboard(has_products: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура каталога"""
    keyboard = InlineKeyboardBuilder()
    
    if has_products:
        keyboard.row(
            InlineKeyboardButton(text="📱 IP камеры", callback_data="category_ip_cameras"),
            InlineKeyboardButton(text="📹 Аналоговые", callback_data="category_analog")
        )
        keyboard.row(
            InlineKeyboardButton(text="💾 Регистраторы", callback_data="category_dvr"),
            InlineKeyboardButton(text="🔌 Аксессуары", callback_data="category_accessories")
        )
        keyboard.row(
            InlineKeyboardButton(text="🔍 Все товары", callback_data="category_all")
        )
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_product_keyboard(product_id: str, in_cart: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура товара"""
    keyboard = InlineKeyboardBuilder()
    
    if not in_cart:
        keyboard.row(
            InlineKeyboardButton(text=BUTTON_ADD_TO_CART, callback_data=f"add_to_cart_{product_id}")
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="➕ Добавить еще", callback_data=f"add_to_cart_{product_id}"),
            InlineKeyboardButton(text=BUTTON_REMOVE_FROM_CART, callback_data=f"remove_from_cart_{product_id}")
        )
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_BACK, callback_data="catalog"),
        InlineKeyboardButton(text=BUTTON_CART, callback_data="cart")
    )
    
    return keyboard.as_markup()


def get_consultant_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура запуска консультанта"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text="🚀 Начать консультацию", callback_data="consultant_start")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_consultant_location_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора места установки"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_HOME, callback_data="location_home"),
        InlineKeyboardButton(text=BUTTON_OFFICE, callback_data="location_office")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_ORGANIZATION, callback_data="location_organization")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_consultant_cameras_count_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора количества камер"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_CAMERAS_1_4, callback_data="cameras_1_4"),
        InlineKeyboardButton(text=BUTTON_CAMERAS_5_8, callback_data="cameras_5_8")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_CAMERAS_9_16, callback_data="cameras_9_16"),
        InlineKeyboardButton(text=BUTTON_CAMERAS_MORE, callback_data="cameras_more")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_consultant_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура Да/Нет"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_YES, callback_data="answer_yes"),
        InlineKeyboardButton(text=BUTTON_NO, callback_data="answer_no")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_consultant_distance_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора дальности"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_DISTANCE_10M, callback_data="distance_10m"),
        InlineKeyboardButton(text=BUTTON_DISTANCE_30M, callback_data="distance_30m")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_DISTANCE_50M, callback_data="distance_50m"),
        InlineKeyboardButton(text=BUTTON_DISTANCE_100M, callback_data="distance_100m")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_consultant_budget_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора бюджета"""
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_BUDGET_500K, callback_data="budget_500k"),
        InlineKeyboardButton(text=BUTTON_BUDGET_1M, callback_data="budget_1m")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_BUDGET_2M, callback_data="budget_2m"),
        InlineKeyboardButton(text=BUTTON_BUDGET_MORE, callback_data="budget_more")
    )
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_cart_keyboard(has_items: bool = True) -> InlineKeyboardMarkup:
    """Клавиатура корзины"""
    keyboard = InlineKeyboardBuilder()
    
    if has_items:
        keyboard.row(
            InlineKeyboardButton(text=BUTTON_CHECKOUT, callback_data="checkout"),
            InlineKeyboardButton(text=BUTTON_CLEAR_CART, callback_data="clear_cart")
        )
    
    keyboard.row(
        InlineKeyboardButton(text=BUTTON_CATALOG, callback_data="catalog"),
        InlineKeyboardButton(text=BUTTON_MAIN_MENU, callback_data="main_menu")
    )
    
    return keyboard.as_markup()


def get_pagination_keyboard(
    current_page: int, 
    total_pages: int, 
    callback_prefix: str
) -> InlineKeyboardMarkup:
    """Клавиатура пагинации"""
    keyboard = InlineKeyboardBuilder()
    
    buttons = []
    
    # Кнопка "Назад"
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="◀️", 
                callback_data=f"{callback_prefix}_page_{current_page - 1}"
            )
        )
    
    # Информация о странице
    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}", 
            callback_data="current_page"
        )
    )
    
    # Кнопка "Вперед"
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="▶️", 
                callback_data=f"{callback_prefix}_page_{current_page + 1}"
            )
        )
    
    if buttons:
        keyboard.row(*buttons)
    
    return keyboard.as_markup()
