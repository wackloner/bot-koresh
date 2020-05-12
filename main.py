import logging
import os

from aiogram.utils.executor import start_webhook
from aiogram import Bot, Dispatcher, types

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'
PROJECT_NAME = 'moshnar-bot'

APP_HOST = "localhost"
APP_PORT = os.getenv('PORT') or 8080

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


logging.basicConfig(level=logging.INFO)

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


async def on_startup(dp):
    logging.info('Starting...')

    logging.info(f'Setting webhook to {WEBHOOK_URL}')
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.info('Shutting down...')

    await bot.delete_webhook()

    logging.info('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=APP_HOST,
        port=APP_PORT,
    )
