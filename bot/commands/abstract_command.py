from dataclasses import dataclass
from typing import Callable, Optional

from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext


def default_update_dispatcher(command: 'Command', dp: Dispatcher) -> None:
    dp.add_handler(CommandHandler(command.name, command.handler))


@dataclass
class Command:
    name: str
    handler: Callable[[Update, CallbackContext], None]
    help: Optional[str] = None

    _update_dispatcher: Callable[['Command', Dispatcher], None] = default_update_dispatcher

    def update_dispatcher(self, dp: Dispatcher):
        self._update_dispatcher(self, dp)
