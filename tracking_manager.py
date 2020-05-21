from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

from blockchain import check_address
from messages import comment_tracking, send_tx_info, send_tx_info_full
from settings import TTL_IN_STATUS
from str_utils import timedelta_to_str
from tracking import Tracking, TrackingStatus, TransactionInfo


# TODO: assure that async/await approach makes it thread-safe
@dataclass
class TrackingManager:
    _trackings: List[Tracking] = field(default_factory=list)
    _trackings_by_hash: Dict[str, Tracking] = field(default_factory=dict)

    def get_all_trackings(self) -> List[Tracking]:
        return self._trackings.copy()

    def add_tracking(self, t: Tracking) -> None:
        self._trackings.append(t)
        self._trackings_by_hash[t.address] = t

    def has_tracking_for_address(self, address: str) -> bool:
        return address in self._trackings_by_hash

    def remove_tracking(self, t: Tracking) -> None:
        self._trackings.remove(t)
        del self._trackings_by_hash[t.address]

    def get_tracking_by_address(self, address: str) -> Optional[Tracking]:
        return self._trackings_by_hash.get(address)

    def update_tracking(self, t: Tracking, new_status: Optional[TrackingStatus] = None, tx_info: Optional[TransactionInfo] = None) -> Optional[Tracking]:
        found = self.get_tracking_by_address(t.address)

        if found is not None:
            if new_status is not None:
                found.status = new_status
                found.status_updated_at = datetime.now()

            if tx_info is not None:
                found.last_confirmations_count = tx_info.confirmations_count

        return found

    async def start_tracking_async(self, t: Tracking) -> None:
        status, tx_info = check_address(t.address)

        if self.has_tracking_for_address(t.address):
            # TODO: handle tx finished
            await send_tx_info_full(t, tx_info, 'чел, да я и так палю че по...')
            return

        # TODO: send sticker SESH
        if status == TrackingStatus.FAILED:
            await comment_tracking(t, f'хз че по {t.address}, сеш (какой-то).')

        if status == TrackingStatus.NO_TRANSACTIONS:
            await comment_tracking(t,
                                   f'пока чёт ни одной транзакции на {t.address}...\n'
                                   f'но я понаблюдаю за ним, этак {timedelta_to_str(TTL_IN_STATUS)}, отпишу ес че')
            self.add_tracking(t)

        if status == TrackingStatus.TRANSACTION_IS_OLD:
            await comment_tracking(t,
                                   f'последняя транзакция на {t.address} была {timedelta_to_str(tx_info.age)} назад...\n'
                                   f'но ладно, мб новая залетит, послежу за адресом ещё {timedelta_to_str(TTL_IN_STATUS)}'
                                   )
            self.add_tracking(t)

        if status == TrackingStatus.NOT_CONFIRMED:
            await send_tx_info(t, tx_info, 'не ну попалим, попалим че...')
            self.add_tracking(t)

        if status == TrackingStatus.CONFIRMED:
            await send_tx_info(t, tx_info, 'УЖЕ намошнено ЧЕЛ))')
