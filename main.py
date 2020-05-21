import logging
import random

from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from datetime import datetime

from settings import API_TOKEN
from tasks import schedule_updater
from tracking import TrackingStatus, Tracking
from tracking_manager import start_tracking, get_all_trackings

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


GREETINGS = [
    'Че по мошне))',
    'Залетает)))))',
    'Ха-тим)',
    'Мас-тер Карди-ГАН )'
]


# TODO: create phrases lists
@dp.message_handler(commands=['start'])
async def greet(message: types.Message):
    logging.info("/start")

    greeting_id = random.randint(0, len(GREETINGS) - 1)
    await message.answer(GREETINGS[greeting_id])


@dp.message_handler(commands=['help'])
async def show_help(message: types.Message):
    logging.info("/help")

    await message.answer("Что умею:\n\n/track addr [addr1 [addr2] ...]\n/show_trackings")


# TODO: get address/tx hash -> check status + question about tracking
# TODO: check execution time (usually it works long)
@dp.message_handler(commands=['track'])
async def track_address(message: types.Message):
    logging.info(f'{message.text}')

    # TODO: validate bitcoin address
    args = message.get_args().strip()
    if args == "":
        await message.reply(f'Анус себе потрекай братан)')
        return

    now = datetime.today()
    for t in [Tracking(address, now, message, TrackingStatus.NOT_STARTED, now, 0) for address in args.split()]:
        await start_tracking(t)


# TODO: show tracked info (separate command)
@dp.message_handler(commands=['show_trackings'])
async def show_trackings(message: types.Message):
    logging.info(f'{message.text}')

    tracked = get_all_trackings()
    msg = 'Хз, я чисто чиллю' if tracked == [] else f'Палю адреса: {list(map(lambda t: t.address, tracked))}'
    await message.answer(msg)


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f"echo '{message.text}'")

    await message.answer(f'{message.text} хули')


if __name__ == '__main__':
    schedule_updater()
    executor.start_polling(dp)
