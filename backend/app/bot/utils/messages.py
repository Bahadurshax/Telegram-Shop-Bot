"""
Тексты сообщений для бота
"""

# Стартовые сообщения
START_MESSAGE = """
🏪 <b>Добро пожаловать в магазин видеонаблюдения!</b>

Здесь вы можете:
• 🛍 Просмотреть каталог товаров
• 🤖 Получить консультацию по выбору оборудования
• 🛒 Оформить заказ

Выберите действие:
"""

HELP_MESSAGE = """
🆘 <b>Помощь</b>

<b>Доступные команды:</b>
/start - Главное меню
/catalog - Каталог товаров
/consultant - AI консультант
/cart - Моя корзина
/help - Эта справка

<b>Как пользоваться ботом:</b>
1. Просмотрите каталог или воспользуйтесь консультантом
2. Добавьте товары в корзину
3. Оформите заказ с указанием контактов

По вопросам обращайтесь к администратору.
"""

# Каталог
CATALOG_EMPTY = "📦 Каталог пуст. Товары появятся в ближайшее время."

CATALOG_MESSAGE = """
🛍 <b>Каталог товаров</b>

Выберите категорию или просмотрите все товары:
"""

PRODUCT_TEMPLATE = """
📦 <b>{name}</b>

📝 {description}

💰 <b>Цена:</b> {price_uzs:,.0f} сум ({price_usd:.0f} $)

📊 <b>Курс:</b> {usd_rate:,.0f} сум/$
"""

# Консультант
CONSULTANT_START = """
🤖 <b>AI Консультант по видеонаблюдению</b>

Я помогу спроектировать систему под ваши задачи: подберу камеры по зонам,
рассчитаю объём архива и предложу товары из нашего каталога.

Ответьте на 8 коротких вопросов 👇
"""

CONSULTANT_QUESTION_LOCATION = """
📍 <b>Вопрос 1/8</b>

Что за объект нужно оборудовать видеонаблюдением?
"""

CONSULTANT_QUESTION_PURPOSE = """
🎯 <b>Вопрос 2/8</b>

Зачем вам камеры — что именно хотите увидеть или предотвратить?
"""

CONSULTANT_QUESTION_CAMERAS = """
🎥 <b>Вопрос 3/8</b>

Сколько камер вам потребуется?
"""

CONSULTANT_QUESTION_PLACEMENT = """
🏠 <b>Вопрос 4/8</b>

Камеры нужны внутри помещения, на улице, или и там и там?
"""

CONSULTANT_QUESTION_DISTANCE = """
📏 <b>Вопрос 5/8</b>

На какое расстояние должна видеть камера?
"""

CONSULTANT_QUESTION_RETENTION = """
💾 <b>Вопрос 6/8</b>

Сколько времени нужно хранить записи?
"""

CONSULTANT_QUESTION_REMOTE = """
📱 <b>Вопрос 7/8</b>

Нужен ли удалённый просмотр с телефона?
"""

CONSULTANT_QUESTION_BUDGET = """
💰 <b>Вопрос 8/8</b>

Какой бюджет вы планируете на систему видеонаблюдения?
"""

CONSULTANT_PROCESSING = """
🤖 <b>Проектирую решение...</b>

Анализирую ответы, рассчитываю архив и подбираю оборудование.
Это займет до минуты.
"""

CONSULTANT_MANAGER_REQUESTED = """
📞 <b>Заявка передана менеджеру</b>

Мы свяжемся с вами в ближайшее время и подберём оборудование под ваши задачи.
"""

# Корзина
CART_EMPTY = """
🛒 <b>Ваша корзина пуста</b>

Загляните в каталог или воспользуйтесь консультантом для выбора товаров.
"""

CART_TEMPLATE = """
🛒 <b>Ваша корзина</b>

{items}

<b>💰 Итого: {total_uzs:,.0f} сум ({total_usd:.0f} $)</b>
"""

CART_ITEM_TEMPLATE = """
📦 <b>{name}</b>
Количество: {quantity} шт.
Цена: {price_uzs:,.0f} сум × {quantity} = {total_uzs:,.0f} сум
"""

# Заказы
ORDER_CONTACT_NAME = """
👤 <b>Оформление заказа</b>

Укажите ваше имя:
"""

ORDER_CONTACT_PHONE = """
📞 <b>Контактный телефон</b>

Укажите ваш номер телефона для связи:
Можете использовать кнопку ниже для отправки номера.
"""

