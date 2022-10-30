from accounting.transactions.repo import FakeTransactionRepo, TransactionRepo
from common.db.uow import UnitOfWork
from accounting.tasks.repo import FakeTaskRepo, TaskRepo
from accounting.users.repo import FakeUserRepo, UserRepo


class AccountingUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo
    transactions: TransactionRepo


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
