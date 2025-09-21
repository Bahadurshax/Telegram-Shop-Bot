"""
API дашборда админ-панели
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from ..auth import verify_admin_token
from ...services.product_service import ProductService
from ...services.order_service import OrderService
from ...database import get_users_collection

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(admin: str = Depends(verify_admin_token)):
    """Получить статистику для дашборда"""
    
    product_service = ProductService()
    order_service = OrderService()
    users_collection = get_users_collection()
    
    # Статистика товаров
    total_products = await product_service.count_products()
    active_products = await product_service.count_products(is_active=True)
    
    # Статистика по категориям
    categories_stats = {}
    categories = ["ip_cameras", "analog", "dvr", "accessories"]
    for category in categories:
        count = await product_service.count_products(category=category)
        categories_stats[category] = count
    
    # Статистика заказов
    total_orders = await order_service.count_orders()
    new_orders = await order_service.count_orders(status="new")
    processing_orders = await order_service.count_orders(status="processing")
    completed_orders = await order_service.count_orders(status="completed")
    
    # Статистика пользователей
    total_users = await users_collection.count_documents({})
    
    # Заказы за последнюю неделю
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = await order_service.get_all_orders(limit=10)
    
    # Заказы за неделю
    week_orders_count = len([
        order for order in recent_orders 
        if order.created_at >= week_ago
    ])
    
    return {
        "products": {
            "total": total_products,
            "active": active_products,
            "inactive": total_products - active_products,
            "by_category": categories_stats
        },
        "orders": {
            "total": total_orders,
            "new": new_orders,
            "processing": processing_orders,
            "completed": completed_orders,
            "cancelled": total_orders - new_orders - processing_orders - completed_orders,
            "this_week": week_orders_count
        },
        "users": {
            "total": total_users
        },
        "recent_orders": [
            {
                "id": order.id,
                "user_name": order.user_name,
                "total_uzs": order.total_amount_uzs,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "items_count": len(order.items)
            }
            for order in recent_orders[:5]
        ]
    }