from datetime import timedelta
from typing import List

from bot.settings import CONFIRMATIONS_NEEDED
from model.tracking import TransactionInfo


HASH_FOOTPRINT_SIZE = 20

UNCONF_EMOJI = '\u274c'
CONF_EMOJI = '\u2705'


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


def seconds_to_str(count: int) -> str:
    return unit_to_str(count, 'секунда', 'секунды', 'секунд')


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

    seconds = t.seconds - hours * 3600 - minutes * 60
    if seconds > 0:
        res += ' ' + seconds_to_str(seconds)

    return res.strip()


def get_addr_url(addr: str) -> str:
    return f'https://www.blockchain.com/btc/address/{addr}'


def get_addr_html_url(addr: str) -> str:
    return f'<a href=\'{get_addr_url(addr)}\'>{addr}</a>'


def get_addr_list_html_str(addrs: List[str]) -> str:
    return '\n'.join(map(get_addr_html_url, addrs))


# TODO: beautify
def tx_info_to_str(info: TransactionInfo) -> str:
    confirmed = CONF_EMOJI if info.confirmations_count >= CONFIRMATIONS_NEEDED else UNCONF_EMOJI
    return f'<pre>{confirmed}[{info.confirmations_count} confirmations]</pre>\n' \
           f'<code>[tx</code> {get_tx_url_html_str(info.hash)}<code>]</code>\n' \
           f'<pre>[created {info.created_at}]</pre>\n'


def get_tx_url(tx_hash: str) -> str:
    return f'https://www.blockchain.com/btc/tx/{tx_hash}'


def get_tx_url_html_str(tx_hash: str) -> str:
    text = f'{tx_hash[:HASH_FOOTPRINT_SIZE]}...'
    url = get_tx_url(tx_hash)

    return f'<a href=\'{url}\'>{text}</a>'
