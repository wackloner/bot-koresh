from dataclasses import dataclass
from typing import ClassVar, List

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from bot.commands.show_map import show_map
from koresh.bot.commands.abstract_command import Command
from koresh.bot.commands.admin_mode import admin_mode
from koresh.bot.commands.create_challenge import handle_challenge, challenge_update_dispatcher
from koresh.bot.commands.translate import translate_handle
from koresh.utils.classes.decorators import send_action, moshnar_command
from koresh.bot.commands.show_tracked import show_tracked
from koresh.bot.commands.split_teams import split_into_teams
from koresh.bot.commands.start import start
from koresh.bot.commands.track_address import track_address
from koresh.bot.commands.troll_mode import troll_mode

from koresh.managers.phrase_manager import PhraseManager


@send_action(ChatAction.TYPING)
@moshnar_command
def show_help(update: Update, context: CallbackContext):
    msg = f'{PhraseManager.how_are_you()}, {update.message.from_user.first_name})\n'
    msg += '\n'
    msg += 'Вообще я так-то 10/10 бот и выкупаю все команды и без ключевых слов, но на случай если ты вдруг не особо '
    msg += 'просекаешь базары или просто не вывозишь, вот тебе список доступных ключевых команд:\n'
    msg += '\n'
    msg += '\n'.join(list(filter(None, map(lambda cmd: cmd.help, Commands.get_all()))))
    update.message.reply_text(msg)


# TODO: naming
@dataclass
class Commands:
    _all: ClassVar[List[Command]] = [
        Command('start', start),

        # TODO: change to check + button for tracking
        Command('track', track_address, help=
                f'/track - попалить, '
                f'какая последняя транзакция на адресе(-ах), и если она есть и ещё не '
                f'дошла, то пиздец пристально последить за ней и СРАЗУ ЖЕ отписать в чат, когда она дойдёт) Можно '
                f'передать слово random, чтобы последить за рандомным адресом с транзакцией'),

        Command('split_teams', split_into_teams, help=
                f'/split_teams - поделить множество людей на n команд (2 по дефолту)'),

        Command('show_tracked', show_tracked, help=
                f'/show_tracked - показать все отслеживаемые адреса'),

        # TODO: don't write name in help (add it in Command init)
        Command('show_map', show_map, help=
                f'/show_map - показать кусок карты по данной локации'),

        Command('troll_mode', troll_mode, help=
                f'/troll_mode on/off - тролльмод'),

        Command('admin_mode', admin_mode),

        Command('translate', translate_handle),

        Command('challenge', handle_challenge, additional_dispatcher_update=challenge_update_dispatcher, help=
                f'/challenge - скинуть в чат кнопку "кто быстрее", если вдруг надо что-то серьёзно порешать'),

        Command('help', show_help)
    ]

    @classmethod
    def get_all(cls) -> List[Command]:
        return cls._all
