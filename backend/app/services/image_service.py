"""
Сервис для загрузки изображений продуктов в Supabase Storage.

Важно: Класс сохраняет название `ImageKitService`, чтобы не менять импорты
в остальных частях приложения, но фактически работает с Supabase.
"""
import mimetypes
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pathlib import Path

from supabase import create_client, Client

from ..config import settings


class ImageKitService:
    """
    Сервис для работы с Supabase Storage (product images).
    """

    def __init__(self):
        # Для бэкенда используем service-role ключ, чтобы обходить RLS-политику
        # на `storage.objects` (загрузка файлов от имени сервера).
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "SUPABASE_URL и SUPABASE_SERVICE_ROLE_KEY должны быть заданы в переменных окружения"
            )

        # Нормализуем URL: нужен базовый URL проекта, без завершающего слэша
        # и без REST-суффикса (клиент сам добавляет /storage/v1 и т.п.;
        # с суффиксом /rest/v1 все запросы к Storage падают с 404)
        base_url = settings.SUPABASE_URL.rstrip("/")
        if base_url.endswith("/rest/v1"):
            base_url = base_url[: -len("/rest/v1")]

        self.client: Client = create_client(
            base_url,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        self.bucket_name: str = settings.SUPABASE_BUCKET

    def upload_image(
        self,
        image_data: bytes,
        filename: str,
        folder: str = "products",
    ) -> Optional[str]:
        """
        Загружает изображение в Supabase Storage.

        Args:
            image_data: Байты изображения
            filename: Имя файла (используется только для расширения)
            folder: Папка внутри bucket (логическая)

        Returns:
            Публичный URL загруженного изображения или None при ошибке
        """
        try:
            extension = Path(filename).suffix or ".png"
            unique_name = f"{uuid4().hex}{extension}"

            # Формируем путь внутри bucket
            normalized_folder = folder.strip("/ ")
            path_in_bucket = (
                f"{normalized_folder}/{unique_name}" if normalized_folder else unique_name
            )

            # Загружаем файл
            storage = self.client.storage.from_(self.bucket_name)
            content_type = mimetypes.guess_type(unique_name)[0] or "image/png"
            # `upload` выбросит исключение при ошибке
            storage.upload(path_in_bucket, image_data, {"content-type": content_type})

            # Получаем публичный URL
            public_url = storage.get_public_url(path_in_bucket)
            return public_url

        except Exception as e:
            print(f"[ERROR] Supabase upload failed for {filename}: {str(e)}")
            return None

    @staticmethod
    def cleanup_temp_folder(folder_path: str, max_age_hours: int = 1) -> int:
        """
        Удаляет старые временные файлы (локальный helper, не связан с Supabase).

        Args:
            folder_path: Путь к папке
            max_age_hours: Максимальный возраст файлов в часах

        Returns:
            Количество удаленных файлов
        """
        if not os.path.exists(folder_path):
            return 0

        deleted_count = 0
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600

        try:
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {str(e)}")

        return deleted_count


# Экземпляр сервиса для использования в других модулях
image_service = ImageKitService()
