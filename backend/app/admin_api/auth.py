"""
Аутентификация для админ-панели
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from ..config import settings

security = HTTPBearer()

# Настройки JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Фиктивный хеш: выравнивает время ответа при неверном логине,
# чтобы нельзя было перебором определить имя пользователя
_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt())


def authenticate_admin(username: str, password: str) -> bool:
    """Проверить логин и пароль админа (constant-time)"""
    user_ok = secrets.compare_digest(
        username.encode(), settings.ADMIN_USERNAME.encode()
    )
    stored = settings.ADMIN_PASSWORD_HASH.encode() if user_ok else _DUMMY_HASH
    pass_ok = bcrypt.checkpw(password.encode(), stored)
    return user_ok and pass_ok


def create_admin_token(username: str) -> str:
    """Создать JWT токен для админа"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode = {
        "sub": username,
        "exp": expire,
        "role": "admin"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Проверить JWT токен админа"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role != "admin":
            raise credentials_exception
            
        return username
        
    except JWTError:
        raise credentials_exception