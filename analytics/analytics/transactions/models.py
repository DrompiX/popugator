from dataclasses import dataclass, field
from datetime import datetime

from common.utils import generate_utc_dt


@dataclass
class TransactionLogRecord:
    public_user_id: str
    credit: int
    debit: int
    created_at: datetime = field(default_factory=generate_utc_dt)
