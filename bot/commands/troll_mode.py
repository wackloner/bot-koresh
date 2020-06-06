from time import sleep

from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from bot.commands.decorators import send_action, moshnar_command
from bot.settings import Settings


@send_action(ChatAction.TYPING)
@moshnar_command
def troll_mode(update: Update, context: CallbackContext):
    if context.args == []:
        if Settings.troll_mode:
            update.message.reply_text('Бля ну и че) Ты вообще вывозишь?)')
        else:
            update.message.reply_text('Нужно ещё передать on/off)')
        return

    token = str(context.args[0]).lower()
    if token == 'off':
        troll_mode_off(update, context)
    elif token == 'on':
        troll_mode_on(update, context)
    else:
        if Settings.troll_mode:
            update.message.reply_text('on/off, `ёбобо))')
        else:
            update.message.reply_text('Нужно ещё передать on/off')


def troll_mode_on(update: Update, context: CallbackContext):
    # TODO: set in chat_data
    if Settings.troll_mode:
        update.message.reply_text('Ты че диб)) Я и так траллирую всех пздц)')
        return

    Settings.troll_mode = True
    update.message.reply_text('Время подор-вать')
    sleep(3)
    update.message.reply_text('Петушкам пердачки)))')
    # sleep(3)
    # context.bot.send_sticker(update.message.chat.id, 'AAMCAQADGQEAAgh5Xtqqo3sxZnU7py5zEry_lqFJwwcAAlgAAz0LwA3tC7GMLRJb81mg7y8ABAEAB20AA-QGAAIaBA')


def troll_mode_off(update: Update, context: CallbackContext):
    # TODO: set in chat_data
    if not Settings.troll_mode:
        update.message.reply_text('Да я и так никого не троллю...')
        return

    update.message.reply_text('Лан-лан...')
    Settings.troll_mode = False
