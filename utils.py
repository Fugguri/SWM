
from speech_to_text import speech_to_text
from main import gs
from DB_connectors.MySql_connect import Database
from telethon import TelegramClient, events
import openai
import asyncio
users_message = {}
clients = {}
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
        print('Working with', me.first_name, me.last_name, me.username)
        await client.start()
        client.add_event_handler(my_event_handler, events.NewMessage)
        await client.run_until_disconnected()


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
            message_text = speech_to_text(f"/root/SWM/{filename}")

    except:
        pass
    phone = "+" + me.phone
    settings = db.get_data_for_client(phone)[5]

    try:
        users_message[event.chat_id]
    except:
        db.start_new_dialog_counter_update(phone)
        settings = db.get_data_for_client(phone)[5]
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
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=users_message[event.chat_id]
        )
        answer = response.choices[0].message.content

        users_message[event.chat_id].append(
            {"role": "assistant", "content": answer})
        await event.client.send_message(message=answer, entity=sender)
        try:
            gs.sheets_append_row(db.get_analytic_sheet_name(phone),
                                 sender.username,
                                 phone,
                                 message_text,
                                 answer)
        except Exception as ex:
            print(ex)
    except openai.BadRequestError:
        await event.client.send_message(message="Не понимаю.Слишком много информации", entity=sender)
    # except openai.PermissionDeniedError as er:
    #     print(er)

    except openai.RateLimitError as ex:
        print(ex)
        await asyncio.sleep(20)
        await my_event_handler(event)
    except ValueError:
        await event.client.send_message(message="Не понимаю.\nПерефразируйте", entity=sender)
    except Exception as ex:
        print(ex)
