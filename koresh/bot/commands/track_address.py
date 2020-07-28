import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from koresh.utils.classes.decorators import send_action, moshnar_command
from koresh.bot.context import app_context
from koresh.bot.settings import ADMIN_CHAT_ID


@send_action(ChatAction.TYPING)
@moshnar_command
def track_address(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if not args:
            update.message.reply_text(f'Анус себе потрекай братишка))')
            return

        for address in args:
            if address == 'random':
                address = app_context.blockchain_client.get_random_address_with_unconfirmed_tx()

            new_tracking = app_context.tracking_manager.track_address(address, update.message, context.bot)

            if new_tracking:
                app_context.bot.send_message(ADMIN_CHAT_ID, f'New tracking from user {update.message.from_user.username}: {address}')

    except Exception as e:
        logging.exception(e)
