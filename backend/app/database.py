import logging
from pymongo import AsyncMongoClient
from gridfs import AsyncGridFSBucket
from typing import Optional
from .config import settings
import pymongo
import certifi

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncMongoClient] = None
        self.database = None
        self.gridfs: Optional[AsyncGridFSBucket] = None
    
    async def connect(self):
        """Подключение к MongoDB"""
        try:
            self.client = AsyncMongoClient(settings.MONGODB_URL, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True), tlsCAFile=certifi.where())
            self.database = self.client[settings.DATABASE_NAME]
            self.gridfs = AsyncGridFSBucket(self.database)
            
            # Проверяем подключение
            await self.client.admin.command('ping')
            logger.info(f"Подключено к MongoDB: {settings.DATABASE_NAME}")
            
            # Создаем индексы
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Ошибка подключения к MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от MongoDB"""
        if self.client:
            await self.client.close()
            logger.info("Отключено от MongoDB")
    
    async def _create_indexes(self):
        """Создание индексов для коллекций"""
        try:
            # Индексы для пользователей
            await self.database.users.create_index("telegram_user_id", unique=True)
            await self.database.users.create_index("created_at")
            
            # Индексы для товаров
            await self.database.products.create_index("name")
            await self.database.products.create_index("category")
            await self.database.products.create_index("is_active")
            await self.database.products.create_index("created_at")
            
            # Индексы для заказов
            await self.database.orders.create_index("telegram_user_id")
            await self.database.orders.create_index("status")
            await self.database.orders.create_index("created_at")
            
            logger.info("Индексы MongoDB созданы успешно")
            
        except Exception as e:
            logger.error(f"Ошибка создания индексов: {e}")


# Создаем экземпляр базы данных
db = Database()


# Функции для получения коллекций
def get_users_collection():
    """Получить коллекцию пользователей"""
    return db.database.users


def get_products_collection():
    """Получить коллекцию товаров"""
    return db.database.products


def get_orders_collection():  
    """Получить коллекцию заказов"""
    return db.database.orders


def get_gridfs():
    """Получить GridFS для файлов"""
    return db.gridfs