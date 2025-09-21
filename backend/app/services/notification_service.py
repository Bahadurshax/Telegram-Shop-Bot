"""
Сервис уведомлений админу
"""
from aiogram import Bot

from ..config import settings
from ..models.order import Order


class NotificationService:
    """Сервис уведомлений"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def notify_new_order(self, order: Order) -> bool:
        """Уведомить админа о новом заказе"""
        if not settings.ADMIN_TELEGRAM_ID:
            return False
        
        try:
            # Формируем сообщение о заказе
            message = self._format_order_notification(order)
            
            # Отправляем админу
            await self.bot.send_message(
                chat_id=settings.ADMIN_TELEGRAM_ID,
                text=message,
                parse_mode="HTML"
            )
            
            return True
            
        except Exception as e:
            print(f"Ошибка отправки уведомления админу: {e}")
            return False
    
    def _format_order_notification(self, order: Order) -> str:
        """Форматирование уведомления о заказе"""
        
        # Товары
        items_text = ""
        for i, item in enumerate(order.items, 1):
            items_text += f"{i}. {item.product_name}\n"
            items_text += f"   Количество: {item.quantity} шт.\n"
            items_text += f"   Цена: {item.price_uzs:,.0f} сум × {item.quantity} = {item.price_uzs * item.quantity:,.0f} сум\n\n"
        
        # Основное сообщение
        message = f"""
🔔 <b>НОВЫЙ ЗАКАЗ #{order.id[:8]}</b>

👤 <b>Клиент:</b>
Имя: {order.user_name}
Телефон: {order.user_phone}
Адрес: {order.user_address or 'Не указан'}

🛒 <b>Заказанные товары:</b>
{items_text}

💰 <b>Итого:</b> {order.total_amount_uzs:,.0f} сум ({order.total_amount_usd:.0f} $)

📅 <b>Дата заказа:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}
"""
        
        # Добавляем отчет консультации если есть
        if order.consultation_report:
            message += f"\n🤖 <b>Отчет консультации:</b>\n{order.consultation_report[:200]}..."
        
        return message
