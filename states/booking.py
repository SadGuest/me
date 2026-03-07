from aiogram.fsm.state import State, StatesGroup


class BookingFSM(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_confirm = State()
