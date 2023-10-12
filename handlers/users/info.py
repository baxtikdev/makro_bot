import re

import requests
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from data.config import env, ADMINS
from keyboards.default.defaultKeys import backFileButton, backButton, phone
from keyboards.inline.inlineKeys import officeLocation, professions, mainMenu, regions, vacancy, backToMain, backInline
from loader import dp, bot
from states.baseState import BaseState, Anketa
from translations.images import INFO_IMAGE, OFFICE, CONNECT, INTRO_IMAGE
from translations.translation import INFO, ADDRESS, CONTACT, PROFESSION, INTRO, BackToMain, GOTO, FillOutForm, \
    LastMessage, PHONE_FORMAT_ERROR, FULLNAME_FORMAT_ERROR, FORMAT


@dp.callback_query_handler(lambda message: message.data == "info", state=BaseState.menu)
async def get_info(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    await call.message.delete()
    language = data.get('language')
    await call.message.answer_photo(
        photo=INFO_IMAGE,
        caption=INFO.get(language),
        reply_markup=backInline(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.professions.set()


@dp.callback_query_handler(lambda message: message.data == "address", state=BaseState.menu)
async def get_address(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    await call.message.delete()
    language = data.get('language')
    await call.message.answer_photo(
        photo=OFFICE,
        caption=ADDRESS.get(language),
        reply_markup=officeLocation(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.professions.set()


@dp.callback_query_handler(lambda message: message.data == "connect", state=BaseState.menu)
async def get_connect(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    await call.message.delete()
    language = data.get('language')
    await call.message.answer_photo(
        photo=CONNECT,
        caption=CONTACT.get(language),
        reply_markup=backInline(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.professions.set()


@dp.callback_query_handler(lambda message: message.data == "professions", state=BaseState.menu)
async def get_vacancy(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()
    data = await state.get_data()
    language = data.get('language')
    await call.message.answer(
        text=PROFESSION.get(language),
        reply_markup=professions(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.professions.set()


@dp.callback_query_handler(lambda message: message.data != "back", state=BaseState.professions)
async def get_regions(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')
    await call.message.edit_reply_markup(
        reply_markup=regions(call.data, language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.regions.set()


def formated(data, language):
    if language == 'ru':
        return f"<b>Вакансия: </b> <b>{data.get('profession').get('title')}</b>\n❗️ Требования\n{data.get('requirements')}\n\n 📍Обязанности:\n{data.get('responsibility')}\n\n ✅ Условия работы:\n{data.get('offer')}"
    return f"<b>Ish o'rni: </b> <b>{data.get('profession').get('title')}</b>\n❗️ Talablar\n{data.get('requirements')}\n\n 📍Mas'uliyat:\n{data.get('responsibility')}\n\n ✅ Ish sharoitlari:\n{data.get('offer')}"


@dp.callback_query_handler(lambda message: message.data != "back", state=BaseState.regions)
async def get_vacancies(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()

    data = await state.get_data()
    language = data.get('language')

    prof_id = call.data.split('_')[0]
    region_id = call.data.split('_')[1]

    BASE_URL = env.str("BASE_URL")
    data = requests.get(url=BASE_URL + f"/api/vacancy-list/?profession={prof_id}&region={region_id}",
                        headers={"Accept-Language": language})
    if not data.json():
        await call.message.answer(
            text=BackToMain.get(language),
            reply_markup=backToMain(language)
        )
        await BaseState.vacancies.set()
        return
    for v in data.json():
        await call.message.answer(
            text=formated(v, language),
            reply_markup=vacancy(v, language)
        )
    await call.answer(cache_time=0.02)
    await BaseState.vacancies.set()


@dp.callback_query_handler(lambda message: message.data == "back", state=BaseState.professions)
async def back(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()
    data = await state.get_data()
    language = data.get('language')
    await call.message.answer_photo(
        photo=INTRO_IMAGE,
        caption=INTRO.get(language),
        reply_markup=mainMenu(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.menu.set()


@dp.callback_query_handler(lambda message: message.data == "back", state=BaseState.regions)
async def back(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')
    await call.message.edit_reply_markup(
        reply_markup=professions(language)
    )
    await call.answer(cache_time=0.02)
    await BaseState.professions.set()


@dp.callback_query_handler(state=BaseState.vacancies)
async def back(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    await call.answer(cache_time=0.02)
    language = data.get('language')
    if call.data == 'MAIN':
        await call.message.delete()
        await call.message.answer_photo(
            photo=INTRO_IMAGE,
            caption=INTRO.get(language),
            reply_markup=mainMenu(language)
        )
        await BaseState.menu.set()
    elif call.data.split('_')[1] == '1':  # borish
        await call.message.delete()
        await call.message.answer_photo(
            photo=OFFICE,
            caption=GOTO.get(language),
            reply_markup=officeLocation(language)
            # reply_markup=backToMain(language)
        )
        await BaseState.professions.set()
        return
    elif call.data.split('_')[1] == '2':  # rezume yuborish
        pass
    elif call.data.split('_')[1] == '0':  # anketa to'ldirish
        await call.message.answer(
            text=FillOutForm.get('cv').get(language),
            reply_markup=backFileButton(language)
        )
        await Anketa.file.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Anketa.file)
@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Anketa.file)
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Anketa.file)
async def get_file(message: types.Message, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')

    if message.text in ['Oʻtkazib yuborish ▶️', 'Пропускать ▶️']:
        await message.answer(
            text=FillOutForm.get('fullname').get(language),
            reply_markup=backButton(language)
        )
        await Anketa.fullname.set()
        return

    elif message.text in ['◀️ Ortga', '◀️ Назадь']:
        a = await message.answer('.', reply_markup=ReplyKeyboardRemove())
        await a.delete()
        await message.answer_photo(
            photo=INTRO_IMAGE,
            caption=INTRO.get(language),
            reply_markup=mainMenu(language)
        )
        await BaseState.menu.set()
        return
    elif message.text:
        await message.answer(
            text=FORMAT.get(language)
        )
        return

    if message.photo:
        await state.update_data({
            "photo_file_id": message.photo[0].file_id
        })
        await state.update_data({
            "file_id": None
        })
    else:
        await state.update_data({
            "file_id": message.document.file_id
        })
        await state.update_data({
            "photo_file_id": None
        })
    await message.answer(
        text=FillOutForm.get('fullname').get(language),
        reply_markup=backButton(language)
    )
    await Anketa.fullname.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Anketa.fullname)
async def get_fullname(message: types.Message, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')

    if message.text in ['◀️ Ortga', '◀️ Назадь']:
        await message.answer(
            text=FillOutForm.get('cv').get(language),
            reply_markup=backFileButton(language)
        )
        await Anketa.file.set()
        return
    fullname = message.text
    full_name_pattern = r'^[A-Za-zÀ-ÖØ-öø-ÿ\'-]+(?: [A-Za-zÀ-ÖØ-öø-ÿ\'-]+)*$'

    if re.match(full_name_pattern, fullname):
        await state.update_data({
            "fullname": fullname
        })
    else:
        await message.reply(FULLNAME_FORMAT_ERROR.get(language))
        return

    await message.answer(
        text=FillOutForm.get('phone').get(language),
        reply_markup=phone(language)
    )
    await Anketa.phone.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Anketa.phone)
@dp.message_handler(content_types=types.ContentType.TEXT, state=Anketa.phone)
async def get_phone(message: types.Message, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')

    if message.text in ['◀️ Ortga', '◀️ Назадь']:
        await message.answer(
            text=FillOutForm.get('fullname').get(language),
            reply_markup=backButton(language)
        )
        await Anketa.fullname.set()
        return
    if message.contact:
        number = message.contact.phone_number
    else:
        number = message.text
    phone_pattern = r'^\+998\d{2}\d{3}\d{4}$'
    if not re.match(phone_pattern, number):
        await message.reply(PHONE_FORMAT_ERROR.get(language))
        return

    await message.answer(
        text=LastMessage.get(language),
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer_photo(
        photo=INTRO_IMAGE,
        caption=INTRO.get(language),
        reply_markup=mainMenu(language)
    )
    await BaseState.menu.set()

    if data.get('photo_file_id'):
        if language == "uz":
            await bot.send_photo(chat_id=ADMINS[0], photo=data.get('photo_file_id'),
                                 caption=f"👤 Ism: {data.get('fullname')}\n\n📞 Tel: {number}")
        else:
            await bot.send_photo(chat_id=ADMINS[0], photo=data.get('photo_file_id'),
                                 caption=f"👤 Имя: {data.get('fullname')}\n\n📞 Тел.: {number}")

        await state.update_data({
            "photo_file_id": None
        })

    elif data.get('file_id'):
        if language == "uz":
            await bot.send_document(chat_id=ADMINS[0], document=data.get('file_id'),
                                    caption=f"👤 Ism: {data.get('fullname')}\n\n📞 Tel: {number}")
        else:
            await bot.send_document(chat_id=ADMINS[0], document=data.get('file_id'),
                                    caption=f"👤 Имя: {data.get('fullname')}\n\n📞 Тел.: {number}")
        await state.update_data({
            "file_id": None
        })

    else:
        if language == "uz":
            await bot.send_message(chat_id=ADMINS[0], text=f"👤 Ism: {data.get('fullname')}\n\n📞 Tel: {number}")
        else:
            await bot.send_document(chat_id=ADMINS[0], text=f"👤 Имя: {data.get('fullname')}\n\n📞 Тел.: {number}")
