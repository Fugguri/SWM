from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
from handlers.telethon import TelegramClient
from threading import Thread


class Addbot(StatesGroup):
    intro = State()
    api_id = State()
    api_hash = State()
    number = State()
    connection = State()
    scenario = State()
    scenario_system = State()
    scenario_assistant = State()


thread = ""
client = []
users_data = {}

kb = keyboards.back().add(types.InlineKeyboardButton(
    text="Далее", callback_data="Далее"))


@dp.callback_query_handler(lambda call: call.data == "Добавить бота")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user}  - добавить бота')
    await Addbot.intro.set()
    users_data[callback.from_user.id] = {}
    await callback.message.answer(text="Ссылка на инструкцию по регистрации https://telegra.ph/Instrukciya-po-registracii-03-25 ", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == "Далее", state=Addbot.intro)
async def next(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - Добавление бота - далее( после инструкции)')
    await Addbot.api_id.set()

    await callback.message.answer(f"Введите api_id\nЧтобы продолжить нажмите далее", reply_markup=kb)


@dp.message_handler(state=Addbot.api_id)
async def collect_id(message: types.Message):
    logger.info(f'{message.from_user}  - добавление API_id')
    await Addbot.api_id.set()
    api_id = message.text
    users_data[message.from_user.id]["api_id"] = api_id
    await message.answer(f"Введите api_id \nТекущий: {api_id}\nЧтобы продолжить нажмите далее", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == "Далее", state=Addbot.api_id)
async def next_id(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - Добавление бота - далее( после api_id)')
    await Addbot.api_hash.set()
    await callback.message.answer(f"Введите api_hash\nЧтобы продолжить нажмите далее", reply_markup=kb)


@dp.message_handler(state=Addbot.api_hash)
async def collect_hash(message: types.Message):
    logger.info(f'{message.from_user}  - добавление API_hash')
    api_hash = message.text
    users_data[message.from_user.id]["api_hash"] = api_hash
    await message.answer(f"Введите api_hash \nТекущий: {api_hash}\nЧтобы продолжить нажмите далее", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == "Далее", state=Addbot.api_hash)
async def next_numver(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - Добавление бота - далее( после hash )')
    await Addbot.number.set()
    await callback.message.answer(f"Введите номер телефона, который привязали при регистрации.\n Обратите внимание, номер должен начинаться с '+' \nЧтобы продолжить нажмите далее", reply_markup=kb)


@dp.message_handler(state=Addbot.number)
async def collect_hash(message: types.Message):
    logger.info(f'{message.from_user}  - добавление номера телефона')
    number = message.text
    users_data[message.from_user.id]["number"] = number
    await message.answer(f"Введите Номер телефона\n Обратите внимание, номер должен начинаться с '+' \nТекущий: {number}\nЧтобы продолжить нажмите далее {users_data[message.from_user.id]}", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == "Далее", state=Addbot.number)
async def next_numver(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - connect')
    await Addbot.connection.set()
    phone = users_data[callback.from_user.id]["number"]
    api_id = users_data[callback.from_user.id]["api_id"]
    api_hash = users_data[callback.from_user.id]["api_hash"]
    client = users_data[callback.from_user.id]["clients"] = TelegramClient(
        "sessions/" + phone, int(api_id), api_hash)
    # client = TelegramClient("+79882547866",
    #                         25080938,
    #                         "704a82f7554add37aba76dc949c88b7b")
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await callback.message.answer(f"Запрос отправлен введите код.\nЧтобы продолжить нажмите далее", reply_markup=kb)
            await client.send_code_request(phone)
            await client.disconnect()
        except Exception as ex:
            await callback.message.answer(ex)
            await client.disconnect()

            await callback.message.answer(f"Ошибка, {ex} \nПопробуйте заново или обратитесь в поддержкку", reply_markup=kb)
    else:
        await callback.message.answer(f"Success add profile: {phone}\nМожете перейти во вкладку редактирования бота", reply_markup=keyboards.back())
        db.create_client(callback.from_user.id,
                         api_id, api_hash, phone)
        await client.disconnect()


@dp.message_handler(state=Addbot.connection)
async def next_number(message: types.Message):
    phone = users_data[message.from_user.id]["number"]
    client = users_data[message.from_user.id]["clients"]
    api_id = users_data[message.from_user.id]["api_id"]
    api_hash = users_data[message.from_user.id]["api_hash"]
    await client.connect()
    if not await client.is_user_authorized():
        try:
            print(phone)
            await client.sign_in("sessions/" + phone, message.text)
            await client.disconnect()
            await message.answer(f"Success add profile: {phone}\nМожете перейти во вкладку редактирования бота", reply_markup=keyboards.back())
            await Addbot.scenario.set()
            db.create_client(message.from_id,
                             api_id, api_hash, phone)
        except Exception as ex:
            await message.answer(ex)
    else:
        await message.answer(f"Success add profile: {phone}\nМожете перейти во вкладку редактирования бота", reply_markup=keyboards.back())
        db.create_client(message.from_id,
                         api_id, api_hash, phone)
        await Addbot.scenario.set()
    # import json
    # data = {
    #     "api_id": api_id,
    #     "api_hash": api_hash,
    #     "number": phone
    # }
    # with open(f"configs/{message.from_id}.json", "w") as write_file:
    #     json.dump(data, write_file)


# @dp.message_handler(commands="f")
# async def f(message: types.Message):
#     await Addbot.connection.set()
#     phone = "+79882547866"
#     api_id = 25080938
#     api_hash = "704a82f7554add37aba76dc949c88b7b"
#     client = TelegramClient(
#         "sessions/" + phone, api_id, api_hash)
#     try:
#         await client.send_code_request(phone)
#         await message.answer(f"Запрос отправлен введите код.\nЧтобы продолжить нажмите далее", reply_markup=kb)
#         await client.disconnect()
#     except Exception as ex:
#         await message.answer(ex)
#         await message.answer(f"Ошибка, {ex} \nПопробуйте заново или обратитесь в поддержкку", reply_markup=kb)
#     await client.disconnect()


@ dp.callback_query_handler(lambda call: call.data == "back", state=Addbot)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())
