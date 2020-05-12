import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'
PROJECT_NAME = 'moshnar-bot'

PORT = os.getenv('PORT') or 8080
# PROXY_URL = 'http://167.71.105.68:8080'

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'
WEBHOOK_URL_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_URL_PATH}'

logging.basicConfig(level=logging.INFO)

# bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info("kek")

    await message.reply("Hi!\nI'm MOSHNAR!")


@dp.message_handler()
async def echo(message: types.Message):
    logging.info("kek")

    await message.answer(f'{message.text} хули')


async def on_startup(app):
    await bot.delete_webhook()
    logging.info(f'Setting webhook to {WEBHOOK_URL}')
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    web.run_app(app, host='0.0.0.0', port=PORT)
