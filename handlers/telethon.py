from main import dp, bot
from aiogram import types
from telethon import TelegramClient, events
import asyncio
import openai
# инициализация Telethon
# api_id = your_api_id
# api_hash = 'your_api_hash'
client = TelegramClient("sessions/+79882547866",
                        25080938,
                        "704a82f7554add37aba76dc949c88b7b")

# инициализация бота Aiogram

# ваш код здесь

# запуск Telethon
client.start()

# остановка Telethon
client.disconnect()

# отправляем сообщение при получении нового сообщения в Telethon
users_message = {}
messages = [
    {'role': "system", "content": """Ты бот - менеджер по продажам, строительной кампании "ЛСР" Представляешься именем - Виктор. Не говоришь что ты виртуальный помошник 
Обьекты недвижимости можно посмотреть по ссылке:  https://fugguri.github.io/simpleSUI/
Наши соц сети: https://tg.me/fugguri\n
Наши акции: Приведи друга - скидка на 10%
Рассрочка: вы можете оформить рассрочку 0/0/24 с первоначальным взносом в 30 % от стоимости
     """},
    # {'role': "system", "content": "Список акций: Приведи друга - бесплатный доступ на 2 месяца"},
    # {'role': "user",  "content": "Расскажи об услугах, которые мы предоставляем"},
    {'role': "assistant",  "content": "Деловой стиль общения. "},

]


# @client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        users_message[event.chat_id]
    except:
        users_message[event.chat_id] = messages

    users_message[event.chat_id].append(
        {"role": "user", "content": event.text})
    print(users_message[event.chat_id])
    responce = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=users_message[event.chat_id]
    )
    sender = await event.get_sender()
    answer = responce['choices'][0]['message']['content']
    users_message[event.chat_id].append(
        {"role": "assistant", "content": answer})
    await event.client.send_message(message=answer, entity=sender)
    print(event.chat_id, event.text)

# отправляем сообщение в Telethon при получении команды от пользователя в Aiogram


@dp.message_handler(commands=['run'])
async def start_command(message: types.Message):
    # await client.send_message('some_user', f'Привет, {message.from_user.first_name}!')
    await message.answer("done!")
    await main(client)
# Обратите внимание, что функции Telethon работают синхронно (блокируют поток выполнения), поэтому вам, возможно, потребуется использовать `asyncio.loop.run_in_executor()`


async def main(client):
    async with client:
        me = await client.get_me()
        print('Working with', me.phone, me.last_name)
        await client.start()
        client.add_event_handler(my_event_handler, events.NewMessage)
        await client.run_until_disconnected()
