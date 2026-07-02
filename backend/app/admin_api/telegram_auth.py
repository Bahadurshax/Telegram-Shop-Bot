"""
Аутентификация Telegram Mini App через initData.

Мини-апп отправляет window.Telegram.WebApp.initData в заголовке
`Authorization: tma <initData>`. Подпись проверяется по алгоритму из
документации Telegram: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException, status

from ..config import settings

# initData генерируется при открытии мини-аппа; 24 часа — запас,
# чтобы не разлогинивать долго открытое приложение
INIT_DATA_MAX_AGE_SECONDS = 24 * 60 * 60


def validate_init_data(init_data: str, bot_token: str) -> dict:
    """
    Проверить подпись initData и вернуть данные пользователя Telegram.

    Возвращает dict с полями пользователя (id, first_name, username, ...).
    Бросает ValueError, если данные невалидны.
    """
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("initData не содержит hash")

    # Строка проверки: пары key=value, отсортированные по ключу, через \n
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise ValueError("Неверная подпись initData")

    auth_date = int(parsed.get("auth_date", 0))
    if auth_date <= 0 or time.time() - auth_date > INIT_DATA_MAX_AGE_SECONDS:
        raise ValueError("initData устарела")

    try:
        user = json.loads(parsed["user"])
    except (KeyError, json.JSONDecodeError):
        raise ValueError("initData не содержит данных пользователя")

    if not isinstance(user.get("id"), int):
        raise ValueError("Некорректный id пользователя в initData")

    return user


async def verify_telegram_user(authorization: str = Header(...)) -> dict:
    """
    FastAPI-зависимость: проверяет заголовок `Authorization: tma <initData>`
    и возвращает данные пользователя Telegram.
    """
    scheme, _, init_data = authorization.partition(" ")

    if scheme.lower() != "tma" or not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ожидается заголовок Authorization: tma <initData>",
        )

    try:
        return validate_init_data(init_data, settings.BOT_TOKEN)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
