from enum import Enum
from pydantic import BaseModel, Field

from common.utils import generate_uuid


class SystemRole(str, Enum):
    MANAGER = 'manager'
    ADMIN = 'admin'
    WORKER = 'worker'
    ACCOUNTANT = 'accountant'

    def __repr__(self) -> str:
        return str(self)


class User(BaseModel):
    username: str
    public_id: str = Field(default_factory=generate_uuid)
    role: SystemRole
