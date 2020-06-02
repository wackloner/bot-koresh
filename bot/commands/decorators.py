import logging
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

from bot.context import App
from bot.settings import SLADKO_EVERY_NTH_MESSAGE
from messages import send_sladko
from utils.callback_context_utils import increase_messages_count


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


RETRIES = 2


def moshnar_command(command_handler):
    @wraps(command_handler)
    def wrapper(*args, **kwargs):
        update: Update = args[0]
        context: CallbackContext = args[1]

        logging.debug(f"Handling: '{update.message.text}'")

        for i in range(RETRIES + 1):
            try:
                res = command_handler(update, context)
                msg_cnt = increase_messages_count(context)
                if msg_cnt % SLADKO_EVERY_NTH_MESSAGE == 0:
                    send_sladko(App.app_context.bot, update.message.chat.id)

                logging.debug(f'Done, msg_cnt = {msg_cnt}')

                return res
            except Exception as e:
                logging.error(e)

        # TODO: log execution time

    return wrapper
