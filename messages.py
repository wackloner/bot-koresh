import logging
from typing import Optional

from telegram import Bot

from utils.str_utils import tx_info_to_str
from model.tracking import Tracking, TransactionInfo


def send_message(context, update, msg):
    context.bot.send_message(update.message.chat.id, msg)


def send_tx_info(t: Tracking, tx_info: TransactionInfo, msg: Optional[str] = None):
    return send_tx_info_full(t, tx_info, msg_after=msg)


def send_tx_info_full(t: Tracking, tx_info: TransactionInfo, msg_before: Optional[str] = None, msg_after: Optional[str] = None):
    output = f'{tx_info_to_str(tx_info)}'
    if msg_before is not None:
        output = f'{msg_before}\n\n' + output
    if msg_after is not None:
        output += f'\n{msg_after}'

    return comment_tracking(t, output)


def comment_tracking(t: Tracking, msg: str):
    logging.debug(f'Commenting... {t.address}')

    return t.trigger_message.reply_html(msg, disable_web_page_preview=True)


SLADKO_STICKER = 'CAACAgIAAxkBAAICg17NohlwOlknBV-TxEbYU8IMoSfVAAIGAAOGXKIDKjC8KNx8UxsZBA'
SESH_STICKER = 'CAACAgIAAxkBAAIEg17P_rvF-pD4ixwmI3jz4v9r5Zt4AAItAAOGXKIDVO8mIP8BqqAZBA'
'CAACAgIAAxkBAAIEqF7QDLxFpRZ6m0a2nZn9Q7-N2pXhAAItAAOGXKIDVO8mIP8BqqAZBA'


def send_sladko(bot: Bot, chat_id):
    bot.send_sticker(chat_id, SLADKO_STICKER)


def send_sesh(bot: Bot, chat_id):
    bot.send_sticker(chat_id, SESH_STICKER)
