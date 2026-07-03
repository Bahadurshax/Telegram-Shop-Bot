"""
Public API AI-консультации для Telegram Mini App
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..telegram_auth import verify_telegram_user
from ...services.ai_consultant import AIConsultantService
from ...services.user_service import UserService
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class ConsultationRequest(BaseModel):
    """Ответы анкеты — коды совпадают с callback-данными бота.

    Новые поля опциональны, чтобы старые клиенты мини-аппа
    (5-вопросная анкета) продолжали работать.
    """
    location_type: str                    # home / office / shop / warehouse / organization
    cameras_count: str                    # 1_4 / 5_8 / 9_16 / more
    budget: str                           # 500k / 1m / 2m / more
    purpose: Optional[str] = None         # theft / staff / identify / general
    placement: Optional[str] = None       # indoor / outdoor / both
    distance: Optional[str] = None        # 10m / 30m / 50m / 100m
    retention: Optional[str] = None       # 7d / 14d / 30d / 60d
    remote_access: Optional[bool] = None
    need_audio: Optional[bool] = None     # legacy-поле старой анкеты


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

    consultation_data = payload.model_dump(exclude_none=True)

    ai_service = AIConsultantService()
    try:
        recommendations = await ai_service.generate_recommendations(consultation_data)
    except Exception as e:
        logger.error(f"Ошибка генерации рекомендаций: {e}")
        raise HTTPException(status_code=502, detail="Не удалось сгенерировать рекомендации")

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
        "products": [
            {
                **item["product"].model_dump(),
                "quantity": item["quantity"],
                "reason": item["reason"],
            }
            for item in recommendations.get("items", [])
        ],
        "explanation": recommendations.get("explanation", ""),
        "zones": recommendations.get("zones", []),
        "equipment": recommendations.get("equipment", []),
        "unmatched": recommendations.get("unmatched", []),
        "storage": recommendations.get("storage", {}),
        "total_uzs": recommendations.get("total_uzs", 0),
        "total_usd": recommendations.get("total_usd", 0),
        "consultation_summary": recommendations.get("consultation_summary", ""),
    }


async def _send_result_to_chat(bot, chat_id: int, recommendations: dict):
    """Отправить рекомендации сообщением в чат с кнопками добавления в корзину"""
    from ...bot.utils.consultant_render import build_result_message

    text, keyboard = build_result_message(recommendations)
    await bot.send_message(chat_id, text, reply_markup=keyboard)