ORDER_CONTACT_ADDRESS = """
📍 <b>Адрес доставки</b>

Укажите адрес доставки:
(можете пропустить, если самовывоз)
"""

ORDER_CONFIRMATION_TEMPLATE = """
✅ <b>Подтверждение заказа</b>

<b>👤 Контактные данные:</b>
Имя: {name}
Телефон: {phone}
Адрес: {address}

<b>🛒 Заказанные товары:</b>
{items}

<b>💰 Итого к оплате: {total_uzs:,.0f} сум ({total_usd:.0f} $)</b>

Подтверждаете заказ?
"""

ORDER_SUCCESS = """
🎉 <b>Заказ успешно оформлен!</b>

Номер заказа: #{order_id}

С вами свяжутся в ближайшее время для уточнения деталей.

Спасибо за покупку! 🙏
"""

# Ошибки
ERROR_GENERAL = "❌ Произошла ошибка. Попробуйте позже."
ERROR_PRODUCT_NOT_FOUND = "❌ Товар не найден."
ERROR_INVALID_QUANTITY = "❌ Неверное количество товара."
ERROR_CONSULTANT_LIMIT = "❌ Превышен лимит консультаций на сегодня."
ERROR_PHONE_FORMAT = "❌ Неверный формат номера телефона. Попробуйте еще раз."

# Кнопки
BUTTON_CATALOG = "🛍 Каталог"
BUTTON_CONSULTANT = "🤖 Консультант"
BUTTON_CART = "🛒 Корзина"
BUTTON_HELP = "🆘 Помощь"
BUTTON_BACK = "◀️ Назад"
BUTTON_MAIN_MENU = "🏠 Главное меню"

# Консультант - кнопки
BUTTON_HOME = "🏠 Дом / квартира"
BUTTON_OFFICE = "🏢 Офис"
BUTTON_SHOP = "🛒 Магазин"
BUTTON_WAREHOUSE = "🏭 Склад / производство"

BUTTON_YES = "✅ Да"
BUTTON_NO = "❌ Нет"

BUTTON_PURPOSE_THEFT = "🚨 Защита от краж"
BUTTON_PURPOSE_STAFF = "👥 Контроль сотрудников"
BUTTON_PURPOSE_IDENTIFY = "🔍 Лица / номера авто"
BUTTON_PURPOSE_GENERAL = "👁 Общий контроль"

BUTTON_CAMERAS_1_4 = "1-4 камеры"
BUTTON_CAMERAS_5_8 = "5-8 камер"
BUTTON_CAMERAS_9_16 = "9-16 камер"
BUTTON_CAMERAS_MORE = "Более 16 камер"

BUTTON_PLACEMENT_INDOOR = "🏠 Внутри"
BUTTON_PLACEMENT_OUTDOOR = "🌳 На улице"
BUTTON_PLACEMENT_BOTH = "🏠+🌳 И там, и там"

BUTTON_DISTANCE_10M = "До 10 метров"
BUTTON_DISTANCE_30M = "До 30 метров"
BUTTON_DISTANCE_50M = "До 50 метров"
BUTTON_DISTANCE_100M = "Более 50 метров"

BUTTON_RETENTION_7D = "1 неделя"
BUTTON_RETENTION_14D = "2 недели"
BUTTON_RETENTION_30D = "1 месяц"
BUTTON_RETENTION_60D = "2 месяца"

BUTTON_BUDGET_500K = "До 500 тыс сум"
BUTTON_BUDGET_1M = "500 тыс - 1 млн"
BUTTON_BUDGET_2M = "1-2 млн"
BUTTON_BUDGET_MORE = "Более 2 млн"

# Корзина - кнопки
BUTTON_ADD_TO_CART = "➕ В корзину"
BUTTON_REMOVE_FROM_CART = "➖ Убрать"
BUTTON_CLEAR_CART = "🗑 Очистить корзину"
BUTTON_CHECKOUT = "✅ Оформить заказ"

# Заказ - кнопки
BUTTON_SEND_PHONE = "📞 Отправить номер"
BUTTON_SKIP_ADDRESS = "⏭ Пропустить"
BUTTON_CONFIRM_ORDER = "✅ Подтвердить заказ"
BUTTON_CANCEL_ORDER = "❌ Отменить"