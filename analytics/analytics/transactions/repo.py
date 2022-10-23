from abc import ABC, abstractmethod
from datetime import date

from analytics.transactions.models import TransactionLogRecord


class TransactionRepo(ABC):
    @abstractmethod
    async def add(self, record: TransactionLogRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, public_id: str) -> list[TransactionLogRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_date(self, d: date) -> list[TransactionLogRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        raise NotImplementedError


class FakeTransactionRepo(TransactionRepo):
    def __init__(self) -> None:
        self.transactions: list[TransactionLogRecord] = []

    async def add(self, record: TransactionLogRecord) -> None:
        self.transactions.append(record)

    async def get_by_user_id(self, public_id: str) -> list[TransactionLogRecord]:
        records: list[TransactionLogRecord] = []
        for transaction in self.transactions:
            if transaction.public_user_id == public_id:
                records.append(transaction)

        return records

    async def get_all_by_date(self, d: date) -> list[TransactionLogRecord]:
        records: list[TransactionLogRecord] = []
        for transaction in self.transactions:
            if transaction.created_at.date() == d:
                records.append(transaction)

        return records

    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        balances: dict[str, int] = {}
        for transaction in self.transactions:
            if transaction.created_at.date() == d:
                balances[transaction.public_user_id] += transaction.debit - transaction.credit

        return balances
