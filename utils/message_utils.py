import logging
from typing import Optional

from telegram import Bot, ParseMode

from model.stickers import Stickers
from utils.str_utils import tx_info_to_str, get_addr_html_url
from model.tracking import Tracking


def send_message(context, update, msg):
    context.bot.send_message(update.message.chat.id, msg)


def send_tx_info(t: Tracking, msg: Optional[str] = None):
    return send_tracking_info_full(t, msg_after=msg)


def send_tracking_info_full(t: Tracking, msg_before: Optional[str] = None, msg_after: Optional[str] = None):
    txs_str = '\n\n'.join([tx_info_to_str(tx_info) for tx_info in t.transactions])
    output = f'{get_addr_html_url(t.address)}:\n{txs_str}'
    if msg_before is not None:
        output = f'{msg_before}\n\n' + output
    if msg_after is not None:
        output += f'\n{msg_after}'

    return comment_tracking(t, output)


def comment_tracking(t: Tracking, msg: str):
    logging.debug(f'Commenting... {t.address}')

    # TODO: fix local
    from bot.context import app_context
    return app_context.bot.send_message(text=msg, chat_id=t.chat_id, disable_web_page_preview=True, parse_mode=ParseMode.HTML)


def send_sladko(bot: Bot, chat_id):
    bot.send_sticker(chat_id, Stickers.SLADKO)


def send_sesh(bot: Bot, chat_id):
    bot.send_sticker(chat_id, Stickers.SESH)
