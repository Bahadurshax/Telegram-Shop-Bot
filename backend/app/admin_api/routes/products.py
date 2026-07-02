"""
API для управления товарами
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from ..auth import verify_admin_token
from ...config import settings
from ...services.image_service import image_service
from ...services.product_service import ProductService
from ...models.product import Product, ProductCreate, ProductUpdate

router = APIRouter()


@router.get("/products", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin: str = Depends(verify_admin_token)
):
    """Получить список товаров"""
    
    product_service = ProductService()
    
    if search:
        products = await product_service.search_products(search, skip=skip, limit=limit, is_active=is_active)
    else:
        products = await product_service.get_products(
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
    
    return products


@router.get("/products/count")
async def get_products_count(
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    admin: str = Depends(verify_admin_token)
):
    """Получить количество товаров"""
    
    product_service = ProductService()
    
    count = await product_service.count_products(
        category=category,
        is_active=is_active
    )
    
    return {"count": count}


@router.post("/products/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
    admin: str = Depends(verify_admin_token)
):
    """Загрузить изображение товара в Supabase Storage, вернуть публичный URL"""

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Поддерживаются только изображения")

    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой (макс. {settings.MAX_FILE_SIZE // (1024*1024)}МБ)"
        )

    image_url = image_service.upload_image(content, file.filename or "image.png", folder="products")
    if not image_url:
        raise HTTPException(status_code=500, detail="Не удалось загрузить изображение")

    return {"image_url": image_url}


@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    admin: str = Depends(verify_admin_token)
):
    """Получить товар по ID"""
    
    product_service = ProductService()
    product = await product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return product


@router.post("/products", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    admin: str = Depends(verify_admin_token)
):
    """Создать товар"""
    
    product_service = ProductService()
    product = await product_service.create_product(product_data)
    
    return product


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    admin: str = Depends(verify_admin_token)
):
    """Обновить товар"""
    
    product_service = ProductService()
    
    # Проверяем существование товара
    existing_product = await product_service.get_product(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Обновляем
    success = await product_service.update_product(product_id, product_data)
    if not success:
        raise HTTPException(status_code=400, detail="Не удалось обновить товар")
    
    # Возвращаем обновленный товар
    updated_product = await product_service.get_product(product_id)
    return updated_product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    admin: str = Depends(verify_admin_token)
):
    """Удалить товар (архивировать)"""
    
    product_service = ProductService()
    
    success = await product_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    return {"message": "Товар архивирован"}


@router.get("/products/categories/list")
async def get_categories(admin: str = Depends(verify_admin_token)):
    """Получить список категорий"""
    
    product_service = ProductService()
    categories = await product_service.get_categories()
    
    return {"categories": categories}
