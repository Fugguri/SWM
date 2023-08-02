
from DB_connectors.MySql_connect import Database
from telethon import TelegramClient, events
import openai
import asyncio
users_message = {}
clients = {}
from main import gs
db = Database("swm")


async def disconnect(phone):
    clients[phone].disconnect()

users_message = {}


async def start_client(a):

    api_id = a[2]
    api_hash = a[3]
    phone = a[4]
    is_active = a[-1]
    client = TelegramClient("sessions/"+phone, api_id, api_hash)
    if is_active:
        try:
            await main(client)
        except Exception as ex:
            print(ex)
    else:
        print(phone)


async def main(client):
    async with client:
        me = await client.get_me()
        print('Working with', me.first_name, me.last_name)
        await client.start()
        client.add_event_handler(my_event_handler, events.NewMessage)
        await client.run_until_disconnected()


async def my_event_handler(event):
    me = await event.client.get_me()
    if event.is_channel:
        return
    if event.is_group:
        return
    phone = "+" + me.phone
    settings = db.get_data_for_client(phone)[5]

    try:
            users_message[event.chat_id]
    except:
            db.start_new_dialog_counter_update(phone)
            settings = db.get_data_for_client(phone)[5]
            messages = [{'role': "system", "content": settings},]
            users_message[event.chat_id] = messages

    if users_message[event.chat_id][0]["content"] != settings:
            messages = [
                {'role': "system", "content": settings},
            ]
            users_message[event.chat_id] = messages

    users_message[event.chat_id].append(
            {"role": "user", "content": event.text})
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
                             event.text,
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
