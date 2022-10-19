from pydantic import BaseModel


class TaskCreated(BaseModel):
    public_id: str
    description: str
    assignee_id: str
    status: str


class TaskUpdated(TaskCreated):
    pass
