import logging
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Optional, List, Dict

from telegram import Message, ParseMode, Bot

from managers.blockchain_client import BlockchainClient
from managers.data_manager import DataManager
from utils.messages import comment_tracking, send_tx_info, send_tx_info_full
from bot.settings import TTL_IN_STATUS, ADMIN_CHAT_ID
from utils.str_utils import timedelta_to_str, get_addr_html_url
from model.tracking import Tracking, TrackingStatus, TransactionInfo


# TODO: check thread-safety
# TODO: schedule backups
@dataclass
class TrackingManager:
    data_manager: DataManager
    blockchain_client: BlockchainClient
    bot: Bot

    @cached_property
    def trackings(self) -> List[Tracking]:
        return self.data_manager.get_current_trackings() or []

    @cached_property
    def trackings_by_hash(self) -> Dict[str, Tracking]:
        return {t.address: t for t in self.trackings}

    def get_all(self) -> List[Tracking]:
        return self.trackings.copy()

    # TODO: more efficient
    def get_by_chat_id(self, chat_id: int) -> List[Tracking]:
        return list(filter(lambda t: t.chat_id == chat_id, self.trackings))

    def do_backup(self) -> bool:
        return self.data_manager.save_trackings(self.trackings)

    def start_tracking(self, address: str, message: Message) -> TrackingStatus:
        now = datetime.today()
        t = Tracking(address, now, message.chat_id, TrackingStatus.NOT_STARTED, now)
        return self.init_tracking(t)

    def add_tracking(self, t: Tracking, info_update: Optional[TransactionInfo] = None) -> None:
        self.trackings.append(t)
        self.trackings_by_hash[t.address] = t
        if info_update is not None:
            self._update_tracking(t, tx_info=info_update)
        self.do_backup()

    def update_existing_tracking(self, t: Tracking, new_status: Optional[TrackingStatus] = None,
                                 tx_info: Optional[TransactionInfo] = None) -> Optional[Tracking]:
        found = self.get_tracking_by_address(t.address)
        if found is not None:
            self._update_tracking(t, new_status, tx_info)
            self.do_backup()
        return found

    def remove_tracking(self, t: Tracking) -> None:
        self.trackings.remove(t)
        del self.trackings_by_hash[t.address]

        logging.debug(f'Removed address {t.address}')
        
        self.do_backup()

    def has_tracking_for_address(self, address: str) -> bool:
        return address in self.trackings_by_hash

    def get_tracking_by_address(self, address: str) -> Optional[Tracking]:
        return self.trackings_by_hash.get(address)

    # TODO: get only address as arg and then create tracking
    def init_tracking(self, t: Tracking) -> TrackingStatus:
        status, tx_info = self.blockchain_client.check_address(t.address)
        self._update_tracking(t, status, tx_info)

        # TODO: handle new statuses

        if self.has_tracking_for_address(t.address):
            # TODO: handle tx finished
            send_tx_info_full(t, tx_info, 'Чел, да я и так палю че по...')
            return status

        if status == TrackingStatus.INVALID_HASH:
            comment_tracking(t, f'Это хуйня, а не адрес, чел)) {t.address} - че?)')
            return status

        if status == TrackingStatus.FAILED:
            comment_tracking(t, f'Хз че по {t.address}, сеш (какой-то).')
            return status

        if status == TrackingStatus.CONFIRMED:
            send_tx_info(t, tx_info, 'УЖЕ намошнено ЧЕЛ))')
            return None

        if status == TrackingStatus.NO_TRANSACTIONS:
            self.bot.send_message(t.chat_id, f'Пока чёт ни одной транзакции на {get_addr_html_url(t.address)}...\n'
                                             f'Но я понаблюдаю за ним, этак {timedelta_to_str(TTL_IN_STATUS)}, отпишу ес че',
                                             parse_mode=ParseMode.HTML)
            self.add_tracking(t)

        if status == TrackingStatus.TRANSACTION_IS_OLD:
            self.bot.send_message(t.chat_id, f'Последняя транзакция на {get_addr_html_url(t.address)} была {timedelta_to_str(tx_info.age)} назад...\n'
                                             f'Но ладно, мб новая залетит, послежу за адресом ещё {timedelta_to_str(TTL_IN_STATUS)}',
                                             parse_mode=ParseMode.HTML)
            self.add_tracking(t)

        if status == TrackingStatus.NOT_CONFIRMED:
            if tx_info.confirmations_count == 0:
                send_tx_info(t, tx_info, 'Так-с, пока чёт нихуя, но я попалю, че)')
            else:
                send_tx_info(t, tx_info, 'Не ну) УЖе найс) Я попалю когда там че)')
            self.add_tracking(t)

        return status

    @staticmethod
    def _update_tracking(t: Tracking, new_status: Optional[TrackingStatus] = None, tx_info: Optional[TransactionInfo] = None) -> Tracking:
        if new_status is not None:
            t.status = new_status
            t.status_updated_at = datetime.now()

        if tx_info is not None:
            t.last_tx_confirmations = tx_info.confirmations_count

        return t
