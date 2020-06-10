import logging
from datetime import timedelta
from time import time

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, CallbackQueryHandler

from bot.commands.button_handler import button_handler
from bot.commands.decorators import send_action, moshnar_command
from bot.context import app_context

DEFAULT_DURATION = timedelta(seconds=60)


button_msg = {}


def stop_challenge_f(chat_id: int, message_id: int):
    def f(context: CallbackContext):
        context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'GG')

    return f


@send_action(ChatAction.TYPING)
@moshnar_command
def challenge(update: Update, context: CallbackContext):
    try:
        duration = DEFAULT_DURATION
        if not context.args == []:
            try:
                duration = int(context.args[0])
            except Exception:
                pass

        challenge_id = context.chat_data.get('challenges_count', 0)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('ЖМЯК', callback_data=challenge_id)]])
        button_message = context.bot.send_message(update.message.chat.id, f'Время по-нажимать)) ({duration}s)', reply_markup=reply_markup)

        if 'challenge_msg' not in context.chat_data:
            context.chat_data['challenge_msg'] = {}
        context.chat_data['challenge_msg'][challenge_id] = button_message.message_id

        if 'challenge_start' not in context.chat_data:
            context.chat_data['challenge_start'] = {}

        context.chat_data['challenge_start'][challenge_id] = time()

        context.chat_data['challenges_count'] = challenge_id + 1

        f = stop_challenge_f(update.message.chat.id, button_message.message_id)
        app_context.job_queue.run_once(f, duration)

    except Exception as e:
        logging.exception(e)


def challenge_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
