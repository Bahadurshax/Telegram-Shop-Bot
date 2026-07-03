"""
Обработчики AI-консультанта: анкета из 8 вопросов и свободный диалог
"""
import asyncio
import re

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ...config import settings
from ..keyboards.inline import (
    get_consultant_start_keyboard,
    get_consultant_location_keyboard,
    get_consultant_purpose_keyboard,
    get_consultant_cameras_count_keyboard,
    get_consultant_placement_keyboard,
    get_consultant_distance_keyboard,
    get_consultant_retention_keyboard,
    get_consultant_yes_no_keyboard,
    get_consultant_budget_keyboard,
    get_consultant_chat_keyboard,
    get_main_menu_keyboard,
)
from ..states.user_states import ConsultantStates
from ..utils.consultant_render import build_result_message
from ..utils.messages import (
    CONSULTANT_START,
    CONSULTANT_QUESTION_LOCATION,
    CONSULTANT_QUESTION_PURPOSE,
    CONSULTANT_QUESTION_CAMERAS,
    CONSULTANT_QUESTION_PLACEMENT,
    CONSULTANT_QUESTION_DISTANCE,
    CONSULTANT_QUESTION_RETENTION,
    CONSULTANT_QUESTION_REMOTE,
    CONSULTANT_QUESTION_BUDGET,
    CONSULTANT_PROCESSING,
    CONSULTANT_MANAGER_REQUESTED,
    CONSULTANT_CHAT_INTRO,
    CONSULTANT_CHAT_ENDED,
)
from ...services.ai_consultant import AIConsultantService
from ...services.consultant_dialog import ConsultantDialogService, build_dialog_context
from ...services.user_service import UserService

router = Router()

# Минимальный интервал между обновлениями черновика (сек), чтобы не упереться
# в лимиты Telegram, но при этом сохранить эффект «живой печати».
_DRAFT_THROTTLE = 0.6
# Тег незакрытого HTML-хвоста в конце обрезанного черновика
_UNCLOSED_TAG_RE = re.compile(r"<[^>]*$")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _plain_for_draft(text: str) -> str:
    """Черновик показываем как обычный текст: убираем HTML-теги, чтобы
    незакрытый на середине генерации тег (<b без </b>) не ломал показ."""
    text = _HTML_TAG_RE.sub("", text)
    text = _UNCLOSED_TAG_RE.sub("", text)
    return text[:4096]


async def _send_draft(bot, chat_id: int, draft_id: int, text: str) -> None:
    """Обновить черновик-«печатает». Ошибки глушим: если стриминг черновиков
    недоступен, клиент всё равно получит финальное сообщение."""
    try:
        await bot.send_message_draft(
            chat_id=chat_id,
            draft_id=draft_id,
            text=_plain_for_draft(text),
            parse_mode=None,
        )
    except Exception:
        pass


async def _save_answer(state: FSMContext, key: str, value):
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data[key] = value
    await state.update_data(consultation_data=consultation_data)


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
    await state.update_data(consultation_data={})

    await callback.message.edit_text(
        CONSULTANT_QUESTION_LOCATION,
        reply_markup=get_consultant_location_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("location_"), ConsultantStates.waiting_location)
async def process_location(callback: CallbackQuery, state: FSMContext):
    """Вопрос 1: тип объекта"""
    await _save_answer(state, "location_type", callback.data.split("location_")[1])
    await state.set_state(ConsultantStates.waiting_purpose)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_PURPOSE,
        reply_markup=get_consultant_purpose_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("purpose_"), ConsultantStates.waiting_purpose)
async def process_purpose(callback: CallbackQuery, state: FSMContext):
    """Вопрос 2: цель наблюдения"""
    await _save_answer(state, "purpose", callback.data.split("purpose_")[1])
    await state.set_state(ConsultantStates.waiting_cameras_count)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_CAMERAS,
        reply_markup=get_consultant_cameras_count_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cameras_"), ConsultantStates.waiting_cameras_count)
async def process_cameras_count(callback: CallbackQuery, state: FSMContext):
    """Вопрос 3: количество камер"""
    await _save_answer(state, "cameras_count", callback.data.split("cameras_")[1])
    await state.set_state(ConsultantStates.waiting_placement)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_PLACEMENT,
        reply_markup=get_consultant_placement_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("placement_"), ConsultantStates.waiting_placement)
async def process_placement(callback: CallbackQuery, state: FSMContext):
    """Вопрос 4: размещение камер"""
    await _save_answer(state, "placement", callback.data.split("placement_")[1])
    await state.set_state(ConsultantStates.waiting_distance)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_DISTANCE,
        reply_markup=get_consultant_distance_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("distance_"), ConsultantStates.waiting_distance)
async def process_distance(callback: CallbackQuery, state: FSMContext):
    """Вопрос 5: дальность обзора"""
    await _save_answer(state, "distance", callback.data.split("distance_")[1])
    await state.set_state(ConsultantStates.waiting_retention)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_RETENTION,
        reply_markup=get_consultant_retention_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("retention_"), ConsultantStates.waiting_retention)
async def process_retention(callback: CallbackQuery, state: FSMContext):
    """Вопрос 6: глубина архива"""
    await _save_answer(state, "retention", callback.data.split("retention_")[1])
    await state.set_state(ConsultantStates.waiting_remote)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_REMOTE,
        reply_markup=get_consultant_yes_no_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("answer_"), ConsultantStates.waiting_remote)
