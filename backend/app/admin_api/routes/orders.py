"""
API для управления заказами
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import verify_admin_token
from ...services.order_service import OrderService
from ...models.order import Order, OrderStatus

router = APIRouter()


@router.get("/orders", response_model=List[Order])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    admin: str = Depends(verify_admin_token)
):
    """Получить список заказов"""
    
    order_service = OrderService()
    orders = await order_service.get_all_orders(status=status, limit=limit)
    
    # Применяем пагинацию вручную (можно улучшить в ProductService)
    paginated_orders = orders[skip:skip + limit] if skip < len(orders) else []
    
    return paginated_orders


@router.get("/orders/count")
async def get_orders_count(
    status: Optional[OrderStatus] = Query(None),
    admin: str = Depends(verify_admin_token)
):
    """Получить количество заказов"""
    
    order_service = OrderService()
    count = await order_service.count_orders(status=status)
    
    return {"count": count}


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    admin: str = Depends(verify_admin_token)
):
    """Получить заказ по ID"""
    
    order_service = OrderService()
    order = await order_service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    return order


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,
    admin: str = Depends(verify_admin_token)
):
    """Обновить статус заказа"""
    
    new_status = status_data.get("status")
    if new_status not in ["new", "processing", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Неверный статус")
    
    order_service = OrderService()
    
    # Проверяем существование заказа
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Обновляем статус
    success = await order_service.update_order_status(order_id, OrderStatus(new_status))
    if not success:
        raise HTTPException(status_code=400, detail="Не удалось обновить статус")
    
    return {"message": "Статус обновлен", "status": new_status}


@router.get("/orders/stats/summary")
async def get_orders_stats(admin: str = Depends(verify_admin_token)):
    """Получить статистику заказов"""
    
    order_service = OrderService()
    
    total = await order_service.count_orders()
    new = await order_service.count_orders(OrderStatus.NEW)
    processing = await order_service.count_orders(OrderStatus.PROCESSING)
    completed = await order_service.count_orders(OrderStatus.COMPLETED)
    cancelled = await order_service.count_orders(OrderStatus.CANCELLED)
    
    return {
        "total": total,
        "new": new,
        "processing": processing,
        "completed": completed,
        "cancelled": cancelled
    }