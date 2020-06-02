import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from bot.commands.decorators import send_action, moshnar_command
from bot.context import App


@send_action(ChatAction.TYPING)
@moshnar_command
def track_address(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            update.message.reply_text(f'Анус себе потрекай братишка))')
            return

        for address in args:
            t = App.app_context.tracking_manager.start_tracking(address, update.message, context)
            logging.debug(f'New tracking: {t}')
    except Exception as e:
        logging.error(e)


@send_action(ChatAction.TYPING)
@moshnar_command
def track_random_address(update: Update, context: CallbackContext):
    try:
        address = App.app_context.blockchain_client.get_random_address_with_unconfirmed_tx()
        logging.info(f'addr = {address}')
        t = App.app_context.tracking_manager.start_tracking(address, update.message, context)
        logging.debug(f'New random tracking: {t}')
    except Exception as e:
        logging.error(e)


# TODO: implement
@moshnar_command
def stop_tracking(update: Update, context: CallbackContext):
    pass
