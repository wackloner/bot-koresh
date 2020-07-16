import logging
from datetime import timedelta, datetime
from typing import Optional

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, CallbackQueryHandler

from bot.commands.button_handler import button_handler
from utils.classes.decorators import send_action, moshnar_command
from bot.context import app_context
from model.challenge import Challenge
from utils.callback_context_utils import get_chat_data
from utils.str_utils import CONF_EMOJI, UNCONF_EMOJI, SUNGLASSES_EMOJI


DEFAULT_DURATION = timedelta(minutes=10)
CHALLENGE_UPDATING_INTERVAL_SEC = 10
CHALLENGE_UPDATING_INTERVAL = timedelta(seconds=CHALLENGE_UPDATING_INTERVAL_SEC)


jobs = {}


def update_challenge_f(challenge_id: int):
    def f(context: CallbackContext):
        global jobs

        try:
            job = context.job

            challenges = job.context['challenges']
            challenge = challenges.get(challenge_id)
            if challenge is None:
                logging.error(f'Challenge {challenge_id} does not exist')
                return

            passed = datetime.now() - challenge.started_at

            if passed > challenge.duration:
                if challenge_id not in jobs:
                    logging.error(f'{challenge_id} challenge job was not cancelled')
                    return

                jobs[challenge_id].schedule_removal()
                del jobs[challenge_id]
                logging.debug(f'{challenge_id} challenge job was scheduled for removal')

            challenge.post_update(app_context.bot)
        except Exception as e:
            logging.exception(e)

    return f


@send_action(ChatAction.TYPING)
@moshnar_command
def handle_challenge(update: Update, context: CallbackContext):
    return create_challenge(update, context)


def get_challenge_reply_markup(challenge_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f'{CONF_EMOJI}ЖМЯК', callback_data=f'add {challenge_id}')],
        [InlineKeyboardButton(f'{UNCONF_EMOJI}Убрать', callback_data=f'remove {challenge_id}')]
    ])


def parse_challenge_text(text: str, duration: timedelta) -> Optional[str]:
        text = text.replace('/challenge', '').strip()
        if duration != DEFAULT_DURATION:
            text = text.replace(str(duration.seconds), '').strip()
        return text if not text == '' else None


def create_challenge(update: Update, context: CallbackContext):
    global jobs

    try:
        # TODO: refactor
        duration = DEFAULT_DURATION
        if not context.args == []:
            try:
                duration = timedelta(seconds=int(context.args[0]))
            except Exception:
                pass

        challenge_text = f'Время по-нажимать{SUNGLASSES_EMOJI}'
        if len(context.args) > 1:
            parsed_text = parse_challenge_text(update.message.text, duration)
            if parsed_text is not None:
                challenge_text = parsed_text

        challenge_id = context.chat_data.get('challenges_count', 0)
        button_message = context.bot.send_message(update.message.chat.id, 'кто прочитал, тот пидор')

        new_challenge = Challenge(
            id=challenge_id,
            msg_id=button_message.message_id,
            chat_id=update.message.chat.id,
            author=update.message.from_user.username,
            duration=duration,
            text=challenge_text,
            started_at=datetime.now()
        )

        new_challenge.post_update(context.bot)
        context.chat_data['challenges_count'] = challenge_id + 1
        get_chat_data(context, 'challenges', {})[challenge_id] = new_challenge

        # TODO: one thread to update all challenges
        f = update_challenge_f(challenge_id)

        job = app_context.job_queue.run_repeating(f, CHALLENGE_UPDATING_INTERVAL,
                                                  context={'challenges': get_chat_data(context, 'challenges', {})})
        jobs[challenge_id] = job

    except Exception as e:
        logging.exception(e)


def challenge_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
