from dataclasses import dataclass
from typing import ClassVar, List

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from bot.commands.abstract_command import Command
from bot.commands.decorators import send_action, moshnar_command
from bot.commands.show_tracked import show_tracked, show_tracked_update_dispatcher
from bot.commands.split_teams import split_into_teams
from bot.commands.start import start
from bot.commands.trackings import track_address, track_random_address

from managers.phrase_manager import PhraseManager


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

        Command('track_random', track_random_address),

        Command('split_teams', split_into_teams, help=
                f'/split_teams - поделить множество людей на n команд (2 по дефолту)'),

        Command('show_tracked', show_tracked, _update_dispatcher=show_tracked_update_dispatcher, help=
                f'/show_tracked - показать все отслеживаемые адреса'),

        Command('help', show_help)
    ]

    @classmethod
    def get_all(cls) -> List[Command]:
        return cls._all

    @classmethod
    def register(cls, command: Command) -> None:
        cls._all.append(command)
