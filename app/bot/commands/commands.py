from dataclasses import dataclass
from typing import ClassVar, List

from telegram import ChatAction, Update
from telegram.ext import CallbackContext

from app.bot.commands.show_map import show_map
from app.bot.commands.abstract_command import Command
from app.bot.commands.admin_mode import admin_mode
from app.bot.commands.create_challenge import handle_challenge, challenge_update_dispatcher
from app.bot.commands.translate import translate_handle
from app.utils.classes.decorators import send_action, moshnar_command
from app.bot.commands.show_tracked import show_tracked
from app.bot.commands.split_teams import split_into_teams
from app.bot.commands.start import start
from app.bot.commands.track_address import track_address_handler
from app.bot.commands.troll_mode import troll_mode

from app.managers.phrase_manager import PhraseManager


@send_action(ChatAction.TYPING)
@moshnar_command
def show_help(update: Update, context: CallbackContext):
    msg = f'{PhraseManager.how_are_you()}, {update.message.from_user.first_name})\n'
    msg += '\n'
    msg += 'Вообще я так-то 10/10 бот и выкупаю все команды и без ключевых слов, но на случай если ты вдруг не особо '
    msg += 'просекаешь базары или просто не вывозишь, вот тебе список доступных ключевых команд:\n'
    msg += '\n'
    msg += '\n'.join(list(filter(None, map(lambda cmd: f'/{cmd.name} {cmd.args or ""}- {cmd.help}', Commands.get_all()))))
    update.message.reply_text(msg)


@dataclass
class Commands:
    _all: ClassVar[List[Command]] = [
        Command('start', start),

        Command('track', track_address_handler, help=
                f'попалить, какая последняя транзакция на адресе(-ах), и если она есть и ещё не '
                f'дошла, то пиздец пристально последить за ней и СРАЗУ ЖЕ отписать в чат, когда она дойдёт) Можно '
                f'передать слово random, чтобы последить за рандомным адресом с транзакцией'),

        Command('split_teams', split_into_teams, help=
                f'поделить множество людей на n команд (2 по дефолту)'),

        Command('show_tracked', show_tracked, help='показать все отслеживаемые адреса'),

        Command('show_map', show_map, args='%lat,%long ', help='показать кусок карты по данной локации'),

        Command('troll_mode', troll_mode, args='on/off ', help='тролльмод, становлюсь игривее)'),

        Command('translate', translate_handle, args='%eng_phrase ', help='перевести на русский'),

        Command('challenge', handle_challenge, additional_dispatcher_update=challenge_update_dispatcher, help=
                f'скинуть в чат кнопку "кто быстрее", если вдруг надо что-то серьёзно порешать'),

        Command('admin_mode', admin_mode),

        Command('help', show_help)
    ]

    @classmethod
    def get_all(cls) -> List[Command]:
        return cls._all
