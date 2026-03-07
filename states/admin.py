from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    waiting_slot_time = State()
