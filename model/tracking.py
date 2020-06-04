import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict


class TrackingStatus(str, enum.Enum):
    INVALID_HASH = 'invalid_hash'
    NOT_STARTED = 'not_started'
    TRANSACTION_IS_OLD = 'transaction_is_too_old'
    NO_TRANSACTIONS = 'no_transactions'
    NOT_CONFIRMED = 'not_confirmed'
    CONFIRMED = 'confirmed'
    TIMEOUT = 'timeout'
    FAILED = 'failed'
    INTERRUPTED = 'interrupted'

    def is_not_confirmed(self):
        return self == self.NOT_CONFIRMED

    def is_confirmed(self):
        return self == self.CONFIRMED

    def has_no_transactions(self):
        return self == self.NO_TRANSACTIONS

    def has_transaction(self):
        return self.is_not_confirmed or self.is_confirmed()

    def in_progress(self):
        return self.has_transaction() or self == self.NO_TRANSACTIONS

    def should_continue(self):
        return self.is_not_confirmed() or self.has_no_transactions()


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
    chat_id: int

    status: TrackingStatus = field(default=TrackingStatus.NOT_STARTED)
    status_updated_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

    last_tx_confirmations: Optional[int] = None

    def to_dict(self) -> Dict:
        return dict(
            address=f'"{self.address}"',
            created_at=self.created_at.timestamp(),
            chat_id=self.chat_id,
            status=f'"{self.status}"',
            status_updated_at=self.status_updated_at.timestamp()
        )

    def to_json(self) -> str:
        return '{' + ', '.join([f'"{k}": {v}'for (k, v) in self.to_dict().items()]) + '}'
