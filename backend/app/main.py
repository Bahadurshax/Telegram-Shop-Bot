"""
Главный файл приложения - Telegram бот + FastAPI админка
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI

from .config import settings
from .database import db
from .utils.logger import setup_logger
from .bot.handlers import register_handlers
from .admin_api.main import create_admin_app
import uvicorn
from uvicorn import Config, Server

# Настраиваем логирование
logger = setup_logger(__name__)


class TelegramShopApp:
    """Основной класс приложения"""
    
    def __init__(self):
        self.bot: Bot = None
        self.dp: Dispatcher = None
        self.admin_app: FastAPI = None
    
    async def setup_bot(self):
        """Инициализация Telegram бота"""
        try:
            # Создаем бота
            self.bot = Bot(
                token=settings.BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            
            # Создаем диспетчер
            self.dp = Dispatcher()
            
            # Регистрируем обработчики
            register_handlers(self.dp)
            
            logger.info("Telegram бот инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    async def setup_admin_app(self):
        """Инициализация админ-панели"""
        try:
            self.admin_app = create_admin_app()
            logger.info("Админ-панель инициализирована")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации админ-панели: {e}")
            raise
    
    async def start(self):
        """Запуск приложения"""
        try:
            # Подключаемся к базе данных
            await db.connect()
            
            # Настраиваем компоненты
            await self.setup_bot()
            await self.setup_admin_app()
            
            # Получаем информацию о боте
            bot_info = await self.bot.get_me()
            logger.info(f"Бот запущен: @{bot_info.username}")

            async def run_bot():
                await self.dp.start_polling(self.bot)
            
            async def run_admin():
                config = Config(app=self.admin_app, host="0.0.0.0", port=8000, log_level="info")
                server = Server(config)
                await server.serve()
            
            await asyncio.gather(run_bot(), run_admin())
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        except Exception as e:
            logger.error(f"Ошибка запуска приложения: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка приложения"""
        logger.info("Остановка приложения...")
        
        if self.bot:
            await self.bot.session.close()
        
        await db.disconnect()
        logger.info("Приложение остановлено")