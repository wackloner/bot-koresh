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

        try:
            # TODO: fix bad code smell of using exceptions as conditions
            challenge_id = int(address)
            player = f'@{query.from_user.username}'

            # TODO: add spent duration info
            if 'challenge_result_msg' not in context.chat_data:
                context.chat_data['challenge_result_msg'] = {}
            if challenge_id not in context.chat_data['challenge_result_msg']:
                res_msg = context.bot.send_message(context.chat_data['id'], player)
                context.chat_data['challenge_result_msg'][challenge_id] = res_msg.message_id

                # TODO: use default dict
                if 'challenge_results' not in context.chat_data:
                    context.chat_data['challenge_results'] = {}
                if challenge_id not in context.chat_data['challenge_results']:
                    context.chat_data['challenge_results'][challenge_id] = []

            context.chat_data['challenge_results'].append(player)

            res_msg = context.chat_data['challenge_result_msg'][challenge_id]
            text = '\n'.join(context.chat_data['challenge_results'])
            context.bot.edit_message_text(chat_id=context.chat_data['id'], message_id=res_msg, text=text)

        except Exception:
            pass

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

