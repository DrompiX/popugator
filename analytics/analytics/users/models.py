from enum import Enum
from pydantic import BaseModel


class SystemRole(str, Enum):
    MANAGER = 'manager'
    ADMIN = 'admin'
    WORKER = 'worker'
    ACCOUNTANT = 'accountant'

    def __repr__(self) -> str:
        return str(self)


class User(BaseModel):
    username: str
    public_id: str
    role: SystemRole


TOP_MAN_GROUP = {SystemRole.ADMIN, SystemRole.MANAGER}
TASK_DOERS_GROUP = {SystemRole.WORKER}
ACCOUNTING_GURUS = {SystemRole.ADMIN, SystemRole.ACCOUNTANT}
