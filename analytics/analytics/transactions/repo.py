from abc import ABC, abstractmethod
from datetime import date

from analytics.transactions.models import TransactionLogRecord


class TransactionRepo(ABC):
    @abstractmethod
    async def add(self, record: TransactionLogRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def get_management_income(self, start: date, end: date) -> int:
        raise NotImplementedError


class FakeTransactionRepo(TransactionRepo):
    def __init__(self) -> None:
        self.transactions: list[TransactionLogRecord] = []

    async def add(self, record: TransactionLogRecord) -> None:
        self.transactions.append(record)

    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        balances: dict[str, int] = {}
        for transaction in self.transactions:
            if transaction.created_at.date() == d:
                balances[transaction.public_user_id] += transaction.debit - transaction.credit

        return balances

    async def get_management_income(self, start: date, end: date) -> int:
        raise NotImplementedError
