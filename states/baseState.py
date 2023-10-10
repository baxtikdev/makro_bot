from aiogram.dispatcher.filters.state import State, StatesGroup


class BaseState(StatesGroup):
    language = State()
    menu = State()
    professions = State()
    regions = State()
    vacancies = State()
    apply = State()


class Anketa(StatesGroup):
    file = State()
    fullname = State()
    phone = State()
