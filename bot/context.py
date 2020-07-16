import logging
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from telegram import Bot
from telegram.ext import Updater, CallbackContext, Job

from external.blockchain_client import BlockchainClient
from managers.data_manager import DataManager
from managers.db_manager import DBManager
from managers.phrase_manager import PhraseManager
from managers.user_manager import UserManager
from utils.message_utils import send_tx_info
from bot.settings import API_TOKEN, TRACKINGS_UPDATE_INTERVAL, UPDATER_ARGS
from model.tracking import TrackingStatus
from managers.tracking_manager import TrackingManager


def update_trackings(context: CallbackContext):
    logging.debug('-> Updating trackings...')

    try:
        for t in app_context.tracking_manager.get_all():
            new_status, tx_info = app_context.blockchain_client.check_address(t.address)
            if tx_info is None:
                logging.error(new_status)
                continue

            additional_info_str = f', {tx_info.confirmations_count} confirmations' if new_status.has_transaction() else ''
            logging.debug(f'--> {t.address} in state {new_status}{additional_info_str}')

            if new_status != t.status:
                if new_status == TrackingStatus.NOT_CONFIRMED:
                    send_tx_info(t, tx_info, 'Так-то оп))')
                    app_context.tracking_manager.update_existing_tracking(t, new_status, tx_info)

                if new_status == TrackingStatus.CONFIRMED:
                    send_tx_info(t, tx_info, PhraseManager.just_confirmed_reaction())
                    app_context.tracking_manager.update_existing_tracking(t, new_status, tx_info)

            if new_status == TrackingStatus.NOT_CONFIRMED and tx_info.confirmations_count != t.last_tx_confirmations:
                send_tx_info(t, tx_info, 'Так-с так-с што тут у н а н а с . . .')
                app_context.tracking_manager.update_existing_tracking(t, new_status, tx_info)

            if not new_status.should_continue():
                app_context.tracking_manager.remove_tracking(t)

    except Exception as e:
        logging.exception(e)

    logging.debug('-> Updating done.')


@dataclass
class Context:
    blockchain_client: BlockchainClient = field(default_factory=BlockchainClient)

    _job: Optional[Job] = field(default=None)

    @cached_property
    def updater(self) -> Updater:
        return Updater(API_TOKEN, use_context=True, request_kwargs=UPDATER_ARGS)

    @cached_property
    def bot(self) -> Bot:
        return self.updater.bot

    @cached_property
    def data_manager(self) -> DataManager:
        return DataManager(self.bot)

    @cached_property
    def tracking_manager(self) -> TrackingManager:
        return TrackingManager(self.data_manager, self.blockchain_client, self.bot)

    @cached_property
    def db_manager(self) -> DBManager:
        return DBManager()

    @cached_property
    def user_manager(self) -> UserManager:
        return UserManager(self.db_manager)

    @cached_property
    def job_queue(self):
        return self.updater.job_queue

    def run_info_updater_if_not(self) -> Optional[Job]:
        if self._job is None:
            self._job = self.job_queue.run_repeating(callback=update_trackings, interval=TRACKINGS_UPDATE_INTERVAL)
        return self._job


app_context = Context()
