from datetime import datetime
from typing import Optional, List, Dict

from blockchain import check_address
from messages import comment_tracking, send_tx_info, send_tx_info_full
from settings import TTL_IN_STATUS
from str_utils import timedelta_to_str
from tracking import Tracking, TrackingStatus, TransactionInfo


# TODO: assure that async/await approach makes it thread-safe
_trackings: List[Tracking] = []
_trackings_by_hash: Dict[str, Tracking]


def get_all_trackings() -> List[Tracking]:
    return _trackings.copy()


def add_tracking(t: Tracking) -> None:
    _trackings.append(t)
    _trackings_by_hash[t.address] = t


def has_tracking_for_address(address: str) -> bool:
    return address in _trackings_by_hash


def remove_tracking(t: Tracking) -> None:
    _trackings.remove(t)
    del _trackings_by_hash[t.address]


def get_tracking_by_address(address: str) -> Optional[Tracking]:
    return _trackings_by_hash.get(address)


def update_tracking(t: Tracking, new_status: Optional[TrackingStatus] = None, tx_info: Optional[TransactionInfo] = None) -> Optional[Tracking]:
    found = get_tracking_by_address(t.address)

    if found is not None:
        if new_status is not None:
            found.status = new_status
            found.status_updated_at = datetime.now()

        if tx_info is not None:
            found.last_confirmations_count = tx_info.confirmations_count

    return found


async def start_tracking(t: Tracking) -> None:
    status, tx_info = check_address(t.address)

    if has_tracking_for_address(t.address):
        # TODO: handle tx finished
        await send_tx_info_full(t, tx_info, 'Чел, я и так палю че по...')
        return

    # TODO: send sticker SESH
    if status == TrackingStatus.FAILED:
        await comment_tracking(t, f'Хз че по {t.address}, сеш (какой-то).')

    if status == TrackingStatus.NO_TRANSACTIONS:
        await comment_tracking(t,
                               f'пока чёт ни одной транзакции на {t.address}...\n'
                               f'но я понаблюдаю за ним, этак {timedelta_to_str(TTL_IN_STATUS)}, отпишу ес че')
        add_tracking(t)

    if status == TrackingStatus.TRANSACTION_IS_OLD:
        await comment_tracking(t,
                               f'последняя транзакция на {t.address} была {timedelta_to_str(tx_info.age)} назад...\n'
                               f'но ладно, мб ещё залетит, послежу за ним ещё {timedelta_to_str(TTL_IN_STATUS)}'
                               )
        add_tracking(t)

    if status == TrackingStatus.NOT_CONFIRMED:
        await send_tx_info(t, tx_info, 'Не ну попалим, попалим че...')
        add_tracking(t)

    if status == TrackingStatus.CONFIRMED:
        await send_tx_info(t, tx_info, 'УЖЕ намошнено ЧЕЛ))')
