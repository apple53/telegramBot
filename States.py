from aiogram.dispatcher.filters.state import State, StatesGroup


class Reg(StatesGroup):
    nickname = State()


class Add_friends(StatesGroup):
    nickname = State()

