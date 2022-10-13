from pydantic import BaseModel


class TaskAdded(BaseModel):
    task_id: str
    task_status: str
    assignee: str


class TaskAssigned(BaseModel):
    task_id: str
    new_assignee: str


class TaskCompleted(BaseModel):
    task_id: str
