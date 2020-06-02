import logging

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, Dispatcher, CallbackQueryHandler, CommandHandler

from bot.commands.decorators import send_action, moshnar_command
from bot.context import App
from managers.phrase_manager import PhraseManager
from utils.callback_context_utils import get_addresses_for_chat
from utils.str_utils import tx_info_to_str


@send_action(ChatAction.TYPING)
@moshnar_command
def show_tracked(update: Update, context: CallbackContext):
    try:
        tracked = get_addresses_for_chat(context)
        if tracked == []:
            update.message.reply_html(PhraseManager.nothing_to_do())
            return

        for address in tracked:
            logging.debug(address)
        keyboard = [[InlineKeyboardButton(address, callback_data=address)] for address in tracked]
        logging.debug(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Да вот попаливаю чета:', reply_markup=reply_markup)
    except Exception as e:
        logging.error(e)


def address_button(update: Update, context: CallbackContext):
    try:
        query = update.callback_query

        query.answer()
        address = query.data

        tracking = App.app_context.tracking_manager.get_tracking_by_address(address)

        if tracking is None:
            logging.error('ERROR')
            return

        query.edit_message_text(
            f'{query.message.text}\n{tx_info_to_str(tracking.last_tx_info)}',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(e)


def show_tracked_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(address_button))
