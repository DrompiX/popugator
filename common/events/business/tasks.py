from pydantic import BaseModel


class TaskAdded(BaseModel):
    public_id: str
    description: str
    assignee_id: str


class TaskAssigned(BaseModel):
    public_id: str
    assignee_id: str


class TaskCompleted(BaseModel):
    public_id: str
    assignee_id: str
