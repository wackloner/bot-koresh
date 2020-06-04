import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from bot.commands.decorators import send_action, moshnar_command
from bot.context import app_context
from bot.settings import ADMIN_CHAT_ID


@send_action(ChatAction.TYPING)
@moshnar_command
def track_address(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            update.message.reply_text(f'Анус себе потрекай братишка))')
            return

        for address in args:
            if address == 'random':
                address = app_context.blockchain_client.get_random_address_with_unconfirmed_tx()

            status = app_context.tracking_manager.create_tracking(address, update.message)

            if status.in_progress():
                app_context.bot.send_message(ADMIN_CHAT_ID, f'New tracking from user {update.message.from_user.username}: {address}')

    except Exception as e:
        logging.exception(e)


# TODO: move to main track command with args
@send_action(ChatAction.TYPING)
@moshnar_command
def track_random_address(update: Update, context: CallbackContext):
    try:
        address = app_context.blockchain_client.get_random_address_with_unconfirmed_tx()
        status = app_context.tracking_manager.create_tracking(address, update.message)

        if status.in_progress():
            app_context.bot.send_message(ADMIN_CHAT_ID, f'new tracking from user {update.message.from_user.username}: {address}')
    except Exception as e:
        logging.exception(e)
