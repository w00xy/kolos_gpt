from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    INITIAL = State()
    CHATGPT = State()
