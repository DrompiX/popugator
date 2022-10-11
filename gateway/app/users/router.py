from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from common.message_bus.protocols import MBProducer

from users.api_models import APIError, CreateUserRequest, CreateUserResponse
from users.models import User
from users.repo import UserAlreadyExists, UserNotFound, UserRepo
from users import services

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={
        404: {'model': APIError},
        500: {'model': APIError},
    },
)


@router.post('/', response_model=CreateUserResponse)
async def create_user(request: Request, req: CreateUserRequest):
    repo: UserRepo = request.app.state.user_repo
    produce_func: MBProducer = request.app.state.user_stream_producer

    logger.info('Creating user with name {} and role {}', req.username, req.role)
    user = User(username=req.username, role=req.role)
    try:
        await services.create_user(repo, produce_func, user)
    except UserAlreadyExists as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        logger.exception('User creation failed: {}', err)
        raise HTTPException(status_code=500, detail='Unexpected internal error occurred')

    return CreateUserResponse()


@router.get('/{user_id}', response_model=User)
async def get_user(request: Request, user_id: str):
    repo: UserRepo = request.app.state.user_repo
    try:
        return await services.get_user(repo, username=user_id)
    except UserNotFound as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        logger.exception('Get user failed: {}', err)
        raise HTTPException(status_code=500, detail='Unexpected internal error occurred')
