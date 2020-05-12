import logging

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'
# PROXY_URL = 'http://167.71.105.68:8080'

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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
