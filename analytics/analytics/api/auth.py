from typing import Awaitable, Callable
from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from pydantic import BaseModel

from loguru import logger

from analytics.users.models import SystemRole
from analytics.users.repo import UserNotFound


class AuthHeaders(BaseModel):
    user_role: SystemRole
    user_public_id: str


def parse_auth_info(r: Request) -> AuthHeaders:
    try:
        return AuthHeaders.parse_obj(r.headers)
    except ValueError:
        logger.exception('Bad auth info in headers {}', r.headers)
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='')


def authorize(allowed: set[SystemRole]) -> Callable[[Request], Awaitable[None]]:
    async def _inner(r: Request) -> None:
        auth_info = parse_auth_info(r)
        if auth_info.user_role not in allowed:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN)

        try:
            db_user = await r.app.state.uow.users.get_user(auth_info.user_public_id)
        except UserNotFound:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

        if db_user.role != auth_info.user_role:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    return _inner
