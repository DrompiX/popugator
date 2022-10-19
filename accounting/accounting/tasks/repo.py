from abc import ABC, abstractmethod

from accounting.tasks.models import Task


class TaskNotFound(Exception):
    def __init__(self, task_id: str) -> None:
        super().__init__(f'Task with id {task_id} not found')
        self.task_id = task_id


class TaskRepo(ABC):
    @abstractmethod
    async def create(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: str) -> Task:
        raise NotImplementedError


class FakeTaskRepo(TaskRepo):
    def __init__(self) -> None:
        self.task_store: dict[str, Task] = {}

    async def create(self, task: Task) -> None:
        self.task_store[task.public_id] = task

    async def get_by_id(self, task_id: str) -> Task:
        if task_id not in self.task_store:
            raise TaskNotFound(task_id)

        return self.task_store[task_id]