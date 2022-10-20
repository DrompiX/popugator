from pydantic import BaseModel, validator


class AddTaskRequest(BaseModel):
    jira_id: str
    description: str

    @validator('description')
    def check_no_jira_id_in_description(cls, value: str) -> str:
        if '[' in value:
            raise ValueError('Jira ID should not be specified in description, use dedicated field')
        return value


class AddTaskResponse(BaseModel):
    public_task_id: str


class APIError(BaseModel):
    detail: str
