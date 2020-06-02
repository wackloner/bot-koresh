import logging
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from telegram import Bot
from telegram.ext import Updater, CallbackContext, Job

from managers.blockchain_utils import check_address
from managers.db_manager import DbManager
from messages import send_tx_info
from managers.phrase_manager import PhraseManager
from bot.settings import API_TOKEN, TRACKINGS_UPDATE_INTERVAL, UPDATER_ARGS
from model.tracking import TrackingStatus
from managers.tracking_manager import TrackingManager


class App:
    app_context = None

    @classmethod
    def set_context(cls, context):
        cls.app_context = context


def update_trackings(context: CallbackContext):
    logging.debug('-> Updating trackings...')

    try:
        for t in App.app_context.tracking_manager.get_all_trackings():
            new_status, tx_info = check_address(t.address)

            additional_info_str = f', {tx_info.confirmations_count} confirmations' if new_status.has_transaction() else ''
            logging.debug(f'--> {t.address} in state {new_status}{additional_info_str}')

            if new_status != t.status:
                if new_status == TrackingStatus.NOT_CONFIRMED:
                    send_tx_info(t, tx_info, 'Так-то оп))')
                    App.app_context.tracking_manager.update_existing_tracking(t, new_status, tx_info)

            if new_status == TrackingStatus.CONFIRMED:
                send_tx_info(t, tx_info, PhraseManager.just_confirmed_reaction())
                logging.debug(f'chat_data = {context.chat_data}')
                App.app_context.tracking_manager.remove_tracking(t)

            if new_status == TrackingStatus.NOT_CONFIRMED and tx_info.confirmations_count != t.last_confirmations_count:
                send_tx_info(t, tx_info, 'Так-с так-с што тут у н а н а с . . .')
                App.app_context.tracking_manager.update_existing_tracking(t, new_status, tx_info)

    except Exception as e:
        logging.error(e)

    logging.debug('-> Updating done.')


@dataclass
class Context:
    tracking_manager: TrackingManager = field(default_factory=TrackingManager)
    _job: Optional[Job] = field(default=None)

    @cached_property
    def updater(self) -> Updater:
        return Updater(API_TOKEN, use_context=True, request_kwargs=UPDATER_ARGS)

    @cached_property
    def bot(self) -> Bot:
        return self.updater.bot

    @cached_property
    def db_manager(self) -> DbManager:
        return DbManager(self.bot, self.tracking_manager)

    @cached_property
    def job_queue(self):
        return self.updater.job_queue

    def run_info_updater(self) -> Optional[Job]:
        if self._job is None:
            self._job = self.job_queue.run_repeating(callback=update_trackings, interval=TRACKINGS_UPDATE_INTERVAL)
        return self._job
