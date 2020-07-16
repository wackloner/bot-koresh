import logging

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Dispatcher, CallbackQueryHandler, CommandHandler

from bot.commands.button_handler import button_handler
from utils.classes.decorators import send_action, moshnar_command
from bot.context import app_context
from managers.phrase_manager import PhraseManager


@send_action(ChatAction.TYPING)
@moshnar_command
def show_tracked(update: Update, context: CallbackContext):
    try:
        if not context.args == [] and context.args[0] == 'fucking_all':
            tracked = app_context.tracking_manager.trackings
        else:
            tracked = app_context.tracking_manager.get_by_chat_id(update.message.chat_id)
        if tracked == []:
            update.message.reply_html(PhraseManager.nothing_to_do())
            return

        keyboard = [[InlineKeyboardButton(t.address, callback_data=t.address)] for t in tracked]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Да вот попаливаю чета:', reply_markup=reply_markup)
    except Exception as e:
        logging.exception(e)


def show_tracked_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
