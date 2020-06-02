import logging
from datetime import datetime
from typing import Tuple, Optional, Dict

import requests

from bot.settings import OLD_TRANSACTION_AGE, CONFIRMATIONS_NEEDED
from utils.str_utils import timedelta_to_str
from model.tracking import TrackingStatus, TransactionInfo

# TODO: refactor to BlockchainClient class or something
from bot.validator import is_valid_bitcoin_address


def get_unconfirmed_txs():
    response = requests.get(f'https://blockchain.info/unconfirmed-transactions?format=json')
    res = response.json()['txs']

    logging.debug(f'{len(res)} unconfirmed txs in total')

    return res


# TODO: random version
def get_last_unconfirmed_tx():
    res = get_unconfirmed_txs()[0]

    logging.debug(f'last_unconfirmed_tx = {res}')

    return res


def get_random_address_with_unconfirmed_tx() -> str:
    last_tx = get_last_unconfirmed_tx()
    return next((out.get('addr') for out in last_tx.get('out', [])), None)


def check_address(address: str) -> Tuple[TrackingStatus, Optional[TransactionInfo]]:
    if not is_valid_bitcoin_address(address):
        logging.debug(f'--> {address}')
        return TrackingStatus.INVALID_HASH, None

    logging.debug(f'get --> {address}')
    response = requests.get(f'https://blockchain.info/rawaddr/{address}')
    logging.info(response)
    if response.status_code == 429:
        logging.error(f'{response.headers}')
    if response.status_code != 200:
        logging.error(f'Failed to check {address}')
        return TrackingStatus.FAILED, None

    address_info = response.json()
    if address_info['n_tx'] == 0:
        return TrackingStatus.NO_TRANSACTIONS, None

    last_transaction = address_info['txs'][0]
    tx_info = _get_tx_info(last_transaction)

    if tx_info.confirmations_count is None:
        return TrackingStatus.FAILED, None

    if tx_info.age > OLD_TRANSACTION_AGE:
        logging.info(f'Last tx {tx_info.hash} is too old: {timedelta_to_str(tx_info.age)}')
        return TrackingStatus.TRANSACTION_IS_OLD, tx_info

    if tx_info.confirmations_count >= CONFIRMATIONS_NEEDED:
        return TrackingStatus.CONFIRMED, tx_info
    else:
        return TrackingStatus.NOT_CONFIRMED, tx_info


def _get_tx_info(last_transaction: Dict[str, str]) -> TransactionInfo:
    tx_hash = last_transaction['hash']
    tx_created_at = datetime.fromtimestamp(int(last_transaction['time']))
    confirmations_cnt = get_confirmations_count(tx_hash)
    return TransactionInfo(tx_hash, tx_created_at, confirmations_cnt)


def get_confirmations_count(tx: str) -> Optional[int]:
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
