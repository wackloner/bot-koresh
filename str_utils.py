from datetime import timedelta

from settings import CONFIRMATIONS_NEEDED
from tracking import TransactionInfo


HASH_FOOTPRINT_SIZE = 20


def unit_to_str(count: int, one: str, no_one: str, no_many: str) -> str:
    if count % 10 == 1:
        return f'{count} {one}'
    if 2 <= count % 10 <= 4:
        return f'{count} {no_one}'
    return f'{count} {no_many}'


def days_to_str(count: int) -> str:
    return unit_to_str(count, 'день', 'дня', 'дней')


def hours_to_str(count: int) -> str:
    return unit_to_str(count, 'час', 'часа', 'часов')


def minutes_to_str(count: int) -> str:
    return unit_to_str(count, 'минута', 'минуты', 'минут')


def timedelta_to_str(t: timedelta) -> str:
    res = ''
    if t.days > 0:
        res = days_to_str(t.days)

    hours = t.seconds // 3600
    if hours > 0:
        res += ' ' + hours_to_str(hours)

    minutes = (t.seconds - hours * 3600) // 60
    if minutes > 0:
        res += ' ' + minutes_to_str(minutes)

    return res.strip()


# TODO: colors
def tx_info_to_str(info: TransactionInfo) -> str:
    confirmed = 'confirmed' if info.confirmations_count >= CONFIRMATIONS_NEEDED else 'unconfirmed'
    return f'<b>{confirmed}</b>\ntx <i>{get_tx_url_html_str(info.hash)}</i>\n' \
           + f'from <code>{info.created_at}</code>\nconfirmations: <code>{info.confirmations_count}</code>'


def get_tx_url(tx_hash: str) -> str:
    return f'https://www.blockchain.com/btc/tx/{tx_hash}'


def get_tx_url_html_str(tx_hash: str) -> str:
    text = f'{tx_hash[:HASH_FOOTPRINT_SIZE]}...'
    url = get_tx_url(tx_hash)

    return f'<a href=\'{url}\'>{text}</a>'
