from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
from handlers.telethon import TelegramClient
from threading import Thread
import asyncio


class Static(StatesGroup):
    counter = State()
    select_phone=State()
    sheet_name =State()
kb = keyboards.back()
phone = {}


@dp.callback_query_handler(lambda call: call.data == "Собрать статистику",state="*")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user} - Собрать статистику')
    await Static.counter.set()
    text = """Выберите номер,с которого собираем статистику"""
    nums = db.all_user_bots(callback.from_user.id)
    kb = keyboards.back()
    kb.add(types.InlineKeyboardButton(
                text="Дабавить гугл таблицу", callback_data="add_sheet_name"))
    for num in nums:
        if types.InlineKeyboardButton(
                text=num, callback_data=num) not in kb["inline_keyboard"]:
            kb.add(types.InlineKeyboardButton(
                text=num, callback_data=num))
    await callback.message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)


@dp.callback_query_handler(lambda call: call.data == "add_sheet_name", state=Static)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    kb = keyboards.back()
    nums = db.all_user_bots(callback.from_user.id)
    for num in nums:
        if types.InlineKeyboardButton(
                text=num, callback_data=num) not in kb["inline_keyboard"]:
            kb.add(types.InlineKeyboardButton(
                text=num, callback_data=num))
    await callback.message.answer("""Выберите номер """,reply_markup=kb )
    await Static.select_phone.set()
    

@dp.message_handler(state=Static.sheet_name)
async def update_sheet_name(message: types.Message, state:State):
    if db.get_analytic_sheet_exist(message.text, message.from_user.id) :
        await message.answer("Такое имя таблицы занято, попробуйте другое")
        return
    try:
        
        db.create_analytics(message.from_id,
                            phone[message.from_id],
                            message.text
                            )
        await message.answer(f"Успешно добавлена гугл таблица {message.text} к номеру {phone[message.from_id]}",reply_markup=kb)
    except:
        
        pass
@dp.callback_query_handler(lambda call: call.data == "back", state=Static)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.callback_query_handler(state=Static.select_phone)
async def create_scenario(callback: types.CallbackQuery,state =State):
    
    phone[callback.from_user.id] = callback.data
    await callback.message.answer(f"""""Введите название Гугл таблицы для номера {callback.data}, в которой будут отображаться данные.\
Внимание!!! Дайте доступ к гугл таблице аккаунту "my-test-account@brave-design-383019.iam.gserviceaccount.com" иначе данные не будут отображаться\nВы можете добавлять несколько номеров в одну таблицу""",  reply_markup=kb)
    await Static.sheet_name.set()
        
        
@dp.callback_query_handler(state=Static)
async def create_scenario(callback: types.CallbackQuery,state=State):    
    try:
            counter = db.get_dialog_counter(callback.data)[0]
    except:
            counter = 0
    await callback.message.answer(f"У профиля {callback.data} - {counter} диалога(ов)", reply_markup=kb)


@ dp.message_handler(lambda mes: mes.text == "Далее", state=Static)
async def update_scenario(message: types.Message):
    numbers = db.all_user_bots(message.from_id)
    await message.answer("Выберите профиль {}".format(numbers), reply_markup=kb)
