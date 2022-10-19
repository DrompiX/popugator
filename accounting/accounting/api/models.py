from pydantic import BaseModel


class TransactionLogRecordOut(BaseModel):
    description: str
    debit: int
    credit: int


class UserAccountInfoResponse(BaseModel):
    balance: int
    log: list[TransactionLogRecordOut]


class ManagementEarnedResponse(BaseModel):
    money_earned: int
