from aiogram.types import Message
from typing import Optional


async def edit_message_text_or_caption(
    message: Message,
    text: str,
    reply_markup: Optional[object] = None,
):
    """
    Универсальный helper:
    - если message текстовое -> edit_text
    - если message с фото -> edit_caption

    Это позволяет безопасно редактировать сообщения, которые мы ранее
    превратили в карточку с картинкой (photo + caption).
    """
    # Если это сообщение с фото (caption)
    if getattr(message, "photo", None):
        return await message.edit_caption(text, reply_markup=reply_markup)

    # Обычное текстовое сообщение
    return await message.edit_text(text, reply_markup=reply_markup)


