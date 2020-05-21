import enum
import logging
import requests

from dataclasses import dataclass
from time import time

import typing
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from timeloop import Timeloop
from datetime import timedelta, datetime

CONFIRMATIONS_NEEDED = 2
POLLING_DELAY = timedelta(seconds=60)
TTL_IN_STATUS = timedelta(hours=2)
OLD_TRANSACTION_AGE = timedelta(hours=6)

API_TOKEN = '1221172107:AAG7GK7OBKMXLASZpbb4fME_SztgOoECF6o'

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info("welcome message")

    await message.reply("Hi!\nI'm MOSHNAR!")


class TrackingStatus(enum.Enum):
    NOT_STARTED = 1
    TRANSACTION_IS_OLD = 2
    NO_TRANSACTIONS = 3
    NOT_CONFIRMED = 4
    CONFIRMED = 5
    FAILED = 6


@dataclass
class Tracking:
    address: str
    added: datetime
    trigger_message: types.Message
    status: TrackingStatus
    statusUpdatedAt: datetime
    last_confirmations: int
    _deleted: bool

    @property
    def deleted(self):
        return self._deleted


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


@dataclass
class TransactionInfo:
    hash: str
    age: timedelta
    createdAt: datetime
    confirmations_cnt: int


def handle_address(address: str) -> typing.Tuple[TrackingStatus, typing.Optional[TransactionInfo]]:
    response = requests.get(f'https://blockchain.info/rawaddr/{address}')
    if response.status_code != 200:
        logging.error(f'Failed to check {address}')
        return TrackingStatus.FAILED, None

    address_info = response.json()
    if address_info['n_tx'] == 0:
        return TrackingStatus.NO_TRANSACTIONS, None

    last_transaction = address_info['txs'][0]
    transaction_hash = last_transaction['hash']
    transaction_time = int(last_transaction['time'])
    transaction_datetime = datetime.fromtimestamp(transaction_time)
    logging.info(f'cur_time={time()}, tx_time={transaction_time}, tx_datetime={transaction_datetime}')
    age_ms = time() - transaction_time
    transaction_age = timedelta(seconds=age_ms)
    logging.info(f'age_ms={age_ms}, age={transaction_age}')

    confirmations_cnt = get_confirmations_count(transaction_hash)
    if confirmations_cnt is None:
        return TrackingStatus.FAILED, None

    transaction_info = TransactionInfo(transaction_hash, transaction_age, transaction_datetime, confirmations_cnt)
    if transaction_age > OLD_TRANSACTION_AGE:
        logging.info(f'tx {transaction_hash} is too old: {transaction_age}')
        return TrackingStatus.TRANSACTION_IS_OLD, transaction_info

    if confirmations_cnt >= CONFIRMATIONS_NEEDED:
        return TrackingStatus.CONFIRMED, transaction_info
    else:
        return TrackingStatus.NOT_CONFIRMED, transaction_info


def is_done(t: Tracking) -> bool:
    status, _ = handle_address(t.address)
    return status == TrackingStatus.CONFIRMED


def too_long_in_status(t: Tracking) -> bool:
    return datetime.today() - t.statusUpdatedAt > TTL_IN_STATUS


def should_remove(t: Tracking) -> bool:
    return is_done(t) or too_long_in_status(t)


def timedelta_to_str(t: timedelta) -> str:
    res = ''
    if t.days > 0:
        res = f'{t.days} days'
    hours = t.seconds // 3600
    minutes = (t.seconds - hours * 3600) // 60
    if hours > 0:
        res += f' {hours} hours'
    if minutes > 0:
        res += f' {minutes} minutes'
    return res.strip()


tracked: typing.List[Tracking] = []


async def start_tracking(tracking: Tracking):
    global tracked

    status, tx_info = handle_address(tracking.address)
    tracking.status = status

    if status == TrackingStatus.FAILED:
        await tracking.trigger_message.answer(f'Failed to track {tracking.address}!\n\nPlease try again!')

    if status == TrackingStatus.NO_TRANSACTIONS:
        await tracking.trigger_message.answer(f'No transactions found for {tracking.address}!\n\nI will wait for the new transactions for {timedelta_to_str(TTL_IN_STATUS)}!')
        tracked.append(tracking)

    if status == TrackingStatus.TRANSACTION_IS_OLD:
        await tracking.trigger_message.answer(f'Last transaction for {tracking.address} was made {timedelta_to_str(tx_info.age)} ago...\n\nBut I will track for the new transactions for another {timedelta_to_str(TTL_IN_STATUS)}.')
        tracked.append(tracking)

    if status == TrackingStatus.NOT_CONFIRMED:
        await tracking.trigger_message.answer(f'{tx_info_to_str(tx_info)}\n\nI will tell you when it gets more :) ')
        tracked.append(tracking)

    if status == TrackingStatus.CONFIRMED:
        await tracking.trigger_message.answer(f'{tx_info_to_str(tx_info)}\n\nCHE PO MOSHNE)))) ')


@dp.message_handler(commands=['track'])
async def track_address(message: types.Message):
    logging.info(f'{message.text}')

    # TODO: validate bitcoin address
    args = message.get_args().strip()
    if args == "":
        await message.answer(f'You must provide at least one Bitcoin address!')
        return

    now = datetime.today()
    for t in [Tracking(address, now, message, TrackingStatus.NOT_STARTED, now, 0, False) for address in args.split()]:
        await start_tracking(t)


@dp.message_handler(commands=['show_tracking'])
async def show_all(message: types.Message):
    global tracked

    logging.info(f'{message.text}')

    await message.answer(f'Now tracking: {list(map(lambda t: t.address, tracked))}')


@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f"echo '{message.text}'")

    await message.answer(f'{message.text} хули')

tl = Timeloop()


def tx_info_to_str(info: TransactionInfo) -> str:
    confirmed = '[Confirmed]' if info.confirmations_cnt >= CONFIRMATIONS_NEEDED else '[Unconfirmed]'
    return f'{confirmed} Transaction\nId: {info.hash}\nCreated at: {info.createdAt}\nConfirmations: {info.confirmations_cnt}'


@tl.job(interval=timedelta(seconds=POLLING_DELAY.seconds))
async def check_addresses():
    global tracked

    for t in tracked:
        if t.deleted:
            continue

        new_status, tx_info = handle_address(t.address)

        if new_status != t.status:
            if new_status == TrackingStatus.NOT_CONFIRMED:
                await t.trigger_message.answer(f'{tx_info_to_str(tx_info)}\n\nI will tell you when it gets more :) ')
                t.status = new_status
                t.last_confirmations = tx_info.confirmations_cnt

            if new_status == TrackingStatus.CONFIRMED:
                await t.trigger_message.answer(f'{tx_info_to_str(tx_info)}\n\nCHE PO MOSHNE)))) ')
                t._deleted = True

        if new_status == TrackingStatus.NOT_CONFIRMED:
            if tx_info.confirmations_cnt != t.last_confirmations:
                await t.trigger_message.answer(f'Ха-тим помошнить (:\n[UNCONFIRMED][{tx_info.createdAt}][{tx_info.hash}]: {tx_info.confirmations_cnt} confirmations.\n\nI will tell you when it gets more :) ')


if __name__ == '__main__':
    tl.start(block=False)
    executor.start_polling(dp)
