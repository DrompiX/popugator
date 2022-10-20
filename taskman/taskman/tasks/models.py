from enum import Enum

from pydantic import BaseModel, Field

from common.utils import generate_uuid


class TaskStatus(str, Enum):
    OPEN = 'open'
    DONE = 'done'

    def __repr__(self) -> str:
        return str(self)


class UnassignedTask(BaseModel):
    public_id: str = Field(default_factory=generate_uuid)
    jira_id: str
    description: str
    status: TaskStatus = TaskStatus.OPEN


class TaskIsAlreadyCompleted(Exception):
    pass


class Task(UnassignedTask):
    assignee_id: str

    def mark_completed(self) -> None:
        if self.status == TaskStatus.DONE:
            raise TaskIsAlreadyCompleted

        self.status = TaskStatus.DONE
