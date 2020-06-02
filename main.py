import atexit
import logging

from telegram.ext import MessageHandler, Filters

from bot.commands.commands import Commands
from bot.commands.default_handler import default_message_handler
from bot.context import app_context


# TODO: separate class
def run():
    updater = app_context.updater
    dp = updater.dispatcher

    for command in Commands.get_all():
        command.update_dispatcher(dp)

    # fallback
    dp.add_handler(MessageHandler(Filters.all, default_message_handler))

    updater.start_polling()

    logging.info('Bot started!')


def tear_down():
    logging.info('EXIT BOT')


if __name__ == '__main__':
    atexit.register(tear_down)

    try:
        run()
    except Exception as ex:
        logging.error(ex)
