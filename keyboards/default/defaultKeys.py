from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from translations.translation import BACK, PASS, PHONE


def backFileButton(lang="uz"):
    back = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'◀️ {BACK.get(lang)}'),
                KeyboardButton(text=f'{PASS.get(lang)} ▶️')
            ],
        ],
        resize_keyboard=True
    )
    return back


def backButton(lang="uz"):
    back = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'◀️ {BACK.get(lang)}'),
            ],
        ],
        resize_keyboard=True
    )
    return back


def phone(lang="uz"):
    phoneNumber = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f'◀️ {BACK.get(lang)}'),
                KeyboardButton(text=f'📞 {PHONE.get(lang)}', request_contact=True),
            ],
        ],
        resize_keyboard=True
    )
    return phoneNumber
