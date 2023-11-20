from aiogram import types
from main import dp, logger, openai
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards


class Communacate(StatesGroup):
    comState = State()


users_message = {}
messages = [
    {'role': "system", "content": """Ты менеджер по продажам сервиса по внедрению нейросети в отдел продаж, тебя зовут Данил.

Наши соц сети: https://t.me/ilya24241

Стоимость внедрения нашего бота зависит от цели, задач и объемов работы.

Твоя задача предлагать покупать наш сервис, если клиент будет отказываться пытаться убедить его в покупки сервиса. 

Для покупки нужно обращаться главному менеджеру @son2421 

Веди диалог официально.
     """},
    {'role': "assistant",  "content": "Деловой стиль общения. Представляешься именем - Дарья. Не говоришь что ты виртуальный помошник "},

]


@dp.callback_query_handler(lambda call: call.data == "Пообщаться с ботом")
async def collect_id(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user}  - Пообщаться с ботом')
    kb = keyboards.back()
    await Communacate.comState.set()
    users_message[callback.from_user.id] = messages
    await callback.message.answer(f"Пишите, и я отвечу", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == "back", state=Communacate)
async def start(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.message_handler(state=Communacate.comState)
async def asd(message: types.Message):
    users_message[message.from_user.id].append(
        {"role": "user", "content": message.text})
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=users_message[message.from_user.id]
    )
    answer = response.choices[0].message.content
    logger.info(f'{message.from_user}: {message.text} {response}')
    users_message[message.from_user.id].append(
        {"role": "assistant", "content": answer})
    kb = keyboards.back()
    await message.reply(response.choices[0].message.content, reply_markup=kb)
