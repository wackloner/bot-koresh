from telegram.ext import CallbackContext


def add_address_for_chat(address: str, context: CallbackContext):
    if 'trackings' not in context.chat_data:
        context.chat_data['trackings'] = []
    context.chat_data['trackings'].append(address)


def remove_address_for_chat(address: str, context: CallbackContext):
    if 'trackings' in context.chat_data:
        context.chat_data['trackings'].remove(address)


def get_addresses_for_chat(context: CallbackContext):
    if 'trackings' not in context.chat_data:
        context.chat_data['trackings'] = []
    return context.chat_data['trackings']


def increase_messages_count(context: CallbackContext):
    context.chat_data['msg_cnt'] = context.chat_data.get('msg_cnt', 32) + 1
    return context.chat_data['msg_cnt']
