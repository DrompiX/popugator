from pydantic import BaseModel


class Task(BaseModel):
    public_id: str
    jira_id: str
    description: str
