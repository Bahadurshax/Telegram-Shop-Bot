from aiogram.fsm.state import State, StatesGroup


class ConsultantStates(StatesGroup):
    """Состояния консультанта (анкета из 8 вопросов)"""
    waiting_location = State()
    waiting_purpose = State()
    waiting_cameras_count = State()
    waiting_placement = State()
    waiting_distance = State()
    waiting_retention = State()
    waiting_remote = State()
    waiting_budget = State()
    processing = State()


class OrderStates(StatesGroup):
    """Состояния оформления заказа"""
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    confirmation = State()