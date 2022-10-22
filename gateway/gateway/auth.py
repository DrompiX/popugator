from fastapi import Request, Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN

from gateway.users.models import User
from gateway.users.repo import UserNotFound, UserRepo

bearer_security = HTTPBearer(scheme_name='Bearer auth', auto_error=False)


async def do_auth(
    request: Request,
    bearer_data: HTTPAuthorizationCredentials = Security(bearer_security),
) -> User:
    users_repo: UserRepo = request.app.state.users_repo
    if bearer_data is None:
        raise HTTPException(HTTP_401_UNAUTHORIZED, detail='Auth info was not specified')

    try:
        return await users_repo.get_by_username(username=bearer_data.credentials)
    except UserNotFound:
        raise HTTPException(HTTP_403_FORBIDDEN, detail='Invalid auth credentials')
    except Exception as err:
        logger.exception('Authorization failed for bearer {}: {}', bearer_data, err)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal error during auth')
