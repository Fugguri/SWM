import logging
import json
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import openai
import asyncio
from utils import *
from DB_connectors.MySql_connect import Database
from google_sheets import GS
file = open("config.json", "r")

config = json.load(file)

file = open("config.json", "r")
config = json.load(file)

OPENAI_KEY = config["openai"]
TOKEN_API = config["TOKEN_API"]

openai.api_key = OPENAI_KEY
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
gs = GS()
storage = MemoryStorage()
bot = Bot(config["TOKEN_API"], parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
db = Database("swm")
py_handler = logging.FileHandler(f"logs/{__name__}.log", mode='w')
logger.addHandler(py_handler)


async def some_callback():
    for bot in db.all_active_bots():
        await start_client(bot)


def between_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(some_callback())

    loop.close()


async def on_startup(_):
    print("Бот запущен")
    logger.debug("Запущен бот!")
    db.cbdt()
    for bot in db.all_active_bots():
        print(bot[4])

        loop = asyncio.get_event_loop()
        try:
            loop.create_task(start_client(bot))
        except:
            await asyncio.sleep(5)
            loop.create_task(start_client(bot))
            
        # loop.run_forever()
        # await
        # await asyncio.sleep(3)
    # _thread = threading.Thread(target=between_callback)
    # _thread.start()


async def on_shutdown(_):
    print("Бот остановлен")


if __name__ == "__main__":
    from handlers import dp
    # dp.start_polling(        dispatcher=dp,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True)
    executor.start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
