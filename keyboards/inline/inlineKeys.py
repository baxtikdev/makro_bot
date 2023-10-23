import requests
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.config import env
from translations.translation import MENU, URL, LOCATION, BACK, BackToMainButton, APPLY, APPROVE, CANCEL, REGIONS

language = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbek tili", callback_data="uz")],
        [InlineKeyboardButton(text='🇷🇺 Русский язык', callback_data='ru')]
    ]
)


def backInline(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.insert(InlineKeyboardButton(text=f"◀️ {BACK.get(lang)}", callback_data='back'))
    return keyboard


def mainMenu(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(InlineKeyboardButton(text=f"ℹ️ {MENU.get(lang)[0]}", callback_data='info'))
    keyboard.insert(InlineKeyboardButton(text=f"🧰 {MENU.get(lang)[1]}", callback_data='professions'))
    keyboard.insert(InlineKeyboardButton(text=f"📍 {MENU.get(lang)[2]}", callback_data="address"))
    keyboard.insert(InlineKeyboardButton(text=f"📞 {MENU.get(lang)[3]}", callback_data='connect'))
    keyboard.add(InlineKeyboardButton(text=f"🌐 {MENU.get(lang)[4]}", callback_data='change_language'))
    return keyboard


def officeLocation(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.insert(InlineKeyboardButton(text=f"📍 {LOCATION.get(lang)}", url=URL))
    keyboard.insert(InlineKeyboardButton(text=f"◀️ {BACK.get(lang)}", callback_data='back'))
    return keyboard


def backToMain(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.insert(InlineKeyboardButton(text=f"◀️ {BackToMainButton.get(lang)}", callback_data="MAIN"))
    return keyboard


def getVacancies(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(InlineKeyboardButton(text=f"📍 {LOCATION.get(lang)}", url=URL))
    return keyboard


def professions(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    BASE_URL = env.str("BASE_URL")
    data = requests.get(url=BASE_URL + "/api/profession-list/", headers={"Accept-Language": lang})
    for p in data.json():
        if p.get('title') in ['Ofis', 'Офис']:
            keyboard.insert(InlineKeyboardButton(text=p.get('title'), callback_data='ofice'))
            continue
        keyboard.insert(InlineKeyboardButton(text=p.get('title'), callback_data=p.get('id')))
    keyboard.add(InlineKeyboardButton(text=f"◀️ {BACK.get(lang)}", callback_data="back"))
    return keyboard


def backBtn(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text=f"◀️ {BACK.get(lang)}", callback_data="back"))
    return keyboard


def regions(lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    # BASE_URL = env.str("BASE_URL")
    # data = requests.get(url=BASE_URL + "/api/region-list/", headers={"Accept-Language": lang})
    # for r in data.json():
    #     keyboard.insert(InlineKeyboardButton(text=r.get('title'), callback_data=f"{prof_id}_{r.get('id')}"))
    for r in REGIONS.get(lang):
        keyboard.insert(InlineKeyboardButton(text=r, callback_data=r))
    keyboard.add(InlineKeyboardButton(text=f"◀️ {BACK.get(lang)}", callback_data="back"))
    return keyboard


def vacancy(vacancy, lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if vacancy == 'ofice':
        tr = 'Ofis' if language == 'uz' else 'Офис'
    else:
        tr = vacancy.get('profession').get('title')
    for j, i in enumerate(APPLY.get(lang)):
        keyboard.insert(InlineKeyboardButton(text=i,
                                             callback_data=f"{tr}_{j}"))
    keyboard.add(InlineKeyboardButton(text=f"◀️ {BackToMainButton.get(lang)}", callback_data="MAIN"))
    return keyboard


def requestBtn(id, lang='uz'):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text=f"✅ {APPROVE.get(lang)}", callback_data=f"approve_{id}"))
    keyboard.add(InlineKeyboardButton(text=f"❌ {CANCEL.get(lang)}", callback_data=f"cancel_{id}"))
    return keyboard
