from datetime import datetime
from enum import Enum
from pydantic import Field

from common.events.base import Event, EventData


class TransactionType(str, Enum):
    PROFIT = 'profit'
    WITHDRAWAL = 'withdrawal'
    PAYMENT = 'payment'


########################################
# TransactionApplied event description #
########################################


class TransactionAppliedData(EventData):
    public_user_id: str
    type: TransactionType
    amount: int
    applied_at: datetime


class TransactionApplied(Event):
    name: str = Field(default='TransactionApplied', const=True)
    domain: str = Field(default='accounting', const=True)
    data: TransactionAppliedData
