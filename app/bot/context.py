from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Optional

from telegram import Bot
from telegram.ext import Updater, Job

from app.external.blockchain_client import BlockchainClient
from app.external.map_client import MapClient
from app.external.translator_client import TranslatorClient
from app.managers.db_manager import DBManager
from app.managers.user_manager import UserManager
from app.bot.settings import BOT_API_TOKEN, UPDATER_ARGS, HI_MARK_INTERVAL
from app.managers.tracking_manager import TrackingManager


@dataclass
class Context:
    blockchain_client: BlockchainClient = field(default_factory=BlockchainClient)
    translator_client: TranslatorClient = field(default_factory=TranslatorClient)
    db_manager: DBManager = field(default_factory=DBManager)

    last_hi_mark_at: datetime = field(default=datetime.now() - HI_MARK_INTERVAL)

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
