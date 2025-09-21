from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.inline import get_main_menu_keyboard
from ..utils.messages import START_MESSAGE, HELP_MESSAGE
from ...services.user_service import UserService

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    try:
        # Очищаем состояние
        await state.clear()
        
        # Создаем или обновляем пользователя
        user_service = UserService()
        await user_service.create_or_update_user(
            telegram_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Отправляем приветствие
        await message.answer(
            START_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        await message.answer("❌ Произошла ошибка при запуске бота.", e)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(HELP_MESSAGE)


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    
    await callback.message.edit_text(
        START_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


def register_start_handlers(dp):
    """Регистрация стартовых обработчиков"""
    dp.include_router(router)