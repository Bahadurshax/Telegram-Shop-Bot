"""
Public API AI-консультации для Telegram Mini App
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..telegram_auth import verify_telegram_user
from ...services.ai_consultant import AIConsultantService
from ...services.user_service import UserService
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class ConsultationRequest(BaseModel):
    """Ответы анкеты — коды совпадают с callback-данными бота"""
    location_type: str  # home / office / organization
    cameras_count: str  # 1_4 / 5_8 / 9_16 / more
    need_audio: bool
    distance: str       # 10m / 30m / 50m / 100m
    budget: str         # 500k / 1m / 2m / more


@router.post("/consultation")
async def create_consultation(
    payload: ConsultationRequest,
    request: Request,
    tg_user: dict = Depends(verify_telegram_user),
):
    """Сгенерировать рекомендации по анкете и сохранить отчет пользователю"""
    user_service = UserService()

    # Пользователь мог открыть мини-апп до первого /start в боте
    await user_service.create_or_update_user(
        telegram_user_id=tg_user["id"],
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
    )

    consultation_data = payload.model_dump()

    ai_service = AIConsultantService()
    try:
        recommendations = await ai_service.generate_recommendations(consultation_data)
    except Exception as e:
        logger.error(f"Ошибка генерации рекомендаций: {e}")
        raise HTTPException(status_code=502, detail="Не удалось сгенерировать рекомендации")

    recommendations["product_ids"] = [p.id for p in recommendations["products"]]

    await user_service.save_consultation_report(
        tg_user["id"], consultation_data, recommendations
    )

    # Дублируем результат в чат с ботом (бот и API живут в одном процессе)
    bot = getattr(request.app.state, "bot", None)
    if bot:
        try:
            await _send_result_to_chat(bot, tg_user["id"], recommendations)
        except Exception as e:
            logger.warning(f"Не удалось отправить результат в чат {tg_user['id']}: {e}")

    return {
        "products": [p.model_dump() for p in recommendations["products"]],
        "explanation": recommendations.get("explanation", ""),
        "total_uzs": recommendations.get("total_uzs", 0),
        "total_usd": recommendations.get("total_usd", 0),
        "consultation_summary": recommendations.get("consultation_summary", ""),
    }


async def _send_result_to_chat(bot, chat_id: int, recommendations: dict):
    """Отправить рекомендации сообщением в чат с кнопками добавления в корзину"""
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    products_text = ""
    for i, product in enumerate(recommendations["products"], 1):
        products_text += f"{i}. {product.name}\n"
        products_text += f"   💰 {product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)\n\n"

    text = (
        "🤖 <b>Результаты консультации</b>\n\n"
        f"{recommendations.get('consultation_summary', '')}\n\n"
        f"<b>Рекомендуемые товары:</b>\n{products_text}"
        f"💰 <b>Итого:</b> {recommendations.get('total_uzs', 0):,.0f} сум "
        f"({recommendations.get('total_usd', 0):.0f} $)"
    )
    if recommendations.get("explanation"):
        text += f"\n\n💡 <b>Пояснение:</b>\n{recommendations['explanation']}"

    keyboard = InlineKeyboardBuilder()
    for product in recommendations["products"]:
        keyboard.row(
            InlineKeyboardButton(
                text=f"➕ {product.name[:25]}...",
                callback_data=f"add_to_cart_{product.id}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu"),
    )

    await bot.send_message(chat_id, text, reply_markup=keyboard.as_markup())
