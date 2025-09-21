import logging
import os
from datetime import datetime
from ..config import settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """Настройка логгера"""
    
    # Создаем директорию для логов
    os.makedirs(settings.LOGS_DIR, exist_ok=True)
    
    # Настраиваем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Убираем предыдущие обработчики
    logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик
    log_file = os.path.join(
        settings.LOGS_DIR, 
        f"app_{datetime.now().strftime('%Y_%m_%d')}.log"
    )
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger