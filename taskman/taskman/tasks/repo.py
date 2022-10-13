from abc import ABC, abstractmethod

from taskman.tasks.models import Task, TaskStatus


class TaskNotFound(Exception):
    def __init__(self, task_id: str) -> None:
        super().__init__(f'Task with id {task_id} not found')
        self.task_id = task_id


class TaskRepo(ABC):
    @abstractmethod
    async def create(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: str) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_open(self) -> list[Task]:
        raise NotImplementedError


class FakeTaskRepo(TaskRepo):
    def __init__(self) -> None:
        self.task_store: dict[str, Task] = {}

    async def create(self, task: Task) -> None:
        self.task_store[task.public_id] = task

    async def update(self, task: Task) -> None:
        await self.create(task)

    async def get_by_id(self, task_id: str) -> Task:
        if task_id not in self.task_store:
            raise TaskNotFound(task_id)

        return self.task_store[task_id]

    async def get_all(self) -> list[Task]:
        return list(self.task_store.values())

    async def get_all_open(self) -> list[Task]:
        return list(filter(lambda t: t.status == TaskStatus.OPEN, self.task_store.values()))
