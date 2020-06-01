from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

from telegram import Message, ParseMode
from telegram.ext import CallbackContext

from blockchain_utils import check_address
from callback_context_utils import remove_address_for_chat, add_address_for_chat
from messages import comment_tracking, send_tx_info, send_tx_info_full
from settings import TTL_IN_STATUS
from str_utils import timedelta_to_str, get_addr_html_url
from tracking import Tracking, TrackingStatus, TransactionInfo


# TODO: check thread-safety
# TODO: backup (disk or messages) and load from backup
@dataclass
class TrackingManager:
    _trackings: List[Tracking] = field(default_factory=list)
    _trackings_by_hash: Dict[str, Tracking] = field(default_factory=dict)

    def get_all_trackings(self) -> List[Tracking]:
        return self._trackings.copy()

    def start_tracking(self, address: str, message: Message, context: CallbackContext) -> Optional[Tracking]:
        now = datetime.today()
        t = Tracking(address, now, message, context, None, TrackingStatus.NOT_STARTED, now)
        t = self.init_tracking(t)

        if t is not None:
            from context import App
            App.app_context.run_info_updater()
        return t

    def add_tracking(self, t: Tracking, info_update: Optional[TransactionInfo] = None) -> None:
        self._trackings.append(t)
        self._trackings_by_hash[t.address] = t
        add_address_for_chat(t.address, t.context)
        if info_update is not None:
            self.update_tracking(t, tx_info=info_update)

    def has_tracking_for_address(self, address: str) -> bool:
        return address in self._trackings_by_hash

    def remove_tracking(self, t: Tracking) -> None:
        remove_address_for_chat(t.address, t.context)
        self._trackings.remove(t)
        del self._trackings_by_hash[t.address]

    def get_tracking_by_address(self, address: str) -> Optional[Tracking]:
        return self._trackings_by_hash.get(address)

    def update_existing_tracking(self, t: Tracking, new_status: Optional[TrackingStatus] = None,
                                 tx_info: Optional[TransactionInfo] = None) -> Optional[Tracking]:
        found = self.get_tracking_by_address(t.address)
        if found is not None:
            self.update_tracking(t, new_status, tx_info)
        return found

    # TODO: get only address as arg and then create tracking
    def init_tracking(self, t: Tracking) -> Optional[Tracking]:
        from context import App

        status, tx_info = check_address(t.address)
        self.update_tracking(t, status, tx_info)

        # TODO: handle new statuses

        if self.has_tracking_for_address(t.address):
            # TODO: handle tx finished
            send_tx_info_full(t, tx_info, 'Чел, да я и так палю че по...')
            return None

        if status == TrackingStatus.INVALID_HASH:
            comment_tracking(t, f'Это хуйня, а не адрес, чел)) {t.address} - че?)')
            return None

        # TODO: send sticker SESH
        if status == TrackingStatus.FAILED:
            comment_tracking(t, f'Хз че по {t.address}, сеш (какой-то).')
            return None

        if status == TrackingStatus.CONFIRMED:
            send_tx_info(t, tx_info, 'УЖЕ намошнено ЧЕЛ))')
            return None

        if status == TrackingStatus.NO_TRANSACTIONS:
            App.app_context.bot.send_message(t.trigger_message.chat_id, f'Пока чёт ни одной транзакции на {get_addr_html_url(t.address)}...\n'
                                                                    f'Но я понаблюдаю за ним, этак {timedelta_to_str(TTL_IN_STATUS)}, отпишу ес че',
                                                                    parse_mode=ParseMode.HTML)
            self.add_tracking(t)

        if status == TrackingStatus.TRANSACTION_IS_OLD:
            App.app_context.bot.send_message(t.trigger_message.chat_id, f'Последняя транзакция на {get_addr_html_url(t.address)} была {timedelta_to_str(tx_info.age)} назад...\n'
                                                                    f'Но ладно, мб новая залетит, послежу за адресом ещё {timedelta_to_str(TTL_IN_STATUS)}',
                                                                    parse_mode=ParseMode.HTML)
            self.add_tracking(t)

        if status == TrackingStatus.NOT_CONFIRMED:
            if tx_info.confirmations_count == 0:
                send_tx_info(t, tx_info, 'Так-с, пока чёт нихуя, но я попалю, че)')
            else:
                send_tx_info(t, tx_info, 'Не ну) УЖе найс) Я попалю когда там че)')
            self.add_tracking(t)

        return t

    @staticmethod
    def update_tracking(t: Tracking, new_status: Optional[TrackingStatus] = None, tx_info: Optional[TransactionInfo] = None) -> Tracking:
        if new_status is not None:
            t.status = new_status
            t.status_updated_at = datetime.now()

        if tx_info is not None:
            t.last_tx_info = tx_info

        return t
