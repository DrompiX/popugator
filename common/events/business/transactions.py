from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class TransactionType(str, Enum):
    PROFIT = 'profit'
    WITHDRAWAL = 'withdrawal'
    PAYMENT = 'payment'


class TransactionApplied(BaseModel):
    public_user_id: str
    type: TransactionType
    amount: int
    applied_at: datetime
