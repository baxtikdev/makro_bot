import requests
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from data.config import env
from keyboards.inline.inlineKeys import language, mainMenu
from loader import dp
from states.baseState import BaseState
from translations.images import INTRO_IMAGE
from translations.translation import INTRO


@dp.message_handler(content_types=types.ContentType.PHOTO, state="*")
async def photo(message: types.Message, state: FSMContext):
    print(message.photo[0].file_id)


@dp.message_handler(commands=['start', 'lang'], state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    a = await message.answer('.', reply_markup=ReplyKeyboardRemove())
    await a.delete()
    await message.answer(
        "Assalomu alaykum!\n\n🌐 <b>Makro</b>ning rasmiy Telegram-botiga xush kelibsiz!\nIltimos, til tanlang.\n\n➖➖➖➖➖➖➖➖➖➖\n\nЗдраствуйте!\n\n🌐 Добро пожаловать на официальный Telegram-бот <b>Makro</b>\nПожалуйста, выберите язык.",
        reply_markup=language)
    await BaseState.language.set()


@dp.callback_query_handler(lambda message: message.data == "change_language", state="*")
async def change_language(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer(
        "Assalomu alaykum!\n\n🌐 <b>Makro</b>ning rasmiy Telegram-botiga xush kelibsiz!\nIltimos, til tanlang.\n\n➖➖➖➖➖➖➖➖➖➖\n\nЗдраствуйте!\n\n🌐 Добро пожаловать на официальный Telegram-бот <b>Makro</b>\nПожалуйста, выберите язык.",
        reply_markup=language)
    await BaseState.language.set()


@dp.callback_query_handler(lambda message: message.data in ['uz', 'ru'], state=BaseState.language)
async def set_language(call: types.CallbackQuery, state=FSMContext):
    await call.message.delete()
    await state.update_data({
        'language': call.data
    })
    await call.message.answer_photo(
        photo=INTRO_IMAGE,
        caption=INTRO.get(call.data),
        reply_markup=mainMenu(call.data)
    )
    await call.answer(cache_time=0.02)
    await BaseState.menu.set()
