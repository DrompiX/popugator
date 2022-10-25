from datetime import date, timedelta
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException

from analytics.api.auth import authorize
from analytics.api.models import CumulativeAnalytics, Period, TopTaskInfo
from analytics.db.uow import AnalyticsUoW
from analytics.users.models import SystemRole
from common.utils import handle_general_exc

router = APIRouter(
    prefix='/analytics',
    tags=['analytics'],
    dependencies=[Depends(authorize({SystemRole.ADMIN}))],
)


@router.get('/today', response_model=CumulativeAnalytics)
@handle_general_exc
async def get_todays_analytics(r: Request):
    uow: AnalyticsUoW = r.app.state.uow
    async with uow:
        user2balance = await uow.transactions.get_balance_by_user(date.today())
        popugs_in_debt = 0
        for balance in user2balance.values():
            if balance < 0:
                popugs_in_debt += 1

        earned = await uow.transactions.get_management_income(date.today(), date.today())

    return CumulativeAnalytics(management_earned=earned, negative_income_popugs=popugs_in_debt)


@router.get('/top_task/{period}', response_model=TopTaskInfo)
@handle_general_exc
async def get_most_expensive_task_for_period(r: Request, period: Period):
    uow: AnalyticsUoW = r.app.state.uow
    end_date = date.today()
    match period:
        case Period.DAY:
            start_date = date.today()
        case Period.WEEK:
            start_date = date.today() - timedelta(weeks=1)
        case Period.MONTH:
            start_date = date.today() - timedelta(weeks=1)

    async with uow:
        task = await uow.tasks.get_most_expensive(start_date, end_date)

    if task is None:
        raise HTTPException(404, 'No completed tasks for specified period')

    return TopTaskInfo(
        start_date=start_date,
        end_date=end_date,
        desctiption=task.description,
        price=task.profit,
    )
