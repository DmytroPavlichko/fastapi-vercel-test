from contextlib import asynccontextmanager
from fastapi import FastAPI
import time
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, Update

TOKEN = os.getenv('TOKEN')

WEBHOOK_PATH = f"/bot/{TOKEN}"
RENDER_WEB_SERVICE_NAME = "fastapi-vercel-test-vert"
WEBHOOK_URL = "https://" + RENDER_WEB_SERVICE_NAME + ".vercel.app" + WEBHOOK_PATH

logging.basicConfig(filemode='a', level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)

    yield

    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.reply("Hello!")

@dp.message()
async def main_handler(message: Message):
    try:
        user_id = message.from_user.id
        user_full_name = message.from_user.full_name
        logging.info(f'Main: {user_id} {user_full_name} {time.asctime()}. Message: {message}')
        await message.reply("Hello world!")
    except:
        logging.info(f'Main: {user_id} {user_full_name} {time.asctime()}. Message: {message}. Error in main_handler')
        await message.reply("Something went wrong...")


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)


@app.get('/')
def hello_world():
    return "Hello,World"


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
