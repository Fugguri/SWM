from aiogram import types
from main import dp, logger
from aiogram.dispatcher.filters.state import State, StatesGroup


@dp.callback_query_handler(lambda call: call.data == "Информация")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user}  - информация')
    await callback.message.answer(text="Наш бот представляет собой инструмент для автоматизации продаж в Telegram. С помощью нашего бота вы сможете создать воронку продаж, включающую в себя персональные сообщения, уведомления и задачи в рамках продаж, а также многие другие инструменты, чтобы максимально эффективно продавать свои товары или услуги в Telegram. ")
