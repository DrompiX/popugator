from datetime import datetime
from functools import wraps
from typing import Any, Callable, Coroutine
from uuid import uuid4

from fastapi.exceptions import HTTPException
from loguru import logger


def generate_uuid() -> str:
    return uuid4().hex[:12]


def generate_utc_ts() -> int:
    return int(datetime.utcnow().timestamp())


def generate_utc_dt() -> datetime:
    return datetime.utcnow()


def handle_general_exc(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(func)
    async def _wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as err:
            logger.exception('{} failed: {}', func.__name__, err)
            raise HTTPException(
                status_code=500,
                detail={
                    'exc_name': err.__class__.__name__,
                    'exc_info': str(err),
                },
            )

    return _wrapped
