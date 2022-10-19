from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from taskman.api.auth import authorize, parse_auth_info, AuthHeaders
from taskman.api.utils import handle_general_exc
from taskman.tasks import services
from taskman.api.models import APIError, AddTaskRequest, AddTaskResponse
from taskman.tasks.models import Task, UnassignedTask
from taskman.db.uow import TaskmanUoW
from taskman.users.models import TASK_DOERS_GROUP, TOP_MAN_GROUP

router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
    responses={
        404: {'model': APIError},
        500: {'model': APIError},
    },
)


@router.post('')
@handle_general_exc
async def add_task(r: Request, data: AddTaskRequest) -> AddTaskResponse:
    tasks_cud, tasks_be = r.app.state.tasks_cud, r.app.state.tasks_be
    unassigned = UnassignedTask(description=data.description)
    new_task = await services.add_task(r.app.state.uow, tasks_cud, tasks_be, unassigned)
    return AddTaskResponse(public_task_id=new_task.public_id)


@router.put('/shuffle', dependencies=[Depends(authorize(TOP_MAN_GROUP))])
@handle_general_exc
async def shuffle_tasks(r: Request):
    await services.shuffle_tasks(r.app.state.uow, r.app.state.tasks_be, r.app.state.tasks_cud)
    return JSONResponse(content={'detail': 'ok'}, status_code=200)


@router.put('/{task_id}/complete', dependencies=[Depends(authorize(TASK_DOERS_GROUP))])
@handle_general_exc
async def complete_task(r: Request, task_id: str, auth_info: AuthHeaders = Depends(parse_auth_info)):
    await services.complete_task(
        r.app.state.uow,
        r.app.state.tasks_be,
        r.app.state.tasks_cud,
        task_id,
        auth_info.user_public_id,
    )
    return JSONResponse(content={'detail': 'ok'}, status_code=200)


@router.get('', response_model=list[Task])
@handle_general_exc
async def get_all_tasks(r: Request) -> list[Task]:
    uow: TaskmanUoW = r.app.state.uow
    async with uow:
        return await uow.tasks.get_all()


@router.get('/{task_id}', response_model=Task)
@handle_general_exc
async def get_task_by_id(r: Request, task_id: str) -> Task:
    uow: TaskmanUoW = r.app.state.uow
    async with uow:
        return await uow.tasks.get_by_id(task_id)
