from pydantic import BaseModel, Field
from common.utils import generate_utc_ts, generate_uuid


class Event(BaseModel):
    event_id: str = Field(default_factory=generate_uuid)
    created_at: int = Field(default_factory=generate_utc_ts)
    event_name: str
    data: BaseModel
