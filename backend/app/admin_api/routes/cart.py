"""
Public API корзины для Telegram Mini App.

Корзина хранится в документе пользователя MongoDB, поэтому товары,
добавленные из мини-аппа, сразу видны в боте (и наоборот).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..telegram_auth import verify_telegram_user
from ...services.user_service import UserService
from ...services.product_service import ProductService

router = APIRouter()


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, gt=0, le=50)


@router.get("/cart")
async def get_cart(tg_user: dict = Depends(verify_telegram_user)):
    """Получить корзину пользователя с данными товаров"""
    user_service = UserService()
    product_service = ProductService()

    user = await user_service.get_user(tg_user["id"])
    if not user:
        return {"items": [], "total_uzs": 0, "total_usd": 0}

    items = []
    total_uzs = 0.0
    total_usd = 0.0

    for cart_item in user.cart:
        product = await product_service.get_product(cart_item.product_id)
        if not product or not product.is_active:
            continue
        items.append({
            "product": product.model_dump(),
            "quantity": cart_item.quantity,
        })
        total_uzs += product.price_uzs * cart_item.quantity
        total_usd += product.price_usd * cart_item.quantity

    return {"items": items, "total_uzs": total_uzs, "total_usd": total_usd}


@router.post("/cart/items")
async def add_cart_item(
    payload: CartItemRequest,
    tg_user: dict = Depends(verify_telegram_user),
):
    """Добавить товар в корзину"""
    user_service = UserService()
    product_service = ProductService()

    product = await product_service.get_product(payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Пользователь мог открыть мини-апп до первого /start в боте
    await user_service.create_or_update_user(
        telegram_user_id=tg_user["id"],
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
    )

    added = await user_service.add_to_cart(
        tg_user["id"], payload.product_id, payload.quantity
    )
    if not added:
        raise HTTPException(status_code=400, detail="Не удалось добавить товар (корзина переполнена?)")

    return {"ok": True}
