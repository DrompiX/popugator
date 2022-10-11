from pydantic import BaseModel


class UserCreated(BaseModel):
    public_id: str
    username: str
    role: str
