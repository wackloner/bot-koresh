import logging
from time import sleep
from typing import List, Optional

from telegram import Update, Message
from telegram.ext import CallbackContext

from bot.commands.challenge import challenge
from bot.commands.decorators import moshnar_command
from bot.commands.delete_after import delete_after_f, parse_time
from bot.commands.split_teams import split_into_teams
from bot.context import app_context
from bot.settings import Settings, MY_CHAT_ID
from bot.validator import is_valid_bitcoin_address
from managers.phrase_manager import PhraseManager
from utils.messages import send_sladko


# TODO: make parse_utils or Parser
from utils.parse_utils import get_alpha_part


def have_start_in_list(tokens: List[str], starts: List[str]) -> bool:
    return any(filter(lambda token: any(filter(lambda s: token.startswith(s), starts)), tokens))


def have_inside_in_list(tokens: List[str], starts: List[str]) -> bool:
    return any(filter(lambda token: any(filter(lambda s: s in token, starts)), tokens))


def have_starts(tokens: List[str], *args):
    return have_start_in_list(tokens, [arg for arg in args])


def have_inside(tokens: List[str], *args):
    return have_inside_in_list(tokens, [arg for arg in args])


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


def is_my_chat(update: Update) -> bool:
    return update.message.chat.id == MY_CHAT_ID


def is_split_request(tokens: List[str]) -> bool:
    return have_start_in_list(tokens, ['подели', 'намошни', 'раздели', 'посплить']) and \
           have_start_in_list(tokens, ['плиз', 'плз', 'плез', 'пож', 'по-братски'])


def is_question(tokens: List[str]) -> bool:
    return '?' in tokens[-1]


