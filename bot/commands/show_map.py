import logging

from telegram import Update
from telegram.ext import CallbackContext

from bot.commands.decorators import moshnar_command
from bot.context import app_context


@moshnar_command
def show_map(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        # TODO: show whole city
        pass
    else:
        coordinates = ''.join(context.args)

        img_link = app_context.map_client.get_img_link_by_coordinates(coordinates)
        update.message.reply_photo(photo=img_link)
