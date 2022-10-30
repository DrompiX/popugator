from typing import Any

from common.db.pg_uow import PostgresUoW
from common.db.uow import UnitOfWork
from taskman.tasks.pg_repo import PostgresTaskRepo
from taskman.tasks.repo import FakeTaskRepo, TaskRepo
from taskman.users.pg_repo import PostgresUserRepo
from taskman.users.repo import FakeUserRepo, UserRepo


class TaskmanUoW(UnitOfWork):
    tasks: TaskRepo
    users: UserRepo


class PgTaskmanUoW(TaskmanUoW, PostgresUoW):
    async def __aenter__(self) -> Any:
        await super().__aenter__()
        self.tasks = PostgresTaskRepo(self._conn)
        self.users = PostgresUserRepo(self._conn)


class FakeUoW(TaskmanUoW):
    def __init__(self) -> None:
        self.tasks = FakeTaskRepo()
        self.users = FakeUserRepo()
        self.commited = False

    async def commit(self) -> None:
        self.commited = True

    async def rollback(self) -> None:
        pass
