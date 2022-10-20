from fastapi import APIRouter, Depends, Request

from analytics.api.auth import authorize
from analytics.api.models import CumulativeAnalytics, Period, TopTaskInfo
from analytics.db.uow import AnalyticsUoW
from analytics.users.models import SystemRole
from common.utils import handle_general_exc

router = APIRouter(
    prefix='/analytics',
    tags=['analytics'],
)


@router.get(
    '/today',
    dependencies=[Depends(authorize({SystemRole.ADMIN}))],
    response_model=CumulativeAnalytics,
)
@handle_general_exc
async def get_todays_analytics(r: Request):
    _uow: AnalyticsUoW = r.app.state.uow
    return CumulativeAnalytics(management_earned=0, negative_income_popugs=0)


@router.get(
    '/top_task/{period}',
    dependencies=[Depends(authorize({SystemRole.ADMIN}))],
    response_model=list[TopTaskInfo],
)
@handle_general_exc
async def get_most_expensive_task_for_period(r: Request, period: Period):
    _uow: AnalyticsUoW = r.app.state.uow
    result: list[TopTaskInfo] = []
    return result