async def process_remote_access(callback: CallbackQuery, state: FSMContext):
    """Вопрос 7: удалённый доступ"""
    await _save_answer(state, "remote_access", callback.data == "answer_yes")
    await state.set_state(ConsultantStates.waiting_budget)

    await callback.message.edit_text(
        CONSULTANT_QUESTION_BUDGET,
        reply_markup=get_consultant_budget_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("budget_"), ConsultantStates.waiting_budget)
async def process_budget_and_generate_recommendations(callback: CallbackQuery, state: FSMContext):
    """Вопрос 8: бюджет — и генерация решения"""
    data = await state.get_data()
    consultation_data = data.get("consultation_data", {})
    consultation_data["budget"] = callback.data.split("budget_")[1]

    await state.set_state(ConsultantStates.processing)
    await callback.message.edit_text(CONSULTANT_PROCESSING, reply_markup=None)
    await callback.answer()

    ai_service = AIConsultantService()
    try:
        recommendations = await ai_service.generate_recommendations(consultation_data)

        user_service = UserService()
        await user_service.save_consultation_report(
            callback.from_user.id,
            consultation_data,
            recommendations
        )

        text, keyboard = build_result_message(recommendations)
        await callback.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        print(f"Ошибка генерации рекомендаций: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при генерации рекомендаций. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )

    await state.clear()


@router.callback_query(F.data == "consult_chat")
async def start_dialog(callback: CallbackQuery, state: FSMContext):
    """Начать свободный диалог с ИИ по выданному решению"""
    user_service = UserService()

    # Контекст — последняя консультация клиента (из бота или мини-аппа)
    reports = []
    try:
        db_user = await user_service.get_user(callback.from_user.id)
        reports = getattr(db_user, "consultation_reports", None) or []
    except Exception as e:
        print(f"Не удалось получить отчёты клиента {callback.from_user.id}: {e}")

    context = build_dialog_context(reports[-1] if reports else None)
    await user_service.start_consultant_dialog(callback.from_user.id, context)

    await state.set_state(ConsultantStates.chatting)
    await callback.message.answer(
        CONSULTANT_CHAT_INTRO,
        reply_markup=get_consultant_chat_keyboard()
    )
    await callback.answer()


@router.message(ConsultantStates.chatting, F.text, ~F.text.startswith("/"))
async def process_dialog_message(message: Message, state: FSMContext):
    """Сообщение клиента в режиме диалога с ИИ.

    Ответ стримится черновиком (send_message_draft) — клиент видит, как
    консультант «печатает» вживую, а затем приходит финальное сообщение.
    """
    bot = message.bot
    chat_id = message.chat.id
    # draft_id должен быть ненулевым; message_id входящего сообщения уникален
    draft_id = message.message_id or 1

    # Пустой черновик сразу показывает нативное «Печатает…»
    await _send_draft(bot, chat_id, draft_id, "")

    dialog_service = ConsultantDialogService()

    final_answer = None
    last_sent = 0.0
    last_text = ""
    loop = asyncio.get_running_loop()

    async for is_final, text in dialog_service.respond_stream(message.from_user.id, message.text):
        if is_final:
            final_answer = text
            break
        now = loop.time()
        if text and text != last_text and (now - last_sent) >= _DRAFT_THROTTLE:
            await _send_draft(bot, chat_id, draft_id, text)
            last_sent = now
            last_text = text

    if not final_answer:
        final_answer = "Не смог сформулировать ответ, попробуйте спросить иначе."

    # Финальное сообщение (HTML по умолчанию) — оно замещает черновик
    try:
        await message.answer(final_answer, reply_markup=get_consultant_chat_keyboard())
    except TelegramBadRequest:
        # Ответ сломал HTML-разметку — отправляем без форматирования
        await message.answer(
            final_answer, parse_mode=None, reply_markup=get_consultant_chat_keyboard()
        )


@router.callback_query(F.data == "consult_chat_end")
async def end_dialog(callback: CallbackQuery, state: FSMContext):
    """Завершить диалог с ИИ"""
    await state.clear()

    await callback.message.answer(
        CONSULTANT_CHAT_ENDED,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "consult_manager")
async def request_manager(callback: CallbackQuery):
    """Клиент просит подбор менеджером — уведомляем админа"""
    user = callback.from_user

    if settings.ADMIN_TELEGRAM_ID:
        username = f"@{user.username}" if user.username else "без username"
        contact = f"{user.full_name} ({username}, id {user.id})"

        # Достаём последнюю консультацию клиента для контекста
        details = ""
        try:
            user_service = UserService()
            db_user = await user_service.get_user(user.id)
            reports = getattr(db_user, "consultation_reports", None) or []
            if reports:
                last = reports[-1]
                summary = last.get("consultation_data", {})
                lines = [f"  {k}: {v}" for k, v in summary.items()]
                details = "\n\n📋 Последняя анкета:\n" + "\n".join(lines)
        except Exception as e:
            print(f"Не удалось получить анкету клиента {user.id}: {e}")

        try:
            await callback.bot.send_message(
                settings.ADMIN_TELEGRAM_ID,
                f"📞 <b>Запрос подбора от клиента</b>\n\n{contact}{details}"
            )
        except Exception as e:
            print(f"Не удалось уведомить администратора: {e}")

    await callback.message.answer(
        CONSULTANT_MANAGER_REQUESTED,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer("Заявка отправлена")


def register_consultant_handlers(dp):
    """Регистрация обработчиков консультанта"""
    dp.include_router(router)
