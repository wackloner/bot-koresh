import logging
from datetime import timedelta, datetime
from time import time

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, CallbackQueryHandler

from bot.commands.button_handler import button_handler
from bot.commands.decorators import send_action, moshnar_command
from bot.context import app_context
from utils.str_utils import timedelta_to_str

DEFAULT_DURATION = timedelta(seconds=60)

CHALLENGE_UPDATING_INTERVAL = timedelta(seconds=4)


jobs = {}


def update_challenge_f(chat_id: int, message_id: int, challenge_id: int, text: str, markup: InlineKeyboardMarkup, started_at: datetime, duration: timedelta):
    def f(context: CallbackContext):
        global jobs

        passed = datetime.now() - started_at

        if passed < duration:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'{text}\n\n<i>Осталось {timedelta_to_str(duration - passed)}...</i>',
                parse_mode=ParseMode.HTML,
                reply_markup=markup
            )
        else:
            if challenge_id not in jobs:
                logging.error(f'{challenge_id} challenge job was not cancelled')
                return

            context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='GG')
            jobs[challenge_id].schedule_removal()
            del jobs[challenge_id]
            logging.debug(f'{challenge_id} challenge job was scheduled for removal')

    return f


@send_action(ChatAction.TYPING)
@moshnar_command
def challenge(update: Update, context: CallbackContext):
    return create_challenge(update, context)


def create_challenge(update: Update, context: CallbackContext):
    global jobs

    try:
        duration = DEFAULT_DURATION
        if not context.args == []:
            try:
                duration = timedelta(seconds=int(context.args[0]))
            except Exception:
                pass

        msg = 'Время по-нажимать))'
        if len(context.args) > 1:
            msg = update.message.text.replace('/challenge', '').strip()
            if duration != DEFAULT_DURATION:
                msg = msg.replace(context.args[0], '').strip()

        challenge_id = context.chat_data.get('challenges_count', 0)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('ЖМЯК', callback_data=challenge_id)]])
        button_message = context.bot.send_message(
            update.message.chat.id,
            f'{msg}\n\n<i>Осталось {timedelta_to_str(duration)}...</i>',
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

        started_at = datetime.now()

        if 'challenge_msg' not in context.chat_data:
            context.chat_data['challenge_msg'] = {}
        context.chat_data['challenge_msg'][challenge_id] = button_message.message_id

        if 'challenge_start' not in context.chat_data:
            context.chat_data['challenge_start'] = {}

        context.chat_data['challenge_start'][challenge_id] = time()

        context.chat_data['challenges_count'] = challenge_id + 1

        # TODO: one thread to update all challenges
        f = update_challenge_f(update.message.chat.id, button_message.message_id, challenge_id, msg, reply_markup, started_at, duration)

        job = app_context.job_queue.run_repeating(f, CHALLENGE_UPDATING_INTERVAL)
        jobs[challenge_id] = job

    except Exception as e:
        logging.exception(e)


def challenge_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
