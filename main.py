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

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )

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

telegram_update = "Empty"

@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    global telegram_update
    telegram_update = Update(**update)
    await dp.feed_raw_update(bot, update)
    await bot.get_session().close()


@app.on_event("shutdown")
async def on_shutdown():
    await bot.get_session().close()


@app.get('/')
def hello_world():
    return telegram_update


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
