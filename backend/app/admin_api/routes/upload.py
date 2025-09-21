"""
API для загрузки файлов и парсинга прайс-листов
"""
import io
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import pandas as pd

from ..auth import verify_admin_token
from ...services.product_service import ProductService
from ...models.product import ProductCreate
from ...config import settings

router = APIRouter()


@router.post("/upload/pricelist")
async def upload_pricelist(
    file: UploadFile = File(...),
    admin: str = Depends(verify_admin_token)
):
    """Загрузить и обработать прайс-лист"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не выбран")
    
    # Проверяем тип файла
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400, 
            detail="Поддерживаются только файлы Excel (.xlsx, .xls) и CSV"
        )
    
    try:
        # Читаем файл
        content = await file.read()
        
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Ожидаемые столбцы (по порядку)
        expected_columns = [
            'name',           # Наименование товара
            'image',          # Фото товара (ссылка или путь)
            'description',    # Характеристика товара
            'price_uzs',      # Цена в сумах
            'price_usd',      # Цена в долларах
            'usd_rate'        # Курс доллара
        ]
        
        # Если количество столбцов не совпадает, пытаемся угадать по названиям
        if len(df.columns) >= 6:
            # Используем первые 6 столбцов
            df = df.iloc[:, :6]
            df.columns = expected_columns
        else:
            # Пытаемся найти столбцы по названиям
            column_mapping = {}
            for col in df.columns:
                col_lower = str(col).lower()
                if any(word in col_lower for word in ['название', 'наименование', 'товар', 'name']):
                    column_mapping['name'] = col
                elif any(word in col_lower for word in ['фото', 'изображение', 'картинка', 'image']):
                    column_mapping['image'] = col
                elif any(word in col_lower for word in ['описание', 'характеристика', 'description']):
                    column_mapping['description'] = col
                elif any(word in col_lower for word in ['сум', 'uzs', 'цена']):
                    if 'price_uzs' not in column_mapping:
                        column_mapping['price_uzs'] = col
                elif any(word in col_lower for word in ['доллар', 'usd',
                ]):
                    column_mapping['price_usd'] = col
                elif any(word in col_lower for word in ['курс', 'rate']):
                    column_mapping['usd_rate'] = col
            
            # Проверяем, что нашли основные столбцы
            required_cols = ['name', 'price_uzs']
            missing_cols = [col for col in required_cols if col not in column_mapping]
            if missing_cols:
                raise HTTPException(
                    status_code=400,
                    detail=f"Не найдены обязательные столбцы: {', '.join(missing_cols)}"
                )
            
            # Переименовываем столбцы
            df = df.rename(columns=column_mapping)
        
        # Очищаем и валидируем данные
        processed_products = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Пропускаем пустые строки
                if pd.isna(row.get('name')) or str(row.get('name')).strip() == '':
                    continue
                
                # Базовые данные
                product_data = {
                    'name': str(row['name']).strip(),
                    'description': str(row.get('description', '')).strip(),
                    'category': 'general'  # По умолчанию
                }
                
                # Цены
                try:
                    product_data['price_uzs'] = float(row.get('price_uzs', 0))
                except (ValueError, TypeError):
                    product_data['price_uzs'] = 0
                
                try:
                    product_data['price_usd'] = float(row.get('price_usd', 0))
                except (ValueError, TypeError):
                    product_data['price_usd'] = 0
                
                try:
                    product_data['usd_rate'] = float(row.get('usd_rate', 11000))
                except (ValueError, TypeError):
                    product_data['usd_rate'] = 11000
                
                # Если нет цены в долларах, рассчитываем
                if product_data['price_usd'] == 0 and product_data['price_uzs'] > 0:
                    product_data['price_usd'] = product_data['price_uzs'] / product_data['usd_rate']
                
                # Если нет цены в сумах, рассчитываем
                if product_data['price_uzs'] == 0 and product_data['price_usd'] > 0:
                    product_data['price_uzs'] = product_data['price_usd'] * product_data['usd_rate']
                
                # Автоматическое определение категории по названию
                name_lower = product_data['name'].lower()
                if any(word in name_lower for word in ['ip', 'сетевая', 'network']):
                    product_data['category'] = 'ip_cameras'
                elif any(word in name_lower for word in ['ahd', 'hdcvi', 'аналог', 'analog']):
                    product_data['category'] = 'analog'
                elif any(word in name_lower for word in ['dvr', 'nvr', 'регистратор', 'recorder']):
                    product_data['category'] = 'dvr'
                elif any(word in name_lower for word in ['блок', 'кабель', 'крепление', 'диск', 'коммутатор', 'hdd']):
                    product_data['category'] = 'accessories'
                elif 'камера' in name_lower:
                    # Если просто "камера" без уточнения, считаем аналоговой
                    product_data['category'] = 'analog'
                
                # Проверяем минимальные требования
                if product_data['price_uzs'] <= 0 and product_data['price_usd'] <= 0:
                    errors.append(f"Строка {index + 2}: Не указана цена товара")
                    continue
                
                if len(product_data['name']) < 3:
                    errors.append(f"Строка {index + 2}: Слишком короткое название товара")
                    continue
                
                processed_products.append(product_data)
                
            except Exception as e:
                errors.append(f"Строка {index + 2}: {str(e)}")
        
        if not processed_products:
            raise HTTPException(
                status_code=400,
                detail="Не найдено валидных товаров для импорта"
            )
        
        # Сохраняем товары в базу
        product_service = ProductService()
        created_count = 0
        updated_count = 0
        
        for product_data in processed_products:
            try:
                # Проверяем, есть ли уже товар с таким названием
                existing_products = await product_service.search_products(product_data['name'], limit=1)
                
                if existing_products and existing_products[0].name.lower() == product_data['name'].lower():
                    # Обновляем существующий товар
                    from ...models.product import ProductUpdate
                    product_update = ProductUpdate(**{
                        k: v for k, v in product_data.items() 
                        if k != 'name'  # Название не обновляем
                    })
                    await product_service.update_product(existing_products[0].id, product_update)
                    updated_count += 1
                else:
                    # Создаем новый товар
                    product_create = ProductCreate(**product_data)
                    await product_service.create_product(product_create)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Ошибка сохранения товара '{product_data['name']}': {str(e)}")
        
        return {
            "success": True,
            "message": f"Прайс-лист обработан успешно",
            "stats": {
                "total_rows": len(df),
                "processed": len(processed_products),
                "created": created_count,
                "updated": updated_count,
                "errors_count": len(errors)
            },
            "errors": errors[:20] if errors else []  # Показываем до 20 ошибок
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Файл пуст или поврежден")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Ошибка парсинга файла. Проверьте формат данных")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


@router.post("/upload/images")
async def upload_product_images(
    files: List[UploadFile] = File(...),
    admin: str = Depends(verify_admin_token)
):
    """Загрузить изображения товаров"""
    
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="Файлы не выбраны")
    
    # Проверяем количество файлов
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Максимум 50 файлов за раз")
    
    uploaded_files = []
    errors = []
    
    # Создаем директорию для изображений
    upload_dir = os.path.join(settings.UPLOAD_DIR, "images")
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        try:
            # Проверяем тип файла
            if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                errors.append(f"{file.filename}: Неподдерживаемый формат изображения")
                continue
            
            # Проверяем размер файла
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                errors.append(f"{file.filename}: Файл слишком большой (макс. {settings.MAX_FILE_SIZE // (1024*1024)}МБ)")
                continue
            
            # Генерируем уникальное имя файла
            import uuid
            from pathlib import Path
            
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Сохраняем файл
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            uploaded_files.append({
                "original_name": file.filename,
                "filename": unique_filename,
                "url": f"/admin/api/upload/images/{unique_filename}",
                "size": len(content)
            })
            
        except Exception as e:
            errors.append(f"{file.filename}: Ошибка загрузки - {str(e)}")
    
    return {
        "success": True,
        "message": f"Загружено {len(uploaded_files)} файлов",
        "uploaded_files": uploaded_files,
        "errors": errors
    }


@router.get("/upload/images/{filename}")
async def get_product_image(filename: str):
    """Получить изображение товара"""
    from fastapi.responses import FileResponse
    
    image_path = os.path.join(settings.UPLOAD_DIR, "images", filename)
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    return FileResponse(image_path)


@router.get("/upload/download/{filename}")
async def download_file(filename: str, admin: str = Depends(verify_admin_token)):
    """Скачать файл"""
    from fastapi.responses import FileResponse
    
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        file_path,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )