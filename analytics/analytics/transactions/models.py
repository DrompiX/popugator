from datetime import datetime

from pydantic import BaseModel


class TransactionLogRecord(BaseModel):
    public_id: str
    public_user_id: str
    credit: int
    debit: int
    created_at: datetime
