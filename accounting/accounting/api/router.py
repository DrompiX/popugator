from fastapi import APIRouter, Depends, Request

from accounting.api.auth import authorize, parse_auth_info, AuthHeaders
from accounting.api.models import ManagementEarnedResponse, TransactionLogRecordOut, UserAccountInfoResponse

from accounting.db.uow import AccountingUoW
from accounting.users.models import ACCOUNTING_GURUS, TASK_DOERS_GROUP
from common.utils import generate_utc_dt, handle_general_exc

router = APIRouter(
    prefix='/accounts',
    tags=['accounts'],
)


@router.get(
    '/me',
    dependencies=[Depends(authorize(TASK_DOERS_GROUP))],
    response_model=UserAccountInfoResponse,
)
@handle_general_exc
async def get_user_account_info(r: Request, auth: AuthHeaders = Depends(parse_auth_info)):
    uow: AccountingUoW = r.app.state.uow
    async with uow:
        transactions = await uow.transactions.get_by_user_id(auth.user_public_id)
    total_debit, total_credit, log_view = 0, 0, []

    for transaction in transactions:
        total_debit += transaction.debit
        total_credit += transaction.credit
        log_view.append(
            TransactionLogRecordOut(
                description=transaction.description,
                debit=transaction.debit,
                credit=transaction.credit,
            )
        )

    return UserAccountInfoResponse(balance=total_debit - total_credit, log=log_view)


@router.get(
    '/stats/today',
    dependencies=[Depends(authorize(ACCOUNTING_GURUS))],
    response_model=ManagementEarnedResponse,
)
@handle_general_exc
async def get_money_stats_for_today(r: Request):
    today = generate_utc_dt().date()
    uow: AccountingUoW = r.app.state.uow
    async with uow:
        transactions = await uow.transactions.get_all_by_date(today)

    total_debit, total_credit = 0, 0
    for transaction in transactions:
        total_debit += transaction.debit
        total_credit += transaction.credit

    return ManagementEarnedResponse(money_earned=total_credit - total_debit)
