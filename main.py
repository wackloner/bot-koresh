import logging
from time import sleep
from typing import List

from telegram import Update, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

from bot.commands.decorators import send_action, moshnar_command
from bot.commands.split_teams import is_splitting, split_into_teams
from managers.blockchain_utils import get_random_address_with_unconfirmed_tx
from utils.callback_context_utils import get_addresses_for_chat, increase_messages_count
from bot.context import Context, App
from messages import send_sladko, send_sesh, send_message
from managers.phrase_manager import PhraseManager


from utils.str_utils import tx_info_to_str
from bot.validator import is_valid_bitcoin_address


@send_action(ChatAction.TYPING)
@moshnar_command
def start(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(PhraseManager.greet())
    except Exception as e:
        logging.error(e)


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


@send_action(ChatAction.TYPING)
@moshnar_command
def track_address(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text(f'Анус себе потрекай братишка))')
        return

    for address in args:
        t = App.app_context.tracking_manager.start_tracking(address, update.message, context)
        logging.debug(f'New tracking: {t}')


@send_action(ChatAction.TYPING)
@moshnar_command
def track_random_address(update: Update, context: CallbackContext):
    address = get_random_address_with_unconfirmed_tx()
    t = App.app_context.tracking_manager.start_tracking(address, update.message, context)
    logging.debug(f'New random tracking: {t}')


# TODO: implement
@moshnar_command
def stop_tracking(update: Update, context: CallbackContext):
    pass


# TODO: button show additional info
# TODO: show tracked info (separate command)
@send_action(ChatAction.TYPING)
@moshnar_command
def show_trackings(update: Update, context: CallbackContext):
    tracked = get_addresses_for_chat(context)

    if tracked == []:
        update.message.reply_html(PhraseManager.nothing_to_do())
        return

    for address in tracked:
        logging.debug(address)
    keyboard = [[InlineKeyboardButton(address, callback_data=address)] for address in tracked]
    logging.debug(keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Да вот попаливаю чета:', reply_markup=reply_markup)


def address_button(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()
    address = query.data

    tracking = App.app_context.tracking_manager.get_tracking_by_address(address)

    if tracking is None:
        logging.error('ERROR')
        return

    query.edit_message_text(f'{query.message.text}\n{tx_info_to_str(tracking.last_tx_info)}', parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def have_starts(tokens: List[str], starts: List[str]) -> bool:
    return any(filter(lambda token: any(filter(lambda s: token.startswith(s), starts)), tokens))


def is_me(tokens: List[str]) -> bool:
    return any(filter(lambda token: (token.startswith('кореш') or token.startswith('Кореш')) and not token == 'корешами', tokens))


# TODO: reformat (I WAS FUCKING HIGH)
def is_thanks(tokens: List[str]) -> bool:
    ot_dushi = 'от' in tokens and 'души' in tokens
    thanks = 'спасибо' in tokens or 'cпс' in tokens or 'cпс)' in tokens or 'Спасибо' in tokens or ot_dushi
    return thanks


@moshnar_command
def default_message_handler(update: Update, context: CallbackContext):
    logging.debug('default handler')

    text = update.message.text

    if is_splitting(text):
        split_into_teams(update, context)
        return

    tokens = text.split()
    low_tokens = text.lower().split()

    if any(filter(lambda token: token.startswith('сеш'), low_tokens)):
        send_sesh(App.app_context.bot, update.message.chat.id)
        return

    for s in tokens:
        try:
            if is_valid_bitcoin_address(s):
                App.app_context.tracking_manager.start_tracking(s, update.message, context)
            return
        except Exception as e:
            pass
            # logging.error(e)

    if low_tokens[-1].startswith('кардиган') or low_tokens[-1].startswith('карди-ган'):
        update.message.reply_text(PhraseManager.kardigun_rhyme())
        return

    if is_me(low_tokens):
        if is_thanks(text):
            update.message.reply_text(PhraseManager.thanks())
            return

        if have_starts(low_tokens, ['еблан', 'пидор', 'маня']):
            update.message.reply_text('Да сорри, я прост чиллил(')
            return

        if have_starts(low_tokens, ['мошн', 'помошн']):
            update.message.reply_text('Не ну так-то я бы помошнил))')
            return

        if have_starts(low_tokens, ['любишь', 'нравится', 'дуть', 'дуешь', 'дудо', 'dudo']):
            update.message.reply_text(PhraseManager.love_420())
            return

        update.message.reply_text(PhraseManager.ans())
        return


def run():
    context = Context()
    App.set_context(context)

    updater = context.updater
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', show_help))
    dp.add_handler(CommandHandler('track', track_address))
    dp.add_handler(CommandHandler('track_random', track_random_address))
    dp.add_handler(CommandHandler('show_trackings', show_trackings))
    dp.add_handler(CommandHandler('stop_tracking', stop_tracking))
    dp.add_handler(CommandHandler('split_teams', split_into_teams))
    dp.add_handler(CallbackQueryHandler(address_button))
    dp.add_handler(MessageHandler(Filters.all, default_message_handler))

    updater.start_polling()

    logging.info('Bot started!')

    updater.idle()


if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception as e:
            logging.error(e)

        sleep(1)
