from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    OPEN = 'open'
    DONE = 'done'

    def __repr__(self) -> str:
        return str(self)


class Task(BaseModel):
    public_id: str
    jira_id: str
    description: str
    status: TaskStatus
    fee: int = 0  # init as 0 if CUD event did not contain money info
    profit: int = 0  # init as 0 if CUD event did not contain money info
    completed_at: Optional[datetime] = None
