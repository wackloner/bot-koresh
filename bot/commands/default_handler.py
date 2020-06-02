import logging
from typing import List

from telegram import Update
from telegram.ext import CallbackContext

from bot.commands.decorators import moshnar_command
from bot.commands.split_teams import is_splitting, split_into_teams
from bot.context import app_context
from bot.validator import is_valid_bitcoin_address
from managers.phrase_manager import PhraseManager
from utils.messages import send_sesh


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
        send_sesh(app_context.bot, update.message.chat.id)
        return

    for s in tokens:
        try:
            if is_valid_bitcoin_address(s):
                app_context.tracking_manager.start_tracking(s, update.message)
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
