from dataclasses import dataclass
from typing import List, Optional

from telegram import Bot

from settings import ADMIN_CHAT_ID
from tracking_manager import TrackingManager


@dataclass
class DbManager:
    bot: Bot
    tracking_manager: TrackingManager
    initialized: bool = False

    trackings_storage_message_id: Optional[int] = None

    def initialize(self) -> bool:
        message = self.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f'{self.tracking_manager.get_all_trackings()}')
        self.trackings_storage_message_id = message.message_id
        return True

    def get_current_trackings(self) -> List[str]:
        fwd = self.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=ADMIN_CHAT_ID, message_id=self.trackings_storage_message_id)
        return [fwd.text]

