import logging
from time import sleep
from typing import List

from telegram import Update, Message
from telegram.ext import CallbackContext

from bot.commands.decorators import moshnar_command
from bot.commands.split_teams import split_into_teams
from bot.context import app_context
from bot.settings import TROLL_MODE
from bot.validator import is_valid_bitcoin_address
from managers.phrase_manager import PhraseManager
from utils.messages import send_sesh, send_sladko


# TODO: make parse_utils or Parser

def have_start_in_list(tokens: List[str], starts: List[str]) -> bool:
    return any(filter(lambda token: any(filter(lambda s: token.startswith(s), starts)), tokens))


def have_starts(tokens: List[str], *args):
    return have_start_in_list(tokens, [arg for arg in args])


def has_mention_of_me(tokens: List[str]) -> bool:
    return have_start_in_list(tokens, ['кореш', 'корефан']) and not have_start_in_list(tokens, ['корешами'])


def is_reply_to_me(message: Message):
    try:
        return message.reply_to_message.from_user.id == app_context.bot.id
    except Exception:
        return False


def is_thanks(tokens: List[str]) -> bool:
    return are_in_a_row(tokens, ['от', 'души']) or have_start_in_list(tokens, ['спс', 'сяп', 'спасиб', 'сенкс'])


def are_in_a_row(tokens: List[str], words: List[str]) -> bool:
    if len(words) > len(tokens):
        return False

    # TODO: optimize
    for i in range(len(tokens) - len(words) + 1):
        ok = True
        for j in range(len(words)):
            if not tokens[j + i].startswith(words[j]):
                ok = False
                break
        if ok:
            return True
    return False


def is_split_request(tokens: List[str]) -> bool:
    return have_start_in_list(tokens, ['подели', 'намошни', 'раздели', 'посплить']) and \
           have_start_in_list(tokens, ['плиз', 'плз', 'плез', 'пож', 'по-братски'])


@moshnar_command
def default_message_handler(update: Update, context: CallbackContext):
    logging.debug('default handler')

    # TODO: count sladkos and send one after 2

    text = update.message.text
    tokens = text.split() if text is not None else []
    low_tokens = text.lower().split() if text is not None else []

    # TODO: reformat for easy creating of new situations/cases
    for s in tokens:
        try:
            if is_valid_bitcoin_address(s):
                app_context.tracking_manager.create_tracking(s, update.message)
            return
        except Exception as e:
            pass
            # logging.error(e)

    if is_split_request(low_tokens):
        split_into_teams(update, context)
        return

    if have_start_in_list(low_tokens, ['cеш']):
        send_sesh(app_context.bot, update.message.chat.id)
        return

    if TROLL_MODE:
        # checking only the last token for a rhyme
        if have_starts(low_tokens[-1:], 'кардиган', 'карди-ган'):
            update.message.reply_text(PhraseManager.kardigun_rhyme())
            return

        if have_starts(low_tokens, 'кардыч', 'перди') or have_starts(low_tokens, 'кардич', 'перди'):
            update.message.reply_text('Снова в сперме😌')
            return

    if has_mention_of_me(low_tokens):
        low_tokens = list(filter(lambda token: not token.startswith('кореш') and not token.startswith('корефан'), low_tokens))
        logging.info(low_tokens)
    elif not is_reply_to_me(update.message):
        # ignoring the message if it's not for me
        return

    if not low_tokens:
        # message was only my name
        update.message.reply_text('Че)')
        return

    if is_thanks(text):
        update.message.reply_text(PhraseManager.thanks())
        return

    if have_starts(low_tokens, 'еблан', 'пидор', 'маня', 'уебок'):
        # TODO: filter possible negation
        update.message.reply_text('Вообще довольно обидно. Ладно, чел, я тебя понял.')
        return

    if have_starts(low_tokens, 'лалыч', 'пету', 'долба', 'долбо'):
        update.message.reply_text('>tfw ты такой лошок, что отыгрываешься на боте))')
        return

    if have_starts(low_tokens, 'мошн', 'помошн'):
        update.message.reply_text('Не ну так-то я бы помошнил))')
        return

    if have_starts(low_tokens, 'трол'):
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

    if have_starts(low_tokens, 'вывоз'):
        update.message.reply_text(PhraseManager.no_vivoz())
        return

    if have_starts(low_tokens, 'завали'):
        update.message.reply_text('Погоди, чел, нет, это ТЫ ЗАВАЛИ)))')
        return

    if have_starts(low_tokens, 'любишь', 'нравится', 'дуть', 'дуешь', 'дудо', 'dudo'):
        update.message.reply_text(PhraseManager.love_420())
        return

    if have_starts(low_tokens, 'красав', 'молодец', 'вп', 'wp', 'малаца'):
        update.message.reply_text('Блин, так-то прям от души в душу душевненько) Спс')
        return

    update.message.reply_text(PhraseManager.default())
