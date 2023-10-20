import re

import requests
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from data.config import env, GROUP
from keyboards.default.defaultKeys import backFileButton, backButton, phone
from keyboards.inline.inlineKeys import officeLocation, professions, mainMenu, regions, vacancy, backToMain, backInline, \
    requestBtn
from loader import dp, bot
from states.baseState import BaseState, Anketa
from translations.images import INFO_IMAGE, OFFICE, CONNECT, INTRO_IMAGE
from translations.translation import INFO, ADDRESS, CONTACT, PROFESSION, INTRO, BackToMain, GOTO, FillOutForm, \
    LastMessage, PHONE_FORMAT_ERROR, FULLNAME_FORMAT_ERROR, FORMAT, NAME, TEL, REQUEST, APP_RESPONSE_ACCEPT, \
    APP_RESPONSE_CANCEL


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
    body = ""
    if language == 'ru':
        if data.get('profession').get('title'):
            body += f"<b>Вакансия: </b> <b>{data.get('profession').get('title')}</b>\n"
        if data.get('requirements'):
            body += f"❗️ Требования\n{data.get('requirements')}\n\n"
        if data.get('responsibility'):
            body += f" 📍Обязанности:\n{data.get('responsibility')}\n\n"
        if data.get('offer'):
            body += f" ✅ Условия работы:\n{data.get('offer')}"
        return body

    if data.get('profession').get('title'):
        body += f"<b>Ish o'rni: </b> <b>{data.get('profession').get('title')}</b>\n"
    if data.get('requirements'):
        body += f"❗️ Talablar\n{data.get('requirements')}\n\n"
    if data.get('responsibility'):
        body += f" 📍Mas'uliyat:\n{data.get('responsibility')}\n\n"
    if data.get('offer'):
        body += f" ✅ Ish sharoitlari:\n{data.get('offer')}"
    return body


@dp.callback_query_handler(lambda message: message.data != "back", state=BaseState.regions)
async def get_vacancies(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()

    data = await state.get_data()
    language = data.get('language')

    prof_id = call.data.split('_')[0]
    region_id = call.data.split('_')[1]

    BASE_URL = env.str("BASE_URL")
    data = requests.get(url=BASE_URL + f"/api/vacancy-list/?profession={prof_id}",
                        headers={"Accept-Language": language})
    if not data.json():
        await call.message.answer(
            text=BackToMain.get(language),
            reply_markup=backToMain(language)
        )
        await BaseState.vacancies.set()
        return

    for v in data.json():
        if v.get('profession').get('title') in ['Sotuvchi-kassir', 'Продавец-кассир']:
            photo = 'AgACAgIAAxkBAAIGkWUyqu3tXx2xHtiVPq3ZCkGBTtNXAAJo0TEbxryQSTfyUqB0ScI1AQADAgADcwADMAQ'
        elif v.get('profession').get('title') in ['Yukchi', 'Грузчик']:
            photo = 'AgACAgIAAxkBAAIGkmUyqyHPaTvE69fuVOF3H6Jkbf3cAAJp0TEbxryQSUtbZ4HoT8FQAQADAgADcwADMAQ'
        elif v.get('profession').get('title') in ["Qo'riqchi", "Охранник"]:
            photo = 'AgACAgIAAxkBAAIGk2UyqzTRMTBTkZe_CQHf0_bpXV1TAAJr0TEbxryQSWDm_lLYKQuAAQADAgADcwADMAQ'
        else:  # v.get('profession').get('title') in ['Ofis', 'Офис']:
            photo = 'AgACAgIAAxkBAAIGlGUyq0d9DKh0jmMOAAHNNu5BXjf0wwACbdExG8a8kEkWxcUW4AatHwEAAwIAA3MAAzAE'
        await call.message.answer_photo(
            photo=photo,
            caption=formated(v, language),
            reply_markup=vacancy(v, language)
        )

    await state.update_data({
        "prof": prof_id,
        "region": region_id,
    })
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

    elif message.text in ['◀️ Ortga', '◀️ Назад']:
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
    else:
        await state.update_data({
            "file_id": message.document.file_id
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

    if message.text in ['◀️ Ortga', '◀️ Назад']:
        await message.answer(
            text=FillOutForm.get('cv').get(language),
            reply_markup=backFileButton(language)
        )
        await Anketa.file.set()
        return
    fullname = message.text
    full_name_pattern = r'^[A-Za-zÀ-ÖØ-öø-ÿА-Яа-я\'-]+(?: [A-Za-zÀ-ÖØ-öø-ÿА-Яа-я\'-]+)*$'

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

    if message.text in ['◀️ Ortga', '◀️ Назад']:
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
    number = number.replace(' ', '')
    phone_pattern = r'(\+?998\(\d{2}\)\d{3}-\d{2}-\d{2}|\+?998\(\d{2}\)\d{7}|\+?998\d{5}-\d{2}-\d{2}|\+?998\(\d{2}\)\d{3}-\d{2}-\d{2}|\+?998\(\d{2}\)\d{7}|\+?998\d{5}-\d{2}-\d{2}|\+?998\d{9}|\+?998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2})'
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
    BASE_URL = env.str("BASE_URL")
    url = BASE_URL + "/api/application-create/"
    post_data = {
        "region": data.get("region"),
        "profession": data.get("prof"),
        "user_id": message.from_user.id,
        "fullname": data.get("fullname"),
        "phone": number,
        "language": language,
    }

    response = requests.post(url, data=post_data)
    response_data = response.json()
    id = response_data.get('id')

    if data.get('photo_file_id'):
        await bot.send_photo(chat_id=GROUP, photo=data.get('photo_file_id'),
                             caption=f"👤 {NAME.get(language)}: {data.get('fullname')}\n\n📞 {TEL.get(language)}: {number}",
                             reply_markup=requestBtn(id, language))

    elif data.get('file_id'):
        await bot.send_document(chat_id=GROUP, document=data.get('file_id'),
                                caption=f"👤 {NAME.get(language)}: {data.get('fullname')}\n\n📞 {TEL.get(language)}: {number}",
                                reply_markup=requestBtn(id, language))

    else:
        await bot.send_message(chat_id=GROUP,
                               text=f"👤 {NAME.get(language)}: {data.get('fullname')}\n\n📞 {TEL.get(language)}: {number}",
                               reply_markup=requestBtn(id, language))

    await state.finish()
    await BaseState.menu.set()
    await state.update_data({
        'language': language
    })


@dp.callback_query_handler(lambda text: text.data.startswith("approve_") or text.data.startswith("cancel_"), state="*")
async def application(call: types.CallbackQuery, state=FSMContext):
    data = await state.get_data()
    language = data.get('language')
    key = call.data.split("_")[0]
    id = call.data.split("_")[1]

    await call.answer(cache_time=0.02)
    await call.answer(text=f"{REQUEST.get(language)}", show_alert=True)
    BASE_URL = env.str("BASE_URL")
    data = requests.get(url=BASE_URL + f"/api/application-detail/{id}/", headers={"Accept-Language": language})
    response = data.json()

    try:
        language = response["language"]
        if key == "approve":
            await bot.send_message(chat_id=response["user_id"],
                                   text=f"{APP_RESPONSE_ACCEPT.get(language)}")
            await bot.edit_message_reply_markup(chat_id=GROUP, message_id=call.message.message_id)
        elif key == 'cancel':
            await call.message.delete()
            await bot.send_message(chat_id=response["user_id"],
                                   text=f"{APP_RESPONSE_CANCEL.get(language)}")
    except:
        pass
