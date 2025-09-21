"""
Обработчики AI-консультанта
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..keyboards.inline import (
    get_consultant_start_keyboard,
    get_consultant_location_keyboard,
    get_consultant_cameras_count_keyboard,
    get_consultant_yes_no_keyboard,
    get_consultant_distance_keyboard,
    get_consultant_budget_keyboard,
    get_main_menu_keyboard
)
from ..states.user_states import ConsultantStates
from ..utils.messages import (
    CONSULTANT_START,
    CONSULTANT_QUESTION_1,
    CONSULTANT_QUESTION_2,
    CONSULTANT_QUESTION_3,
    CONSULTANT_QUESTION_4, 
    CONSULTANT_QUESTION_5,
    CONSULTANT_PROCESSING,
    CONSULTANT_RESULT_TEMPLATE
)
from ...services.ai_consultant import AIConsultantService
from ...services.user_service import UserService

router = Router()


@router.callback_query(F.data == "consultant")
async def show_consultant_start(callback: CallbackQuery, state: FSMContext):
    """Показать стартовое меню консультанта"""
    await state.clear()
    
    await callback.message.edit_text(
        CONSULTANT_START,
        reply_markup=get_consultant_start_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "consultant_start")
async def start_consultation(callback: CallbackQuery, state: FSMContext):
    """Начать консультацию"""
    await state.set_state(ConsultantStates.waiting_location)
    
    # Инициализируем данные консультации
    await state.update_data(consultation_data={})
    
    await callback.message.edit_text(
        CONSULTANT_QUESTION_1,
        reply_markup=get_consultant_location_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("location_"), ConsultantStates.waiting_location)
async def process_location(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора места установки"""
    location = callback.data.split("location_")[1]
    
    # Сохраняем ответ
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["location_type"] = location
    await state.update_data(consultation_data=consultation_data)
    
    # Переходим к следующему вопросу
    await state.set_state(ConsultantStates.waiting_cameras_count)
    
    await callback.message.edit_text(
        CONSULTANT_QUESTION_2,
        reply_markup=get_consultant_cameras_count_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cameras_"), ConsultantStates.waiting_cameras_count)
async def process_cameras_count(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора количества камер"""
    cameras = callback.data.split("cameras_")[1]
    
    # Сохраняем ответ
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["cameras_count"] = cameras
    await state.update_data(consultation_data=consultation_data)
    
    # Переходим к следующему вопросу
    await state.set_state(ConsultantStates.waiting_audio)
    
    await callback.message.edit_text(
        CONSULTANT_QUESTION_3,
        reply_markup=get_consultant_yes_no_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("answer_"), ConsultantStates.waiting_audio)
async def process_audio_need(callback: CallbackQuery, state: FSMContext):
    """Обработка вопроса о записи звука"""
    need_audio = callback.data == "answer_yes"
    
    # Сохраняем ответ
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["need_audio"] = need_audio
    await state.update_data(consultation_data=consultation_data)
    
    # Переходим к следующему вопросу
    await state.set_state(ConsultantStates.waiting_distance)
    
    await callback.message.edit_text(
        CONSULTANT_QUESTION_4,
        reply_markup=get_consultant_distance_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("distance_"), ConsultantStates.waiting_distance)
async def process_distance(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора дальности"""
    distance = callback.data.split("distance_")[1]
    
    # Сохраняем ответ
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["distance"] = distance
    await state.update_data(consultation_data=consultation_data)
    
    # Переходим к последнему вопросу
    await state.set_state(ConsultantStates.waiting_budget)
    
    await callback.message.edit_text(
        CONSULTANT_QUESTION_5,
        reply_markup=get_consultant_budget_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("budget_"), ConsultantStates.waiting_budget)
async def process_budget_and_generate_recommendations(callback: CallbackQuery, state: FSMContext):
    """Обработка бюджета и генерация рекомендаций"""
    budget = callback.data.split("budget_")[1]
    
    # Сохраняем ответ
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["budget"] = budget
    
    # Устанавливаем состояние обработки
    await state.set_state(ConsultantStates.processing)
    
    # Показываем сообщение о обработке
    await callback.message.edit_text(
        CONSULTANT_PROCESSING,
        reply_markup=None
    )
    await callback.answer()
    
    # Генерируем рекомендации через AI
    ai_service = AIConsultantService()
    try:
        recommendations = await ai_service.generate_recommendations(consultation_data)
        
        # Сохраняем отчет консультации для пользователя
        user_service = UserService()
        await user_service.save_consultation_report(
            callback.from_user.id,
            consultation_data,
            recommendations
        )
        
        # Формируем текст с рекомендациями
        products_text = ""
        for i, product in enumerate(recommendations["products"], 1):
            products_text += f"{i}. {product.name}\n"
            products_text += f"   💰 {product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)\n\n"
        
        result_text = CONSULTANT_RESULT_TEMPLATE.format(
            location=recommendations["consultation_summary"].split('\n')[0].split(': ')[1],
            cameras_count=recommendations["consultation_summary"].split('\n')[1].split(': ')[1],
            audio=recommendations["consultation_summary"].split('\n')[2].split(': ')[1],
            distance=recommendations["consultation_summary"].split('\n')[3].split(': ')[1],
            budget=recommendations["consultation_summary"].split('\n')[4].split(': ')[1],
            recommendations=products_text,
            total_price=f"{recommendations['total_uzs']:,.0f} сум ({recommendations['total_usd']:.0f} $)"
        )
        
        # Добавляем объяснение
        if recommendations.get("explanation"):
            result_text += f"\n💡 <b>Пояснение:</b>\n{recommendations['explanation']}\n"
        
        # Создаем клавиатуру с товарами
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        
        keyboard = InlineKeyboardBuilder()
        
        # Кнопки товаров для добавления в корзину
        for product in recommendations["products"]:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"➕ {product.name[:25]}...",
                    callback_data=f"add_to_cart_{product.id}"
                )
            )
        
        # Основные кнопки
        keyboard.row(
            InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
            InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")
        )
        keyboard.row(
            InlineKeyboardButton(text="🔄 Новая консультация", callback_data="consultant"),
            InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu")
        )
        
        await callback.message.edit_text(
            result_text,
            reply_markup=keyboard.as_markup()
        )
        
    except Exception as e:
        print(f"Ошибка генерации рекомендаций: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при генерации рекомендаций. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )
    
    # Очищаем состояние
    await state.clear()


def register_consultant_handlers(dp):
    """Регистрация обработчиков консультанта"""
    dp.include_router(router)