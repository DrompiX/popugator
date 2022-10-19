from pydantic import BaseModel


class AddTaskRequest(BaseModel):
    description: str


class AddTaskResponse(BaseModel):
    public_task_id: str


class APIError(BaseModel):
    detail: str
