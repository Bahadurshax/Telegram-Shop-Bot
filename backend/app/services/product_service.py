"""
Сервис для работы с товарами
"""
from typing import List, Optional

from ..models.product import Product, ProductCreate, ProductUpdate
from ..repositories.product_repo import ProductRepository


class ProductService:
    """Сервис товаров"""
    def __init__(self):
        self.collection = ProductRepository()
    

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Создать товар"""
        return await self.collection.create_product(product_data)
    

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Получить товар по ID"""
        return await self.collection.get_product(product_id)
    

    async def get_products(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Product]:
        """Получить список товаров"""
        return await self.collection.get_products(
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
    

    async def count_products(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Подсчитать количество товаров"""
        return await self.collection.count_products(
            category=category,
            is_active=is_active
        )
    

    async def update_product(
        self, 
        product_id: str, 
        update_data: ProductUpdate
    ) -> bool:
        """Обновить товар"""
        return await self.collection.update_product(product_id, update_data)
    

    async def delete_product(self, product_id: str) -> bool:
        """Удалить товар (архивировать)"""
        return await self.collection.delete_product(product_id)
    

    async def get_categories(self) -> List[str]:
        """Получить список категорий"""
        return await self.collection.get_categories()
    

    async def search_products(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """Поиск товаров"""
        return await self.collection.search_products(query, skip, limit, is_active)

    async def create_products_bulk(self, products_data: List[ProductCreate]) -> List[Product]:
        """Массовое создание товаров"""
        return await self.collection.create_products_bulk(products_data)