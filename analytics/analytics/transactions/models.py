from datetime import datetime

from pydantic import BaseModel

from common.events.business.transactions import TransactionType


class TransactionLogRecord(BaseModel):
    public_id: str
    public_user_id: str
    type: TransactionType
    credit: int
    debit: int
    created_at: datetime
