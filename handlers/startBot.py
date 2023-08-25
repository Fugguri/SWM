import openai
import asyncio
from main import dp, bot
from aiogram import types
from main import dp, logger, db,gs
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
from telethon import TelegramClient, events
from handlers.telethon import TelegramClient
from speech_to_text import speech_to_text 


kb = keyboards.back().add(types.InlineKeyboardButton(
    text="Далее", callback_data="Далее"))


class StartBot(StatesGroup):
    scenario = State()
    scenario_system = State()
    scenario_assistant = State()


kb = keyboards.back()
phone = {}


@dp.callback_query_handler(lambda call: call.data == "Запуск бота")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user.id}  - Редактировать бота')
    await StartBot.scenario.set()
    text = """Выберите номер, к которому хотите привязать новый сценарий"""
    nums = db.all_user_bots(callback.from_user.id)
    kb = keyboards.back()
    for num in nums:
        if types.InlineKeyboardButton(
                text=num, callback_data=num) not in kb["inline_keyboard"]:
            kb.add(types.InlineKeyboardButton(
                text=num, callback_data=num))
    await callback.message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)


@ dp.callback_query_handler(lambda call: call.data == "back", state=StartBot)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.callback_query_handler(state=StartBot.scenario)
async def select_phone(callback: types.callback_query):
    # phone[callback.from_user.id] = callback.data
    a = db.get_data_for_client(callback.data)
    api_id = a[2]
    api_hash = a[3]
    phone = a[4]
    settings = a[5]
    client = TelegramClient("sessions/"+phone, api_id, api_hash)
    messages = [{'role': "system", "content": settings},]
    if db.is_active(phone):
        try:
            await callback.message.answer(f"Запустил бота {phone.replace('sessions/','')}", reply_markup=kb)
            asyncio.ensure_future(main(client))
            # await main(client)
        except Exception as ex:
            print(ex)
            await callback.message.answer(f"Ошибка бота {ex} обратитеть в поддержку".format(phone))
    else:
        await callback.message.answer("Оплатите подписку на сервис.\nДля опталы подписки пишите https://t.me/son2421")

users_message = {}


async def my_event_handler(event):
    me = await event.client.get_me()
    if event.is_channel:
        return
    if event.is_group:
        return
    message_text = event.text
    try:
        if event.document.mime_type == 'audio/ogg':
            filename = f"media/{event.document.id}.ogg"
            await event.download_media(file=filename)
            message_text = speech_to_text(f"/home/fugguri/Документы/PROJECT/swm/{filename}")
    except:
        pass
    phone = "+" + me.phone
    settings = db.get_data_for_client(phone)[5]

    try:
            users_message[event.chat_id]
    except:
            settings = db.get_data_for_client(phone)[5]
            db.start_new_dialog_counter_update(phone)
            messages = [{'role': "system", "content": settings},]
            users_message[event.chat_id] = messages
    if users_message[event.chat_id][0]['content'] != settings:
        messages = [{'role': "system", "content": settings},]

    if users_message[event.chat_id][0]["content"] != settings:
            messages = [
                {'role': "system", "content": settings},
            ]
            users_message[event.chat_id] = messages

    users_message[event.chat_id].append(
            {"role": "user", "content": message_text})
    sender = await event.get_sender()
    try:
        responce = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=users_message[event.chat_id]
        )
        answer = responce['choices'][0]['message']['content']

        users_message[event.chat_id].append(
                {"role": "assistant", "content": answer})
        await event.client.send_message(message=answer, entity=sender)
        try:
            gs.sheets_append_row(db.get_analytic_sheet_name(phone),
                             sender.username,
                             phone,
                             message_text,
                             answer)
        except Exception as ex :
            print(ex)
    except openai.error.InvalidRequestError:
            await event.client.send_message(message="Не понимаю.Слишком много информации", entity=sender)
    except openai.error.RateLimitError as ex:
            print(ex)
            await asyncio.sleep(20)
            await my_event_handler(event)
    except ValueError:
            await event.client.send_message(message="Не понимаю.\nПерефразируйте", entity=sender)
    except Exception as ex:
            print(ex)



async def main(client):
    async with client:
        me = await client.get_me()
        print('Working with', me.first_name, me.last_name)
        await client.start()
        client.add_event_handler(my_event_handler, events.NewMessage)
        await client.run_until_disconnected()
