import asyncio
import logging

from timeloop import Timeloop

from blockchain import check_address
from messages import send_tx_info
from settings import POLLING_DELAY
from tracking import TrackingStatus
from tracking_manager import remove_tracking, update_tracking, get_all_trackings

_tl = Timeloop()
_event_loop = asyncio.new_event_loop()


@_tl.job(interval=POLLING_DELAY)
def update_trackings():
    logging.info('Updating tracked addresses info...')

    _event_loop.run_until_complete(update_trackings_async())

    logging.info('Finish updating.')


async def update_trackings_async():
    for t in get_all_trackings():
        new_status, tx_info = check_address(t.address)
        additional_info_str = f', {tx_info.confirmations_count} confirmations' if new_status.has_transaction() else ''
        logging.info(f'{t.address} in state {new_status}{additional_info_str}')

        if new_status != t.status:
            if new_status == TrackingStatus.NOT_CONFIRMED:
                await send_tx_info(t, tx_info, 'Так-то оп))')
                update_tracking(t, new_status, tx_info)

            if new_status == TrackingStatus.CONFIRMED:
                await send_tx_info(t, tx_info, 'Так-то по мрази залетело)))')
                remove_tracking(t)

        if new_status == TrackingStatus.NOT_CONFIRMED and tx_info.confirmations_count != t.last_confirmations_count:
            await send_tx_info(t, tx_info, 'Так-с так-с што тут у н а н а с . . .')
            update_tracking(t, new_status, tx_info)


def schedule_updater():
    _tl.start(block=False)
