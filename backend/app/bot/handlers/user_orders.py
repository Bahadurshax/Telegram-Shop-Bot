"""
Обработчик для просмотра заказов пользователя
"""
from aiogram import Router, F, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ..keyboards.inline import get_main_menu_keyboard
from ..utils.telegram import edit_message_text_or_caption
from ...services.order_service import OrderService

router = Router()


@router.message(Command("orders"))
async def cmd_orders(message: Message):
    """Команда просмотра заказов"""
    await show_user_orders(message.from_user.id, message)


@router.callback_query(F.data == "my_orders")
async def callback_orders(callback: CallbackQuery):
    """Callback просмотра заказов"""
    await show_user_orders(callback.from_user.id, callback)


async def show_user_orders(user_id: int, update):
    """Показать заказы пользователя"""
    order_service = OrderService()
    orders = await order_service.get_user_orders(user_id, limit=10)
    
    if not orders:
        text = """
📋 <b>Ваши заказы</b>

У вас пока нет заказов.
Оформите первый заказ через каталог или консультанта!
"""
        keyboard = get_main_menu_keyboard()
    else:
        text = f"📋 <b>Ваши заказы ({len(orders)})</b>\n\n"
        
        # Статусы на русском
        status_map = {
            "new": "🆕 Новый",
            "processing": "⏳ В обработке", 
            "completed": "✅ Выполнен",
            "cancelled": "❌ Отменен"
        }
        
        for i, order in enumerate(orders, 1):
            status = status_map.get(order.status, order.status)
            text += f"<b>{i}. Заказ #{order.id[:8]}</b>\n"
            text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            text += f"📊 Статус: {status}\n"
            text += f"💰 Сумма: {order.total_amount_uzs:,.0f} сум\n"
            text += f"📦 Товаров: {len(order.items)} шт.\n\n"
        
        # Клавиатура
        keyboard = InlineKeyboardBuilder()
        
        # Кнопки для просмотра деталей заказов (первые 3)
        for order in orders[:3]:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"👁 Заказ #{order.id[:8]}",
                    callback_data=f"order_details_{order.id}"
                )
            )
        
        keyboard.row(
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        
        keyboard = keyboard.as_markup()

    if isinstance(update, CallbackQuery):
        await edit_message_text_or_caption(update.message, text, reply_markup=keyboard)
        await update.answer()
    else:
        await update.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("order_details_"))
async def show_order_details(callback: CallbackQuery):
    """Показать детали заказа"""
    order_id = callback.data.split("order_details_")[1]
    
    order_service = OrderService()
    order = await order_service.get_order(order_id)
    
    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return
    
    # Проверяем, что это заказ текущего пользователя
    if order.telegram_user_id != callback.from_user.id:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Статус
    status_map = {
        "new": "🆕 Новый",
        "processing": "⏳ В обработке", 
        "completed": "✅ Выполнен",
        "cancelled": "❌ Отменен"
    }
    
    status = status_map.get(order.status, order.status)
    
    # Формируем детали
    text = f"""
📋 <b>Заказ #{order.id[:8]}</b>

📅 <b>Дата:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
📊 <b>Статус:</b> {status}

👤 <b>Контактные данные:</b>
Имя: {order.user_name}
Телефон: {order.user_phone}
Адрес: {order.user_address or 'Самовывоз'}

🛒 <b>Товары:</b>
"""
    
    for i, item in enumerate(order.items, 1):
        item_total = item.price_uzs * item.quantity
        text += f"{i}. {item.product_name}\n"
        text += f"   {item.quantity} шт. × {item.price_uzs:,.0f} = {item_total:,.0f} сум\n\n"
    
    text += f"💰 <b>Итого:</b> {order.total_amount_uzs:,.0f} сум ({order.total_amount_usd:.0f} $)"
    
    # Клавиатура
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="◀️ К заказам", callback_data="my_orders"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")
    )
    
    await edit_message_text_or_caption(
        callback.message,
        text,
        reply_markup=keyboard.as_markup(),
    )

def register_user_order_handlers(dp: Dispatcher):
    dp.include_router(router)