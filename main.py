import atexit
import logging

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from bot.commands.default_handler import default_message_handler
from bot.commands.split_teams import split_into_teams
from bot.commands.start_help import start, show_help
from bot.commands.trackings import track_address, track_random_address, show_trackings, stop_tracking, address_button
from bot.context import Context, App


# TODO: separate class
def run():
    context = Context()
    App.set_context(context)

    updater = context.updater
    dp = updater.dispatcher

    # TODO: naming
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', show_help))
    dp.add_handler(CommandHandler('track', track_address))
    dp.add_handler(CommandHandler('track_random', track_random_address))
    dp.add_handler(CommandHandler('show_trackings', show_trackings))
    dp.add_handler(CommandHandler('stop_tracking', stop_tracking))
    dp.add_handler(CommandHandler('split_teams', split_into_teams))
    dp.add_handler(CallbackQueryHandler(address_button))
    dp.add_handler(MessageHandler(Filters.all, default_message_handler))

    updater.start_polling()

    logging.info('Bot started!')

    updater.idle()


def tear_down():
    logging.info('EXIT BOT')


if __name__ == '__main__':
    atexit.register(tear_down)

    try:
        run()
    except Exception as ex:
        logging.error(ex)
