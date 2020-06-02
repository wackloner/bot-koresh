import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from telegram import Message
from telegram.ext import CallbackContext


class TrackingStatus(enum.Enum):
    INVALID_HASH = 0
    NOT_STARTED = 1
    TRANSACTION_IS_OLD = 2
    NO_TRANSACTIONS = 3
    NOT_CONFIRMED = 4
    CONFIRMED = 5
    TIMEOUT = 6
    FAILED = 7

    def has_transaction(self):
        return self == self.NOT_CONFIRMED or self == self.CONFIRMED


@dataclass
class TransactionInfo:
    hash: str
    created_at: datetime
    confirmations_count: int

    @property
    def age(self) -> timedelta:
        return datetime.now() - self.created_at


@dataclass
class Tracking:
    address: str
    added_at: datetime

    # TODO: do not store the whole message
    trigger_message: Message
    context: CallbackContext

    last_tx_info: Optional[TransactionInfo]
    status: TrackingStatus
    status_updated_at: datetime

    @property
    def last_confirmations_count(self) -> int:
        return self.last_tx_info.confirmations_count
