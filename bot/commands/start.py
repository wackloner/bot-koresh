import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from utils.classes.decorators import send_action, moshnar_command
from managers.phrase_manager import PhraseManager


@send_action(ChatAction.TYPING)
@moshnar_command
def start(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(PhraseManager.greet())
    except Exception as ex:
        logging.exception(ex)
