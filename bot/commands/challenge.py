import logging

from telegram import ChatAction, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Dispatcher, CommandHandler, CallbackQueryHandler

from bot.commands.button_handler import button_handler
from bot.commands.decorators import send_action, moshnar_command


@send_action(ChatAction.TYPING)
@moshnar_command
def challenge(update: Update, context: CallbackContext):
    try:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('ЖМЯК', callback_data='ЖМЯК')]])
        update.message.reply_text('Кто же первый?...', reply_markup=reply_markup)

    except Exception as e:
        logging.exception(e)


def challenge_update_dispatcher(command: 'Command', dp: Dispatcher):
    dp.add_handler(CommandHandler(command.name, command.handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
