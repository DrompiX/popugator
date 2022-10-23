from datetime import datetime

from pydantic import BaseModel, Field

from common.utils import generate_utc_dt, generate_uuid


class TransactionLogRecord(BaseModel):
    public_id: str = Field(default_factory=generate_uuid)
    public_user_id: str
    description: str
    credit: int
    debit: int
    created_at: datetime = Field(default_factory=generate_utc_dt)
