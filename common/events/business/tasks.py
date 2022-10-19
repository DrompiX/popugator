from pydantic import BaseModel


class TaskAdded(BaseModel):
    public_task_id: str
    task_status: str
    assignee_id: str


class TaskAssigned(BaseModel):
    public_task_id: str
    assignee_id: str


class TaskCompleted(BaseModel):
    public_task_id: str
    assignee_id: str
