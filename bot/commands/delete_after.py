import logging
from typing import Optional

from telegram.ext import CallbackContext


def delete_after_f(chat_id: int, message_id: int):
    def delete_after(context: CallbackContext):
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return delete_after


def parse_time(token: str) -> Optional[int]:
    if len(token) == 0 or token[0] != '$':
        return None

    logging.debug(token)

    token = token[1:]
    name = token[-1]
    num_str = token[:-1]

    logging.debug(f'name = {name}, num_str = {num_str}')

    try:
        num = int(num_str)
    except Exception:
        return None

    res = None

    if name == 's':
        res = num

    if name == 'm':
        res = num * 60

    if name == 'h':
        res = num * 60 * 60

    if name == 'd':
        res = num * 60 * 60 * 24

    logging.debug(f'delete_after_s = {res}')

    return res
