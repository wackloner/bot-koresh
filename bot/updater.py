import logging
from typing import Optional

from telegram.ext import CallbackContext, Job

from bot.context import app_context
from bot.settings import TRACKINGS_UPDATE_INTERVAL
from managers.phrase_manager import PhraseManager
from model.tracking import AddressStatus
from utils.message_utils import send_tx_info


def update_trackings(context: CallbackContext):
    logging.debug('-> Updating trackings...')

    try:
        for t in app_context.tracking_manager.get_all():
            old_status = t.status
            updated = app_context.tracking_manager.update_tracking(t)
            if not updated:
                continue

            if updated.status != old_status:
                if updated.status == AddressStatus.NOT_CONFIRMED:
                    send_tx_info(t, 'Так-то опачи))')
                    continue

                if updated.status == AddressStatus.CONFIRMED:
                    send_tx_info(t, PhraseManager.just_confirmed_reaction())
                    if app_context.tracking_manager.remove_tracking(updated):
                        logging.debug(f'Address {t.address} was removed.')
                    else:
                        logging.debug(f'Failed to remove address {t.address}.')
                    continue

            if updated.status == AddressStatus.NOT_CONFIRMED:
                send_tx_info(t, 'Так-с так-с што тут у н а н а с . . .')

    except Exception as e:
        logging.exception(e)

    logging.debug('-> Updating done.')


def run_info_updater_if_not() -> Optional[Job]:
    if app_context.updater_job is None:
        app_context.updater_job = app_context.job_queue.run_repeating(callback=update_trackings, interval=TRACKINGS_UPDATE_INTERVAL)
    return app_context.updater_job
