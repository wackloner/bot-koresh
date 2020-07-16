from telegram.ext import CallbackContext


def delete_after_f(chat_id: int, message_id: int):
    def delete_after(context: CallbackContext):
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return delete_after
