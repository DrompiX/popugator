from analytics.transactions.repo import FakeTransactionRepo, TransactionRepo
from analytics.tasks.repo import FakeTaskRepo, TaskRepo
from analytics.users.repo import FakeUserRepo, UserRepo
from common.db.uow import UnitOfWork


class AnalyticsUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo
    transactions: TransactionRepo


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
