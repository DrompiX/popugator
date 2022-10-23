from datetime import timedelta

from loguru import logger

from accounting.db.uow import AccountingUoW
from accounting.transactions.models import TransactionLogRecord
from common.events.business.transactions import TransactionApplied, TransactionType
from common.message_bus.protocols import MBProducer
from common.utils import generate_utc_dt


async def perform_reset(uow: AccountingUoW, accounting_be: MBProducer) -> None:
    yesterday = generate_utc_dt().date() - timedelta(days=1)

    async with uow:
        users = await uow.users.get_all()
        balances = await uow.transactions.get_balance_by_user(yesterday)

    for user in users:
        if user.public_id not in balances:
            # User has no balance updates for today
            continue

        balance = balances[user.public_id]
        if balance <= 0:
            logger.info(
                'User {} balance is not positive, skipping payment for {}',
                user.public_id,
                yesterday,
            )
            continue

        payout = TransactionLogRecord(
            public_user_id=user.public_id, description='Daily payout', debit=0, credit=balance
        )
        await uow.transactions.add(payout)

        payment_event = TransactionApplied(
            version=1,
            data={
                'public_user_id': user.public_id,
                'type': TransactionType.PAYMENT,
                'amount': balance,
                'applied_at': payout.created_at,
            },
        )
        accounting_be(key=user.public_id, value=payment_event.json())
