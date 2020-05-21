import enum
from dataclasses import dataclass
from datetime import datetime, timedelta

from aiogram import types


class TrackingStatus(enum.Enum):
    NOT_STARTED = 1
    TRANSACTION_IS_OLD = 2
    NO_TRANSACTIONS = 3
    NOT_CONFIRMED = 4
    CONFIRMED = 5
    FAILED = 6

    def has_transaction(self):
        return self == self.NOT_CONFIRMED or self == self.CONFIRMED


@dataclass
class Tracking:
    address: str
    added_at: datetime
    trigger_message: types.Message

    status: TrackingStatus
    status_updated_at: datetime
    last_confirmations_count: int


@dataclass
class TransactionInfo:
    hash: str
    created_at: datetime
    confirmations_count: int

    @property
    def age(self) -> timedelta:
        return datetime.now() - self.created_at
