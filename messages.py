import logging
from typing import Optional

from str_utils import tx_info_to_str
from tracking import Tracking, TransactionInfo


async def send_tx_info(t: Tracking, tx_info: TransactionInfo, msg: Optional[str] = None):
    return await send_tx_info_full(t, tx_info, msg_after=msg)


async def send_tx_info_full(t: Tracking, tx_info: TransactionInfo, msg_before: Optional[str] = None, msg_after: Optional[str] = None):
    output = f'{tx_info_to_str(tx_info)}'
    if msg_before is not None:
        output = f'{msg_before}\n\n' + output
    if msg_after is not None:
        output += f'\n\n{msg_after}'
    return await comment_tracking(t, output)


async def comment_tracking(t: Tracking, msg: str):
    logging.info(f'comment {t.address}')
    res = await t.trigger_message.reply(msg, parse_mode='HTML')
    logging.info(f'sent')
    return res
