from typing import Any

from accounting.transactions.pg_repo import PostgresTransactionRepo
from accounting.transactions.repo import FakeTransactionRepo, TransactionRepo
from accounting.tasks.pg_repo import PostgresTaskRepo
from accounting.tasks.repo import FakeTaskRepo, TaskRepo
from accounting.users.pg_repo import PostgresUserRepo
from accounting.users.repo import FakeUserRepo, UserRepo
from common.db.pg_uow import PostgresUoW
from common.db.uow import UnitOfWork


class AccountingUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo
    transactions: TransactionRepo


class PgAnalyticsUoW(AccountingUoW, PostgresUoW):
    async def __aenter__(self) -> Any:
        await super().__aenter__()
        self.tasks = PostgresTaskRepo(self._conn)
        self.users = PostgresUserRepo(self._conn)
        self.transactions = PostgresTransactionRepo(self._conn)


class FakeUoW(AccountingUoW):
    def __init__(self) -> None:
        self.tasks = FakeTaskRepo()
        self.users = FakeUserRepo()
        self.transactions = FakeTransactionRepo()
        self.commited = False

    async def commit(self) -> None:
        self.commited = True

    async def rollback(self) -> None:
        pass
