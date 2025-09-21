"""
Обработчики каталога товаров
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.media_group import MediaGroupBuilder
from math import ceil

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from ..keyboards.inline import (
    get_catalog_keyboard, 
    get_product_keyboard, 
    get_pagination_keyboard,
    get_main_menu_keyboard
)
from ..utils.messages import (
    CATALOG_MESSAGE, 
    CATALOG_EMPTY, 
    PRODUCT_TEMPLATE
)
from ...services.product_service import ProductService
from ...services.user_service import UserService

router = Router()

# Константы для пагинации
PRODUCTS_PER_PAGE = 5


@router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery): # CallbackQuery - объект, который содержит информацию о нажатой кнопке
    """Показать каталог товаров"""
    product_service = ProductService()
    
    # Проверяем наличие товаров
    total_products = await product_service.count_products()
    
    if total_products == 0:
        await callback.message.edit_text(
            CATALOG_EMPTY,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Показываем каталог с категориями
    # callback.message - message with the callback button that originated the callback query
    await callback.message.edit_text(
        CATALOG_MESSAGE,
        reply_markup=get_catalog_keyboard(has_products=True)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Показать товары категории"""
    category = callback.data.split("category_")[1]
    # category is one of the following: ip_cameras, analog, dvr, accessories, all
    await show_products_page(callback, category, 1)


@router.callback_query(F.data.startswith("products_"))
async def show_products_pagination(callback: CallbackQuery):
    """Пагинация товаров"""
    print('Pagination callback:', callback.data)
    parts = callback.data.split("_")
    category = parts[1] if len(parts) > 3 else "all"
    if "ip" in parts:
      category = "ip_cameras"
    page = int(parts[-1])
    print('Category:', category, 'Page:', page)
    
    await show_products_page(callback, category, page)


async def show_products_page(callback: CallbackQuery, category: str, page: int):
    """Показать страницу товаров"""
    product_service = ProductService()
    
    # Вычисляем параметры пагинации
    skip = (page - 1) * PRODUCTS_PER_PAGE
    
    # Получаем товары и общее количество
    products = await product_service.get_products(
        category=category if category != "all" else None,
        skip=skip,
        limit=PRODUCTS_PER_PAGE # 5
    )
    
    total_products = await product_service.count_products(
        category=category if category != "all" else None
    )
    
    if not products:
        await callback.message.edit_text(
            CATALOG_EMPTY,
            reply_markup=get_catalog_keyboard(has_products=False)
        )
        await callback.answer()
        return
    
    # Формируем сообщение со списком товаров
    category_names = {
        "all": "Все товары",
        "ip_cameras": "IP камеры",
        "analog": "Аналоговые камеры",
        "dvr": "Регистраторы",
        "accessories": "Аксессуары"
    }
    
    category_name = category_names.get(category, "Товары")
    
    text = f"🛍 <b>{category_name}</b>\n\n"
    
    for i, product in enumerate(products, 1):
        item_num = skip + i
        text += f"<b>{item_num}.</b> {product.name}\n"
        text += f"💰 {product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)\n"
        text += f"<code>/product_{product.id}</code>\n\n"
    
    # Клавиатура с пагинацией
    # считаем количество страниц
    total_pages = ceil(total_products / PRODUCTS_PER_PAGE)
    print("total pages ", total_pages)
    
    keyboard_builder = []
    
    # Добавляем кнопки товаров
    for product in products:
        keyboard_builder.append([
            {
                "text": f"👁 {product.name[:30]}...",
                "callback_data": f"product_{product.id}"
            }
        ])
    
    # Пагинация
    if total_pages > 1: # если страниц больше одной, добавляем кнопки пагинации
        pagination_buttons = []
        
        if page > 1: # если это не первая страница, добавляем кнопку "назад"
            pagination_buttons.append({
                "text": "◀️",
                "callback_data": f"products_{category}_page_{page - 1}" # переход на предыдущую страницу (page - 1)
            })
        # если это первая страница, кнопка "назад" не нужна
        # добавляем кнопку с номером текущей страницы
        pagination_buttons.append({
            "text": f"{page}/{total_pages}", # отображаем текущую страницу и общее количество страниц
            "callback_data": "current_page"
        })
        # если это не последняя страница, добавляем кнопку "вперед"
        # переход на следующую страницу (page + 1)
        if page < total_pages:
            pagination_buttons.append({
                "text": "▶️",
                "callback_data": f"products_{category}_page_{page + 1}"
            })
        
        keyboard_builder.append(pagination_buttons)
    
    # Кнопки навигации
    keyboard_builder.append([
        {"text": "◀️ Каталог", "callback_data": "catalog"},
        {"text": "🏠 Меню", "callback_data": "main_menu"}
    ])
    
    # Создаем клавиатуру
    
    keyboard = InlineKeyboardBuilder()
    
    for row in keyboard_builder:
        if len(row) == 1:
            keyboard.row(
                InlineKeyboardButton(
                    text=row[0]["text"],
                    callback_data=row[0]["callback_data"]
                )
            )
        else:
            buttons = [
                InlineKeyboardButton(
                    text=btn["text"],
                    callback_data=btn["callback_data"]
                ) for btn in row
            ]
            keyboard.row(*buttons)
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    """Показать детали товара"""
    product_id = callback.data.split("product_")[1]
    
    product_service = ProductService()
    user_service = UserService()
    
    # Получаем товар
    product = await product_service.get_product(product_id)
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Проверяем, есть ли товар в корзине
    user = await user_service.get_user(callback.from_user.id)
    in_cart = False
    if user:
        in_cart = any(item.product_id == product_id for item in user.cart)
    
    # Формируем текст
    text = PRODUCT_TEMPLATE.format(
        name=product.name,
        description=product.description,
        price_uzs=product.price_uzs,
        price_usd=product.price_usd,
        usd_rate=product.usd_rate
    )
    
    # Если есть изображение, отправляем с фото
    if product.image_id:
        try:
            # TODO: Реализовать отправку изображения из GridFS
            await callback.message.edit_text(
                text,
                reply_markup=get_product_keyboard(product_id, in_cart)
            )
        except Exception:
            await callback.message.edit_text(
                text,
                reply_markup=get_product_keyboard(product_id, in_cart)
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_product_keyboard(product_id, in_cart)
        )
    
    await callback.answer()



def register_catalog_handlers(dp):
    """Регистрация обработчиков каталога"""
    dp.include_router(router)