import logging
from time import time

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from bot.context import app_context
from utils.str_utils import tx_info_to_str


CONNECTION_DELAY = 1.5


def button_handler(update: Update, context: CallbackContext):
    try:
        query = update.callback_query

        query.answer()
        address = query.data

        challenge_id = -1
        try:
            challenge_id = int(address)
        except Exception:
            pass

        if challenge_id != -1:
            try:
                player = f'@{query.from_user.username}'
                logging.debug(f'{player} in A GAME yo')

                # TODO: count number of times pressed
                if 'challenge_result_msg' not in context.chat_data:
                    context.chat_data['challenge_result_msg'] = {}
                if challenge_id not in context.chat_data['challenge_result_msg']:
                    res_msg = context.bot.send_message(context.chat_data['id'], player)
                    context.chat_data['challenge_result_msg'][challenge_id] = res_msg.message_id

                    # TODO: use default dict
                    if 'challenge_results' not in context.chat_data:
                        context.chat_data['challenge_results'] = {}
                    if challenge_id not in context.chat_data['challenge_results']:
                        context.chat_data['challenge_results'][challenge_id] = {}

                if player not in context.chat_data['challenge_results'][challenge_id]:
                    spent = time() - context.chat_data['challenge_start'][challenge_id] - CONNECTION_DELAY
                    context.chat_data['challenge_results'][challenge_id][player] = round(spent, 1)
                    res_msg = context.chat_data['challenge_result_msg'][challenge_id]
                    text = '\n'.join(f'{k} {v}s' for (k, v) in context.chat_data['challenge_results'][challenge_id].items())
                    context.bot.edit_message_text(chat_id=context.chat_data['id'], message_id=res_msg, text=text)

                return

            except Exception as e:
                logging.exception(e)
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

