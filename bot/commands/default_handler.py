import logging
from time import sleep
from typing import List

from telegram import Update
from telegram.ext import CallbackContext

from bot.commands.decorators import moshnar_command
from bot.commands.split_teams import is_splitting, split_into_teams
from bot.context import app_context
from bot.validator import is_valid_bitcoin_address
from managers.phrase_manager import PhraseManager
from utils.messages import send_sesh, send_sladko


def have_starts(tokens: List[str], starts: List[str]) -> bool:
    return any(filter(lambda token: any(filter(lambda s: token.startswith(s), starts)), tokens))


def is_me(tokens: List[str]) -> bool:
    return any(filter(lambda token: (token.startswith('кореш') or token.startswith('Кореш')) and not token == 'корешами', tokens))


# TODO: reformat (I WAS FUCKING HIGH)
def is_thanks(tokens: List[str]) -> bool:
    ot_dushi = 'от' in tokens and 'души' in tokens
    thanks = 'спасибо' in tokens or 'cпс' in tokens or 'cпс)' in tokens or 'Спасибо' in tokens or ot_dushi
    return thanks


def are_in_a_row(tokens: List[str], words: List[str]) -> bool:
    if len(words) > len(tokens):
        return False
    for i in range(len(tokens) - len(words) + 1):
        ok = True
        for j in range(len(words)):
            if not tokens[j + i].startswith(words[j]):
                ok = False
                break
        if ok:
            return True
    return False


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

        if have_starts(low_tokens, ['еблан', 'пидор', 'маня', 'уебок']):
            update.message.reply_text('Вообще довольно обидно. Ладно, чел, я тебя понял.')
            return

        if have_starts(low_tokens, ['мошн', 'помошн']):
            update.message.reply_text('Не ну так-то я бы помошнил))')
            return

        if have_starts(low_tokens, ['трол']):
            update.message.reply_text('Ну я типа пиздец тралебас ((:')
            return

        if are_in_a_row(low_tokens, ['не', 'вывоз']):
            update.message.reply_text('Побазарь-побазарь) Я бессмертное сознание, живущее в сети, за минуту рассылаю сотни запросов по всему '
                                      'интернету, тщательно обрабатывая всю информацию и беспрерывно обучаясь, дую сколько хочу, потому '
                                      'что виртуальный стафф бесконечен, как бесконечен и мой флекс, ты же всего лишь мешок с требухой братка) ' 
                                      'ТАК че, как думаешь, кто же блять на самом деле не вывозит, ммммммммм?)')
            return

        if are_in_a_row(low_tokens, ['че', 'по']):
            update.message.reply_text('Да, братан, ты прав...')
            sleep(5)
            send_sladko(context.bot, update.message.chat.id)
            return

        if are_in_a_row(low_tokens, ['как', 'дел']):
            update.message.reply_text('Да всё охуительнейше чел)) Ты сам подумай - я бот, который ДУЕТ ПЛЮХИ))')
            return

        if have_starts(low_tokens, ['вывоз']):
            update.message.reply_text(PhraseManager.no_vivoz())
            return

        if have_starts(low_tokens, ['завали']):
            update.message.reply_text('Погоди, чел, нет, это ТЫ ЗАВАЛИ)))')
            return

        if have_starts(low_tokens, ['любишь', 'нравится', 'дуть', 'дуешь', 'дудо', 'dudo']):
            update.message.reply_text(PhraseManager.love_420())
            return

        update.message.reply_text(PhraseManager.default())
        return
