"""
Рендеринг результата AI-консультации в сообщение Telegram.

Используется и обработчиком бота, и API мини-аппа (дублирование результата
в чат), чтобы клиент видел одинаковый отчёт из обеих точек входа.
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_result_message(recommendations: dict) -> tuple[str, InlineKeyboardMarkup]:
    """Собрать текст результата консультации и клавиатуру под него"""

    parts = ["🤖 <b>Ваше решение по видеонаблюдению</b>\n"]

    summary = recommendations.get("consultation_summary")
    if summary:
        parts.append(f"<b>📋 Ваши ответы:</b>\n{summary}\n")

    explanation = recommendations.get("explanation")
    if explanation:
        parts.append(f"💡 {explanation}\n")

    zones = recommendations.get("zones") or []
    if zones:
        zone_lines = []
        for zone in zones:
            zone_lines.append(
                f"• <b>{zone.get('zone', '')}</b> — {zone.get('spec', '')} × {zone.get('count', 1)}\n"
                f"  <i>{zone.get('reason', '')}</i>"
            )
        parts.append("<b>🗺 Карта решения:</b>\n" + "\n".join(zone_lines) + "\n")

    equipment = recommendations.get("equipment") or []
    if equipment:
        eq_lines = [
            f"• <b>{eq.get('item', '')}</b> — {eq.get('spec', '')}"
            for eq in equipment
        ]
        parts.append("<b>🔧 Оборудование:</b>\n" + "\n".join(eq_lines) + "\n")

    storage = recommendations.get("storage") or {}
    if storage.get("summary"):
        parts.append(f"<b>💾 Архив:</b> {storage['summary']}\n")

    items = recommendations.get("items") or []
    if items:
        product_lines = []
        for i, item in enumerate(items, 1):
            product = item["product"]
            quantity = item.get("quantity", 1)
            qty_text = f" × {quantity}" if quantity > 1 else ""
            product_lines.append(
                f"{i}. {product.name}{qty_text}\n"
                f"   💰 {product.price_uzs:,.0f} сум ({product.price_usd:.0f} $)"
            )
            reason = item.get("reason")
            if reason:
                product_lines.append(f"   <i>{reason}</i>")
        parts.append("<b>🛍 Товары из каталога:</b>\n" + "\n".join(product_lines) + "\n")

    unmatched = recommendations.get("unmatched") or []
    if unmatched:
        parts.append(
            "<b>⚠️ Нет точного соответствия в каталоге:</b>\n"
            + "\n".join(f"• {u}" for u in unmatched)
            + "\nПо этим позициям поможет менеджер.\n"
        )

    total_uzs = recommendations.get("total_uzs", 0)
    total_usd = recommendations.get("total_usd", 0)
    if items:
        parts.append(f"💰 <b>Итого:</b> {total_uzs:,.0f} сум ({total_usd:.0f} $)")

    keyboard = InlineKeyboardBuilder()
    for item in items:
        product = item["product"]
        keyboard.row(
            InlineKeyboardButton(
                text=f"➕ {product.name[:28]}",
                callback_data=f"add_to_cart_{product.id}",
            )
        )

    if unmatched or not items:
        keyboard.row(
            InlineKeyboardButton(text="📞 Запросить подбор у менеджера", callback_data="consult_manager")
        )

    keyboard.row(
        InlineKeyboardButton(text="🛒 Корзина", callback_data="cart"),
        InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🏠 Меню", callback_data="main_menu"),
    )

    return "\n".join(parts), keyboard.as_markup()
