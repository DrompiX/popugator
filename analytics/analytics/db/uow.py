from typing import Any

from analytics.tasks.pg_repo import PostgresTaskRepo
from analytics.transactions.pg_repo import PostgresTransactionRepo
from analytics.transactions.repo import FakeTransactionRepo, TransactionRepo
from analytics.tasks.repo import FakeTaskRepo, TaskRepo
from analytics.users.pg_repo import PostgresUserRepo
from analytics.users.repo import FakeUserRepo, UserRepo
from common.db.pg_uow import PostgresUoW
from common.db.uow import UnitOfWork


class AnalyticsUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo
    transactions: TransactionRepo


class PgAnalyticsUoW(AnalyticsUoW, PostgresUoW):
    async def __aenter__(self) -> Any:
        await super().__aenter__()
        self.tasks = PostgresTaskRepo(self._conn)
        self.users = PostgresUserRepo(self._conn)
        self.transactions = PostgresTransactionRepo(self._conn)


class FakeUoW(AnalyticsUoW):
    def __init__(self) -> None:
        self.tasks = FakeTaskRepo()
        self.users = FakeUserRepo()
        self.transactions = FakeTransactionRepo()
        self.commited = False

    async def commit(self) -> None:
        self.commited = True

    async def rollback(self) -> None:
        pass
