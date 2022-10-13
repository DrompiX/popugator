from functools import wraps
from typing import Any, Callable, Coroutine

from fastapi.exceptions import HTTPException
from loguru import logger


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
