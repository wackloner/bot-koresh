from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from telegram import Bot
from telegram.ext import Updater, Job

from koresh.external.blockchain_client import BlockchainClient
from koresh.external.map_client import MapClient
from koresh.external.translator_client import TranslatorClient
from koresh.managers.db_manager import DBManager
from koresh.managers.user_manager import UserManager
from koresh.bot.settings import BOT_API_TOKEN, UPDATER_ARGS
from koresh.managers.tracking_manager import TrackingManager


@dataclass
class Context:
    blockchain_client: BlockchainClient = field(default_factory=BlockchainClient)
    translator_client: TranslatorClient = field(default_factory=TranslatorClient)
    db_manager: DBManager = field(default_factory=DBManager)

    updater_job: Optional[Job] = field(default=None)

    @cached_property
    def updater(self) -> Updater:
        return Updater(BOT_API_TOKEN, use_context=True, request_kwargs=UPDATER_ARGS)

    @cached_property
    def bot(self) -> Bot:
        return self.updater.bot

    @cached_property
    def map_client(self) -> MapClient:
        return MapClient()

    @cached_property
    def tracking_manager(self) -> TrackingManager:
        return TrackingManager(self.blockchain_client, self.db_manager)

    @cached_property
    def user_manager(self) -> UserManager:
        return UserManager(self.db_manager)

    @cached_property
    def job_queue(self):
        return self.updater.job_queue


app_context = Context()
