from common.db.uow import UnitOfWork
from taskman.tasks.repo import FakeTaskRepo, TaskRepo
from taskman.users.repo import FakeUserRepo, UserRepo


class TaskmanUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo


class FakeUoW(TaskmanUoW):
    def __init__(self) -> None:
        self.tasks = FakeTaskRepo()
        self.users = FakeUserRepo()
        self.commited = False

    async def commit(self) -> None:
        self.commited = True

    async def rollback(self) -> None:
        pass
