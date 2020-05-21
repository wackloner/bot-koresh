import asyncio
import logging

from timeloop import Timeloop

from blockchain import check_address
from context import tracking_manager
from messages import send_tx_info
from settings import POLLING_DELAY
from tracking import TrackingStatus


_tl = Timeloop()
_event_loop = asyncio.new_event_loop()


@_tl.job(interval=POLLING_DELAY)
def update_trackings():
    logging.info('Updating trackings...')

    asyncio.run_coroutine_threadsafe(update_trackings_async(), _event_loop)

    logging.info('Data updated.')


async def update_trackings_async():
    for t in tracking_manager.get_all_trackings():
        new_status, tx_info = check_address(t.address)
        additional_info_str = f', {tx_info.confirmations_count} confirmations' if new_status.has_transaction() else ''
        logging.info(f'{t.address} in state {new_status}{additional_info_str}')

        if new_status != t.status:
            if new_status == TrackingStatus.NOT_CONFIRMED:
                await send_tx_info(t, tx_info, 'Так-то оп))')
                tracking_manager.update_tracking(t, new_status, tx_info)

            if new_status == TrackingStatus.CONFIRMED:
                await send_tx_info(t, tx_info, 'Так-то по мрази залетело)))')
                tracking_manager.remove_tracking(t)

        if new_status == TrackingStatus.NOT_CONFIRMED and tx_info.confirmations_count != t.last_confirmations_count:
            await send_tx_info(t, tx_info, 'Так-с так-с што тут у н а н а с . . .')
            tracking_manager.update_tracking(t, new_status, tx_info)


def schedule_trackings_updater():
    _tl.start(block=False)

    update_trackings()
