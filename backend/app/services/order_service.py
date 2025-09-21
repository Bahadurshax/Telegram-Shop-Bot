"""
Сервис для работы с заказами
"""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import get_orders_collection
from ..models.order import Order, OrderItem, OrderStatus
from ..models.user import User
from ..services.product_service import ProductService
from ..services.user_service import UserService


class OrderService:
    """Сервис заказов"""
    
    def __init__(self):
        self.product_service = ProductService()
        self.user_service = UserService()
    
    async def create_order_from_cart(
        self,
        telegram_user_id: int,
        user_name: str,
        user_phone: str,
        user_address: Optional[str] = None,
        consultation_report: Optional[str] = None
    ) -> Optional[Order]:
        """Создать заказ из корзины пользователя"""
        
        # Получаем пользователя
        user = await self.user_service.get_user(telegram_user_id)
        if not user or not user.cart:
            return None
        
        # Формируем товары заказа
        order_items = []
        total_uzs = 0
        total_usd = 0

        # cart_item: {product_id: str, quantity: int}
        
        for cart_item in user.cart: # проходимся по товарам в корзине пользователя
            # Получаем актуальную информацию о товаре
            product = await self.product_service.get_product(cart_item.product_id)
            if not product or not product.is_active:
                continue  # Пропускаем неактивные товары
            
            # Создаем позицию заказа
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                price_uzs=product.price_uzs,
                price_usd=product.price_usd
            )
            
            order_items.append(order_item)
            total_uzs += product.price_uzs * cart_item.quantity
            total_usd += product.price_usd * cart_item.quantity
        
        if not order_items:
            return None
        
        # Создаем заказ
        collection = get_orders_collection()
        
        order_data = {
            "telegram_user_id": telegram_user_id,
            "user_name": user_name,
            "user_phone": user_phone,
            "user_address": user_address,
            "items": [item.model_dump() for item in order_items],
            "total_amount_uzs": total_uzs,
            "total_amount_usd": total_usd,
            "consultation_report": consultation_report,
            "status": OrderStatus.NEW,
            "created_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(order_data)
        order_data["_id"] = str(result.inserted_id)
        
        # Очищаем корзину пользователя
        await self.user_service.clear_cart(telegram_user_id)
        
        return Order(**order_data)
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Получить заказ по ID"""
        collection = get_orders_collection()
        
        try:
            order_data = await collection.find_one({"_id": ObjectId(order_id)})
            if order_data:
                order_data["_id"] = str(order_data["_id"])
                return Order(**order_data)
        except Exception as e:
            print("Ошибка при получении заказа: ", e)
            pass
        
        return None
    
    async def get_user_orders(
        self,
        telegram_user_id: int,
        limit: int = 10
    ) -> List[Order]:
        """Получить заказы пользователя"""
        collection = get_orders_collection()
        
        cursor = collection.find(
            {"telegram_user_id": telegram_user_id}
        ).sort("created_at", -1).limit(limit)
        
        orders = []
        async for order_data in cursor:
            order_data["_id"] = str(order_data["_id"])
            orders.append(Order(**order_data))
        
        return orders
    
    async def get_all_orders(
        self,
        status: Optional[OrderStatus] = None,
        limit: int = 50
    ) -> List[Order]:
        """Получить все заказы для админа"""
        collection = get_orders_collection()
        
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        cursor = collection.find(filter_dict).sort("created_at", -1).limit(limit)
        
        orders = []
        async for order_data in cursor:
            order_data["_id"] = str(order_data["_id"])
            orders.append(Order(**order_data))
        
        return orders
    
    async def update_order_status(
        self,
        order_id: str,
        status: OrderStatus
    ) -> bool:
        """Обновить статус заказа"""
        collection = get_orders_collection()
        
        try:
            result = await collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def count_orders(self, status: Optional[OrderStatus] = None) -> int:
        """Подсчитать количество заказов"""
        collection = get_orders_collection()
        
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        return await collection.count_documents(filter_dict)

