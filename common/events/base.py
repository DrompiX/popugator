from typing import TypedDict
from pydantic import BaseModel, Field
from common.utils import generate_utc_ts, generate_uuid


class EventData(TypedDict):
    pass


class Event(BaseModel):
    created_at: int = Field(default_factory=generate_utc_ts)
    id: str = Field(default_factory=generate_uuid)
    version: int
    name: str
    domain: str
    data: EventData
