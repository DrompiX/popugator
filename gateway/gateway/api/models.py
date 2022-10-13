from pydantic import BaseModel

from gateway.users.models import SystemRole


class CreateUserRequest(BaseModel):
    username: str
    role: SystemRole


class CreateUserResponse(BaseModel):
    detail: str = 'ok'


class APIError(BaseModel):
    detail: str
