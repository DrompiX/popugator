import asyncio
from datetime import timedelta

import asyncpg
from kafka import KafkaProducer
from loguru import logger

from accounting.db.uow import AccountingUoW, PgAccountingUoW
from accounting.transactions.models import TransactionLogRecord
from common.events.business.transactions import TransactionApplied, TransactionType
from common.message_bus.protocols import MBProducer
from common.message_bus.kafka_producer import make_mb_producer
from common.utils import generate_utc_dt


async def perform_reset(uow: AccountingUoW, accounting_be: MBProducer) -> None:
    yesterday = generate_utc_dt().date() - timedelta(days=1)

    events: list[TransactionApplied] = []
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
                public_user_id=user.public_id,
                type=TransactionType.PAYMENT,
                description='Daily payout',
                debit=0,
                credit=balance,
            )
            await uow.transactions.add(payout)

            events.append(
                TransactionApplied(
                    version=1,
                    data={
                        'public_id': payout.public_id,
                        'public_user_id': payout.public_user_id,
                        'type': payout.type,
                        'debit': payout.debit,
                        'credit': payout.credit,
                        'applied_at': payout.created_at,
                    },
                )
            )

        await uow.commit()

    for event in events:
        accounting_be(key=event.data['public_user_id'], value=event.json())


async def run():
    pool: asyncpg.Pool | None = await asyncpg.create_pool(
        dsn='postgres://postgres:password12345@localhost:5432',
        database='accounting',
    )
    if pool is None:
        raise ValueError('Connection to database failed, could not start service')

    producer = KafkaProducer(bootstrap_servers=['localhost:9095'], linger_ms=2)
    accounting_be = make_mb_producer(producer, topic='accounting', sync=True)

    uow = PgAccountingUoW(pool)
    await perform_reset(uow, accounting_be)


if __name__ == '__main__':
    asyncio.run(run())
