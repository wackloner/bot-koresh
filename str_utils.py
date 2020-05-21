from datetime import timedelta

from settings import CONFIRMATIONS_NEEDED
from tracking import TransactionInfo

ADDRESS_FOOTPRINT_SYMBOLS_COUNT = 5


def timedelta_to_str(t: timedelta) -> str:
    res = ''
    if t.days > 0:
        res = f'{t.days} дней'
    hours = t.seconds // 3600
    minutes = (t.seconds - hours * 3600) // 60
    if hours > 0:
        res += f' {hours} часов'
    if minutes > 0:
        res += f' {minutes} минут'
    return res.strip()


# TODO: colors
def tx_info_to_str(info: TransactionInfo) -> str:
    confirmed = 'Confirmed' if info.confirmations_count >= CONFIRMATIONS_NEEDED else 'Unconfirmed'
    return f'<b>{confirmed}</b> tx <i>{get_address_footprint(info.hash)}</i>\n' \
           + f'Created at {info.created_at}\n<u>Confirmations: {info.confirmations_count}</u>'


def get_address_footprint(address: str) -> str:
    return address[0: ADDRESS_FOOTPRINT_SYMBOLS_COUNT] + '...' + address[-ADDRESS_FOOTPRINT_SYMBOLS_COUNT:]
