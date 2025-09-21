"""
Обработчики корзины
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..keyboards.inline import get_cart_keyboard, get_main_menu_keyboard
from ..utils.messages import CART_EMPTY, CART_TEMPLATE, CART_ITEM_TEMPLATE
from ...services.user_service import UserService
from ...services.product_service import ProductService
from ...models.user import CartItem

router = Router()


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """Показать корзину"""
    user_service = UserService()
    user = await user_service.get_user(callback.from_user.id)
    
    if not user or not user.cart:
        await callback.message.edit_text(
            CART_EMPTY,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Получаем детали товаров в корзине
    product_service = ProductService()
    cart_items = []
    total_uzs = 0
    total_usd = 0
    
    for cart_item in user.cart:
        product = await product_service.get_product(cart_item.product_id)
        if product and product.is_active:
            item_total_uzs = product.price_uzs * cart_item.quantity
            item_total_usd = product.price_usd * cart_item.quantity
            
            cart_items.append({
                "product": product,
                "quantity": cart_item.quantity,
                "total_uzs": item_total_uzs,
                "total_usd": item_total_usd
            })
            
            total_uzs += item_total_uzs
            total_usd += item_total_usd
    
    if not cart_items:
        await callback.message.edit_text(
            CART_EMPTY,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Формируем текст корзины
    items_text = ""
    for i, item in enumerate(cart_items, 1):
        items_text += f"{i}. " + CART_ITEM_TEMPLATE.format(
            name=item["product"].name,
            quantity=item["quantity"],
            price_uzs=item["product"].price_uzs,
            total_uzs=item["total_uzs"]
        ) + "\n\n"
    
    text = CART_TEMPLATE.format(
        items=items_text,
        total_uzs=total_uzs,
        total_usd=total_usd
    )
    
    # Создаем клавиатуру с товарами
    from aiogram.types import InlineKeyboardButton
    keyboard = InlineKeyboardBuilder()
    
    # Кнопки для каждого товара
    for item in cart_items:
        product = item["product"]
        keyboard.row(
            InlineKeyboardButton(
                text=f"➖ {product.name[:20]}...",
                callback_data=f"remove_from_cart_{product.id}"
            ),
            InlineKeyboardButton(
                text=f"({item['quantity']})",
                callback_data=f"quantity_{product.id}"
            ),
            InlineKeyboardButton(
                text="➕",
                callback_data=f"add_to_cart_{product.id}"
            )
        )
    
    # Основные кнопки
    keyboard.row(
        InlineKeyboardButton(
            text="✅ Оформить заказ",
            callback_data="checkout"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="🗑 Очистить корзину",
            callback_data="clear_cart"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="🛍 Каталог",
            callback_data="catalog"
        ),
        InlineKeyboardButton(
            text="🏠 Меню",
            callback_data="main_menu"
        )
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """Добавить товар в корзину"""
    product_id = callback.data.split("add_to_cart_")[1]
    
    user_service = UserService()
    product_service = ProductService()
    
    # Проверяем товар
    product = await product_service.get_product(product_id)
    if not product or not product.is_active:
        await callback.answer("❌ Товар недоступен", show_alert=True)
        return
    
    # Получаем пользователя
    user = await user_service.get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ошибка получения данных пользователя", show_alert=True)
        return
    
    # Добавляем в корзину
    success = await user_service.add_to_cart(callback.from_user.id, product_id)
    
    if success:
        await callback.answer("✅ Товар добавлен в корзину")
        # Обновляем отображение товара или корзины
        if "cart" in callback.message.text:
            await show_cart(callback)
    else:
        await callback.answer("❌ Не удалось добавить товар", show_alert=True)


@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback: CallbackQuery):
    """Убрать товар из корзины"""
    product_id = callback.data.split("remove_from_cart_")[1]
    
    user_service = UserService()
    success = await user_service.remove_from_cart(callback.from_user.id, product_id)
    
    if success:
        await callback.answer("➖ Товар убран из корзины")
        await show_cart(callback)  # Обновляем корзину
    else:
        await callback.answer("❌ Не удалось убрать товар", show_alert=True)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Очистить корзину"""
    user_service = UserService()
    success = await user_service.clear_cart(callback.from_user.id)
    
    if success:
        await callback.answer("🗑 Корзина очищена")
        await callback.message.edit_text(
            CART_EMPTY,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.answer("❌ Не удалось очистить корзину", show_alert=True)


# @router.callback_query(F.data == "checkout")
# async def start_checkout(callback: CallbackQuery):
#     """Начать оформление заказа"""
#     # TODO: Реализовать в следующем этапе
#     await callback.answer("🚧 Оформление заказов будет доступно в следующей версии")


def register_cart_handlers(dp):
    """Регистрация обработчиков корзины"""
    dp.include_router(router)