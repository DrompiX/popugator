from fastapi import Depends, Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN

from users.models import User
from users.repo import UserNotFound, UserRepo
from users.router import get_repo

bearer_security = HTTPBearer(scheme_name='Bearer auth', auto_error=False)


async def do_auth(
    bearer_data: HTTPAuthorizationCredentials = Security(bearer_security),
    users_repo: UserRepo = Depends(get_repo),
) -> User:
    if bearer_data is None:
        raise HTTPException(HTTP_401_UNAUTHORIZED, detail='Auth info was not specified')

    try:
        return await users_repo.get_user(username=bearer_data.credentials)
    except UserNotFound:
        raise HTTPException(HTTP_403_FORBIDDEN, detail='Invalid auth credentials')
    except Exception as err:
        logger.exception('Authorization failed for bearer {}: {}', bearer_data, err)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal error during auth')
