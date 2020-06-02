import logging

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from bot.commands.decorators import send_action, moshnar_command
from managers.phrase_manager import PhraseManager


@send_action(ChatAction.TYPING)
@moshnar_command
def start(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(PhraseManager.greet())
    except Exception as ex:
        logging.error(ex)


@send_action(ChatAction.TYPING)
@moshnar_command
def show_help(update: Update, context: CallbackContext):
    msg = f'{PhraseManager.how_are_you()}, {update.message.from_user.first_name})\n' \
          f'/track __address__ [addresses] - посмотреть, какая последняя транзакция на адресе, и если она ещё не,' \
          f'дошла, то пиздец пристально последить и сразу же отписать в чат, когда дойдёт)\n' \
          f'но ваще я прост ОБОЖАЮ палить че по, поэтому триггерюсь сам просто по мрази)' \
          f'/show_trackings - показать все отслеживаемые адреса\n' \
          f'/split_teams - поделить множество людей на n команд (2 по дефолту) ' \
          f'Можно и без специальной команды, просто вежливо попросить (:'
    update.message.reply_text(msg)
