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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Admin auth
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Telegram Admin
    ADMIN_TELEGRAM_ID: Optional[int] = None
    
    # Limits
    MAX_CART_ITEMS: int = 50
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Paths
    UPLOAD_DIR: str = "data/uploads"
    LOGS_DIR: str = "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем экземпляр настроек
settings = Settings()