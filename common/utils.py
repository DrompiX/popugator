from datetime import datetime
from uuid import uuid4


def generate_uuid() -> str:
    return uuid4().hex[:12]


def generate_utc_ts() -> int:
    return int(datetime.utcnow().timestamp())
