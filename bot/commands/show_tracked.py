import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from model.tracking import AddressStatus
from utils.classes.decorators import send_action, moshnar_command
from bot.context import app_context
from managers.phrase_manager import PhraseManager
from utils.message_utils import send_tx_info


@send_action(ChatAction.TYPING)
@moshnar_command
def show_tracked(update: Update, context: CallbackContext):
    try:
        if context.args and context.args[0] == 'fucking_all':
            tracked = app_context.tracking_manager.get_all()
        else:
            tracked = app_context.tracking_manager.get_by_chat_id(update.message.chat.id)

        if not tracked:
            update.message.reply_html(PhraseManager.nothing_to_do())
            return

        for t in tracked:
            app_context.tracking_manager.update_tracking(t)
            send_tx_info(t)
            if t.status == AddressStatus.CONFIRMED:
                if app_context.tracking_manager.remove_tracking(t):
                    logging.debug(f'Address {t.address} was removed.')
                else:
                    logging.debug(f'Failed to remove address {t.address}.')

    except Exception as e:
        logging.exception(e)
