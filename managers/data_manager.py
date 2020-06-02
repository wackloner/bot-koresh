import json
import logging
from dataclasses import dataclass
from functools import cached_property
from typing import List

from telegram import Bot

from bot.settings import ADMIN_CHAT_ID, DATA_MESSAGE_ID
from model.tracking import Tracking


@dataclass
class DataManager:
    bot: Bot

    @cached_property
    def data_message_id(self) -> int:
        if DATA_MESSAGE_ID is not None:
            return DATA_MESSAGE_ID

        empty_json = json.dumps([])
        message = self.bot.send_message(chat_id=ADMIN_CHAT_ID, text=empty_json)

        logging.debug(f'New data message: {message.message_id}')
        return message.message_id

    def get_current_trackings(self) -> List[Tracking]:
        fwd = self.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=ADMIN_CHAT_ID, message_id=self.data_message_id)
        self.bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=fwd.message_id)

        json_list = json.loads(fwd.text)
        logging.debug(f'current trackings json = {json_list}')

        trackings_list = [Tracking(**json_item) for json_item in json_list]
        logging.debug(f'current trackings = {trackings_list}')

        return trackings_list

    def save_trackings(self, trackings: List[Tracking]) -> bool:
        data_str = self._get_json(trackings)

        logging.debug(f'KEK = {data_str}')

        edited = self.bot.edit_message_text(chat_id=ADMIN_CHAT_ID, message_id=self.data_message_id, text=data_str)
        return edited is not True

    @staticmethod
    def _get_json(trackings: List[Tracking]) -> str:
        return '[' + ',\n'.join([t.to_json() for t in trackings]) + ']'