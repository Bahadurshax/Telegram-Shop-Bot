"""
Скрипт запуска приложения
"""
import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import TelegramShopApp


async def main():
    """Главная функция"""
    app = TelegramShopApp()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Приложение остановлено пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")