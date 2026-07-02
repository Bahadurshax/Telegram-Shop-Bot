import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook"
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    
    # Claude AI
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
    
    # Admin API
    ADMIN_API_HOST: str = os.getenv("ADMIN_API_HOST", "127.0.0.1")
    ADMIN_API_PORT: int = int(os.getenv("ADMIN_API_PORT", "8000"))
    SECRET_KEY: str  # обязательное поле — приложение не стартует без него

    # Admin auth
    ADMIN_USERNAME: str  # обязательное поле
    ADMIN_PASSWORD_HASH: str  # bcrypt-хеш пароля, не сам пароль
    
    # Telegram Admin
    ADMIN_TELEGRAM_ID: Optional[int] = None

    # Telegram Mini App (если задан — кнопка консультанта открывает мини-апп)
    MINI_APP_URL: str = os.getenv("MINI_APP_URL", "")
    
    # Limits
    MAX_CART_ITEMS: int = 50
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Paths
    UPLOAD_DIR: str = "data/uploads"
    LOGS_DIR: str = "logs"
    
    # Supabase Storage (for product images)
    # URL проекта (как в Dashboard, без /storage/v1)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    # На фронтенде можно использовать ANON KEY, но бэкенд для загрузки файлов
    # должен использовать SERVICE ROLE KEY, чтобы обходить RLS.
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "product-images")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем экземпляр настроек
settings = Settings()