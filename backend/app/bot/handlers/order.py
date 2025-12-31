"""
Обработчики оформления заказов
"""
import re
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ..states.user_states import OrderStates
from ..keyboards.inline import get_main_menu_keyboard
from ..utils.telegram import edit_message_text_or_caption
from ..utils.messages import (
    ORDER_CONTACT_NAME,
    ORDER_CONTACT_PHONE,
    ORDER_CONTACT_ADDRESS,
    ORDER_CONFIRMATION_TEMPLATE,
    ORDER_SUCCESS,
    ERROR_PHONE_FORMAT,
    CART_EMPTY
)
from ...services.order_service import OrderService
from ...services.user_service import UserService
from ...services.product_service import ProductService
from ...services.notification_service import NotificationService

router = Router()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Начать оформление заказа"""
    
    # Проверяем корзину
    user_service = UserService()
    user = await user_service.get_user(callback.from_user.id)
    
    if not user or not user.cart:
        await edit_message_text_or_caption(
            callback.message,
            CART_EMPTY,
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
        return
    
    # Начинаем процесс оформления
    await state.set_state(OrderStates.waiting_name)
    
    await callback.message.edit_text(
        ORDER_CONTACT_NAME,
        reply_markup=None,
    )
    await callback.answer()


@router.message(OrderStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка ввода имени"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа")
        return
    
    # Сохраняем имя
    await state.update_data(user_name=name)
    
    # Переходим к вводу телефона
    await state.set_state(OrderStates.waiting_phone)
    
    # Клавиатура с кнопкой отправки номера
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Отправить номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        ORDER_CONTACT_PHONE,
        reply_markup=phone_keyboard
    )


@router.message(OrderStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка ввода телефона"""
    
    phone = ""
    
    # Если отправлен контакт
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text.strip()
    else:
        await message.answer("❌ Пожалуйста, введите номер телефона или используйте кнопку")
        return
    
    # Валидация телефона
    if not validate_phone(phone):
        await message.answer(
            ERROR_PHONE_FORMAT + "\nПример: +998901234567 или 901234567",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📞 Отправить номер", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return
    
    # Нормализуем номер
    normalized_phone = normalize_phone(phone)
    
    # Сохраняем телефон
    await state.update_data(user_phone=normalized_phone)
    
    # Переходим к адресу
    await state.set_state(OrderStates.waiting_address)
    
    # Клавиатура для пропуска адреса
    skip_keyboard = InlineKeyboardBuilder()
    skip_keyboard.row(
        InlineKeyboardButton(text="⏭ Пропустить адрес", callback_data="skip_address")
    )
    
    await message.answer(
        ORDER_CONTACT_ADDRESS,
        reply_markup=skip_keyboard.as_markup()
    )


@router.callback_query(F.data == "skip_address", OrderStates.waiting_address)
async def skip_address(callback: CallbackQuery, state: FSMContext):
    """Пропустить ввод адреса"""
    await state.update_data(user_address=None)
    await show_order_confirmation(callback, state)


@router.message(OrderStates.waiting_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка ввода адреса"""
    address = message.text.strip()
    
    if len(address) < 5:
        await message.answer("❌ Адрес слишком короткий. Минимум 5 символов")
        return
    
    await state.update_data(user_address=address)
    await show_order_confirmation(message, state)


async def show_order_confirmation(update, state: FSMContext):
    """Показать подтверждение заказа"""
    data = await state.get_data() # Получаем данные из состояния
    
    # Получаем данные корзины
    user_service = UserService()
    product_service = ProductService()
    
    if hasattr(update, 'from_user'):
        user_id = update.from_user.id
    else:
        user_id = update.message.from_user.id
    
    user = await user_service.get_user(user_id)
    
    if not user or not user.cart:
        if hasattr(update, 'message'):
            await edit_message_text_or_caption(
                update.message,
                "❌ Корзина пуста",
                reply_markup=get_main_menu_keyboard(),
            )
        else:
            await update.answer("❌ Корзина пуста", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return
    
    # Формируем список товаров
    items_text = ""
    total_uzs = 0
    total_usd = 0
    
    # 
    for i, cart_item in enumerate(user.cart, 1):
        product = await product_service.get_product(cart_item.product_id)
        if product and product.is_active:
            item_total_uzs = product.price_uzs * cart_item.quantity
            item_total_usd = product.price_usd * cart_item.quantity
            
            items_text += f"{i}. {product.name}\n"
            items_text += f"   {cart_item.quantity} шт. × {product.price_uzs:,.0f} = {item_total_uzs:,.0f} сум\n\n"
            
            total_uzs += item_total_uzs
            total_usd += item_total_usd
    
    # Формируем текст подтверждения
    confirmation_text = ORDER_CONFIRMATION_TEMPLATE.format(
        name=data["user_name"],
        phone=data["user_phone"],
        address=data.get("user_address", "Самовывоз"),
        items=items_text,
        total_uzs=total_uzs,
        total_usd=total_usd
    )
    
    # Сохраняем итоговые суммы
    await state.update_data(total_uzs=total_uzs, total_usd=total_usd)
    
    # Клавиатура подтверждения
    confirmation_keyboard = InlineKeyboardBuilder()
    confirmation_keyboard.row(
        InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")
    )
    
    await state.set_state(OrderStates.confirmation)
    
    if hasattr(update, 'message') and hasattr(update.message, 'edit_text'):
        await edit_message_text_or_caption(
            update.message,
            confirmation_text,
            reply_markup=confirmation_keyboard.as_markup(),
        )
    else:
        await update.answer(
            confirmation_text,
            reply_markup=confirmation_keyboard.as_markup()
        )


@router.callback_query(F.data == "confirm_order", OrderStates.confirmation)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Подтвердить заказ"""
    data = await state.get_data()
    
    try:
        # Создаем заказ
        order_service = OrderService()
        order = await order_service.create_order_from_cart(
            telegram_user_id=callback.from_user.id,
            user_name=data["user_name"],
            user_phone=data["user_phone"],
            user_address=data.get("user_address"),
            consultation_report=None  # TODO: добавить отчет консультации если был
        )
        
        if not order:
            await edit_message_text_or_caption(
                callback.message,
                "❌ Не удалось создать заказ. Корзина пуста или товары недоступны.",
                reply_markup=get_main_menu_keyboard(),
            )
            await callback.answer()
            await state.clear()
            return
        
        # Отправляем уведомление админу
        notification_service = NotificationService(callback.bot)
        await notification_service.notify_new_order(order)
        
        # Показываем успешное сообщение
        success_text = ORDER_SUCCESS.format(order_id=order.id[:8])
        
        await callback.message.edit_text(
            success_text,
            reply_markup=get_main_menu_keyboard(),
        )
        
        await callback.answer("🎉 Заказ успешно оформлен!")
        
    except Exception as e:
        print(f"Ошибка создания заказа: {e}")
        await edit_message_text_or_caption(
            callback.message,
            "❌ Произошла ошибка при оформлении заказа. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer()
    
    await state.clear()


@router.callback_query(F.data == "cancel_order", OrderStates.confirmation)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Отменить заказ"""
    await state.clear()
    
    await edit_message_text_or_caption(
        callback.message,
        "❌ Оформление заказа отменено. Товары остались в корзине.",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


def validate_phone(phone: str) -> bool:
    """Проверка формата телефона"""
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    patterns = [
        r'^\+998\d{9}$',  # +998xxxxxxxxx
        r'^998\d{9}$',    # 998xxxxxxxxx  
        r'^8\d{9}$',      # 8xxxxxxxxx
        r'^\d{9}$'        # xxxxxxxxx
    ]
    
    for pattern in patterns:
        if re.match(pattern, clean_phone):
            return True
    
    return False


def normalize_phone(phone: str) -> str:
    """Нормализация номера телефона"""
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if clean_phone.startswith('+998'):
        return clean_phone
    elif clean_phone.startswith('998'):
        return '+' + clean_phone
    elif clean_phone.startswith('8') and len(clean_phone) == 10:
        return '+998' + clean_phone[1:]
    elif len(clean_phone) == 9:
        return '+998' + clean_phone
    
    return phone


def register_order_handlers(dp):
    """Регистрация обработчиков заказов"""
    dp.include_router(router)