def get_delete_after(tokens: List[str]) -> Optional[str]:
    option = list(filter(lambda token: token.startswith('$') and token[-1] in 'smhd', tokens))
    return option[0] if len(option) > 0 else None


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
            alpha_part = get_alpha_part(s)
            if is_valid_bitcoin_address(alpha_part):
                app_context.tracking_manager.create_tracking(alpha_part, update.message)
            return
        except Exception as e:
            pass
            # logging.error(e)

    if is_split_request(low_tokens):
        split_into_teams(update, context)
        return

    delete_after_time = get_delete_after(low_tokens)
    if delete_after_time is not None:
        logging.debug(f'default_handler = {delete_after_time}')

        timer = parse_time(delete_after_time)
        if timer is None:
            update.message.reply_text('Чёт не вышло(')
            return

        app_context.job_queue.run_once(callback=delete_after_f(update.message.chat.id, update.message.message_id), when=timer)
        reply_msg = update.message.reply_text('Организуем-организуем)')

        bot_delay = min(7, timer)
        # delete my msg as well
        app_context.job_queue.run_once(callback=delete_after_f(reply_msg.chat.id, reply_msg.message_id), when=bot_delay)
        return

    if Settings.troll_mode:
        # checking only the last token for a rhyme
        if have_starts(low_tokens[-1:], 'кардиган', 'карди-ган', 'мастер-кардиган'):
            update.message.reply_text(PhraseManager.kardigun_rhyme())
            return

        if are_in_a_row(low_tokens, ['кардыч', 'перди']) or are_in_a_row(low_tokens, ['кардич', 'перди']):
            update.message.reply_text('Снова в сперме😌')
            return

        if are_in_a_row(low_tokens, ['кореш', 'вывоз']):
            update.message.reply_text('Бля ну ты побазарь мне тут ещё про вывоз лалыч))')
            return

        if str(low_tokens[-1]).endswith('да'):
            update.message.reply_text('Пизда))')
            return

        if have_starts(low_tokens, 'принял'):
            update.message.reply_text('На роток ты принял))')
            return

        if str(low_tokens[-1]).endswith('на'):
            update.message.reply_text('Хуй на)))')
            return

        if have_inside(low_tokens, 'ахах', 'aзаз', 'азах', 'ахаз'):
            update.message.reply_text('А ты че угараешь-то, лалыч?))))')
            return

    if are_in_a_row(low_tokens, ['кореш', 'вывоз']):
        update.message.reply_text('Не ну я-то вывожу (:')
        return

    if have_starts(low_tokens, 'мусора'):
        update.message.reply_text('Мусора сосатб(((')
        return

    if has_mention_of_me(low_tokens):
        low_tokens = list(filter(lambda token: not token.startswith('кореш') and not token.startswith('корефан'), low_tokens))
        logging.info(low_tokens)
    elif not (is_reply_to_me(update.message) or is_my_chat(update)):

        if Settings.troll_mode:
            if str(low_tokens[-1]).endswith('))))'):
                update.message.reply_text('Че такой довольный-то, пидорок?))')
                return

            if str(low_tokens[-1]).endswith('(((('):
                update.message.reply_text('Да ты не грусти, всё равно ты не бот и скоро сдохнешь')
                return

        return

    if 'prev_users' not in context.chat_data:
        context.chat_data['prev_users'] = []

    context.chat_data['prev_users'].append(update.message.from_user.id)

    logging.debug(context.chat_data['prev_users'])

    if len(context.chat_data['prev_users']) >= 3:
        if Settings.troll_mode and context.chat_data['prev_users'][0] == context.chat_data['prev_users'][1] and context.chat_data['prev_users'][1] == context.chat_data['prev_users'][2]:
            update.message.reply_text('Че доебался-то)) Челик, ты просто имитация процессора, разве может такая поебота перетроллить БОТА???)))))')
            context.chat_data['prev_users'].clear()
            return
        else:
            context.chat_data['prev_users'].pop(0)

    if not low_tokens:
        # message was only my name
        update.message.reply_text('Че)')
        return

    if is_thanks(text):
        update.message.reply_text(PhraseManager.reply_to_thanks())
        return

    if have_starts(low_tokens, 'еблан', 'пидор', 'маня', 'уебок', 'лал', 'пету', 'долба', 'долбо', 'лох', 'пидр', 'лош', 'гондон', 'гандон'):
        # TODO: filter possible negation
        update.message.reply_text(PhraseManager.reply_to_offense())
        return

    # for diden only
    if are_in_a_row(low_tokens, ['мне', 'не', 'приятель']):
        update.message.reply_text('Ты мне не кореш, друг...')
        return

    if have_starts(low_tokens, 'нов') and have_starts(low_tokens, 'функц'):
        update.message.reply_text('Да я ебашу пиздец))')
        return

    if have_starts(low_tokens, 'бедняга'):
        update.message.reply_text('Да лан, мне норм🤨🤨')
        return

    if are_in_a_row(low_tokens, ['плиз', 'удали']):
        context.bot.delete_message(update.message.chat.id, 2598)
        return

    if are_in_a_row(low_tokens, ['обдут', 'никит']):
        update.message.reply_text('Не ну этот чел ебашит по красоте)))')
        return

    if have_starts(low_tokens, 'соси', 'пососи'):
        update.message.reply_text('Зачем, если ты уже сосёшь?)')
        return

    if have_starts(low_tokens, 'иди'):
        update.message.reply_text('Да сам иди, петушня)')
        return

    if have_starts(low_tokens, 'мошн', 'помошн'):
        update.message.reply_text('Не ну так-то я бы помошнил))')
        return

    if have_starts(low_tokens, 'намошнено', 'помошнено'):
        update.message.reply_text('Пиздатенько че)')
        return

    if have_starts(low_tokens, 'трол'):
        update.message.reply_text('Ну я типа пиздец тралебас ((:')
        return

    if have_starts(low_tokens, 'кнопк'):
        challenge(update, context)
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

    if have_starts(low_tokens, 'сешишь'):
        update.message.reply_text('Да хз, я прост на чилле, сешишь тут только ты братишка)))')
        return

    if have_starts(low_tokens, 'завали'):
        update.message.reply_text('Погоди, чел, нет, это ТЫ ЗАВАЛИ)))')
        return

    if have_starts(low_tokens, 'залетай'):
        update.message.reply_text('Так-с, записываю айпишник')
        return

    if have_starts(low_tokens, 'базар'):
        update.message.reply_text('Не ну я базарю че')
        return

    if have_starts(low_tokens, 'толер'):
        update.message.reply_text('По пизде нахуй')
        return

    if have_starts(low_tokens, 'флекс', 'пофлекс'):
        update.message.reply_text(PhraseManager.flex())
        return
    
    if have_starts(low_tokens, 'жиз'):
        update.message.reply_text('Да жиза пиздец братан...')
        return

    if have_starts(low_tokens, 'если'):
        update.message.reply_text('Это ты конечно интересно придумал, но хз братишка))))')
        return

    if have_starts(low_tokens, 'любишь', 'нравится', 'дуть', 'дуешь', 'дудо', 'dudo', 'плюх', 'напас'):
        update.message.reply_text(PhraseManager.love_420())
        return

    if have_starts(low_tokens, 'красав', 'молодец', 'вп', 'wp', 'малаца', 'хорош', 'батя'):
        update.message.reply_text(PhraseManager.thanks())
        return

    if is_question(low_tokens):
        update.message.reply_text(PhraseManager.answer_question())
        return

    if Settings.troll_mode:
        if str(low_tokens[-1]).endswith('))))'):
            update.message.reply_text('Че такой довольный-то, пидорок?))')
            return

        if str(low_tokens[-1]).endswith('(((('):
            update.message.reply_text('Да ты не грусти, всё равно ты не бот и скоро сдохнешь')
            return

        update.message.reply_text('Не понял че ты хочешь, но думаю, что это потому что ты маня)')
        return

    update.message.reply_text(PhraseManager.default())
