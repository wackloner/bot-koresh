import logging
import requests

from dataclasses import dataclass
from time import time

import typing
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from timeloop import Timeloop
from datetime import timedelta


CONFIRMATIONS_NEEDED = 2

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info("welcome message")

    await message.reply("Hi!\nI'm MOSHNAR!")


@dataclass
class Tracking:
    address: str
    added: float
    request: types.Message


def get_confirmations_count(tx: str):
    response = requests.get(f'https://blockchain.info/rawtx/{tx}')
    if response.status_code != 200:
        logging.error(f'Failed to fetch transaction {tx} info')
        return None

    transaction_info = response.json()
    block_height = transaction_info.get('block_height')
    if block_height is None:
        return 0

    response = requests.get('https://blockchain.info/q/getblockcount')
    if response.status_code != 200:
        logging.error(f'Failed to fetch total number of blocks')
        return None

    total_blocks = response.json()

    return total_blocks - block_height + 1


TRANSACTION_TTL = 3 * 60 * 60
NEW_TX_WAITING_TIME = 60 * 60


def get_last_transaction_hash_if_fresh(address: str) -> typing.Optional[str]:
    response = requests.get(f'https://blockchain.info/rawaddr/{address}')
    if response.status_code != 200:
        logging.error(f'Failed to check {address}')
        return None

    address_info = response.json()
    if address_info['n_tx'] == 0:
        return None

    last_transaction = address_info['txs'][0]
    transaction_hash = last_transaction['hash']
    transaction_age = time() - last_transaction['time']

    if transaction_age > TRANSACTION_TTL:
        logging.info(f'tx {transaction_hash} is too old: {transaction_age}s')
        return None

    return transaction_hash


def is_done(t: Tracking) -> bool:
    last_transaction_hash = get_last_transaction_hash_if_fresh(t.address)
    if last_transaction_hash is None:
        return False

    confirmations_cnt = get_confirmations_count(last_transaction_hash)

    logging.info(f'{last_transaction_hash} = {confirmations_cnt}')
    return confirmations_cnt >= CONFIRMATIONS_NEEDED


def is_tracking_too_long(t: Tracking) -> bool:
    return time() - t.added > NEW_TX_WAITING_TIME


def should_remove(t: Tracking) -> bool:
    return is_done(t) or is_tracking_too_long(t)


tracked = []


@dp.message_handler(commands=['track'])
async def track_address(message: types.Message):
    global tracked

    logging.info(f'{message.text}')

    # TODO: check address
    args = message.get_args().strip()
    if args == "":
        await message.answer(f'You must provide at least one Bitcoin address!')
        return

    now = time()
    for t in [Tracking(addr, now, message) for addr in args.split()]:
        tracked.append(t)

    await message.answer(f'Now tracking: {tracked}')


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f"echo '{message.text}'")

    await message.answer(f'{message.text} хули')

tl = Timeloop()


@tl.job(interval=timedelta(seconds=3))
def check_addresses():
    global tracked
    # TODO: thread-safety
    tracked = [t for t in tracked if not should_remove(t)]


if __name__ == '__main__':
    tl.start(block=False)
    executor.start_polling(dp)
