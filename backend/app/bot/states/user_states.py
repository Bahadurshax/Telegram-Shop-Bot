from aiogram.fsm.state import State, StatesGroup


class ConsultantStates(StatesGroup):
    """Состояния консультанта"""
    waiting_location = State()
    waiting_cameras_count = State()
    waiting_audio = State()
    waiting_distance = State()
    waiting_budget = State()
    processing = State()


class OrderStates(StatesGroup):
    """Состояния оформления заказа"""
    waiting_name = State()
    waiting_phone = State()
    waiting_address = State()
    confirmation = State()