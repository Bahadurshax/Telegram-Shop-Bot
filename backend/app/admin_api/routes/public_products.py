"""
Public API для получения товаров без авторизации
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from ...services.product_service import ProductService
from ...models.product import Product

router = APIRouter()


@router.get("/products", response_model=List[Product])
async def get_public_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Получить список активных товаров (публичный доступ)"""

    product_service = ProductService()

    if search:
        products = await product_service.search_products(search, skip=skip, limit=limit)
        # Фильтруем только активные товары
        products = [p for p in products if p.is_active]
    else:
        # Получаем только активные товары
        products = await product_service.get_products(
            category=category,
            is_active=True,
            skip=skip,
            limit=limit
        )

    return products


@router.get("/products/count")
async def get_public_products_count(
    category: Optional[str] = Query(None)
):
    """Получить количество активных товаров (публичный доступ)"""

    product_service = ProductService()

    count = await product_service.count_products(
        category=category,
        is_active=True
    )

    return {"count": count}


@router.get("/products/{product_id}", response_model=Product)
async def get_public_product(product_id: str):
    """Получить активный товар по ID (публичный доступ)"""

    product_service = ProductService()
    product = await product_service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if not product.is_active:
        raise HTTPException(status_code=404, detail="Товар недоступен")

    return product


@router.get("/categories")
async def get_public_categories():
    """Получить список категорий с активными товарами (публичный доступ)"""

    product_service = ProductService()
    categories = await product_service.get_categories()

    return {"categories": categories}