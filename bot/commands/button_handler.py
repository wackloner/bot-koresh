import logging

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from bot.context import app_context
from utils.str_utils import tx_info_to_str


def button_handler(update: Update, context: CallbackContext):
    try:
        query = update.callback_query

        query.answer()
        address = query.data

        if address == 'ЖМЯК':
            update.callback_query.edit_message_text(f'Ии первым был @{query.from_user.username} (:')
            return

        tracking = app_context.tracking_manager.get_tracking_by_address(address)

        if tracking is None:
            logging.error('SHIT ERROR')
            return

        query.edit_message_text(
            f'{query.message.text}\n{tx_info_to_str(app_context.blockchain_client.get_last_tx_info(tracking.address))}',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    except Exception as e:
        logging.exception(e)

