from telegram.ext import CallbackContext


def increase_messages_count(context: CallbackContext):
    context.chat_data['msg_cnt'] = context.chat_data.get('msg_cnt', 0) + 1
    return context.chat_data['msg_cnt']
