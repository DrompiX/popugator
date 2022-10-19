from pydantic import BaseModel, Field
from common.utils import generate_utc_ts, generate_uuid


class Event(BaseModel):
    created_at: int = Field(default_factory=generate_utc_ts)
    id: str = Field(default_factory=generate_uuid)
    version: int = 1
    name: str
    data: BaseModel
