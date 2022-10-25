import asyncio
from datetime import datetime
from functools import partial

import asyncpg
from kafka import KafkaConsumer
from loguru import logger

from analytics.db.uow import AnalyticsUoW, PgAnalyticsUoW
from analytics.tasks.models import Task, TaskStatus
from analytics.tasks.repo import TaskNotFound
from analytics.transactions.models import TransactionLogRecord
from analytics.users.models import SystemRole, User
from common.events.business import transactions as trans_be
from common.events.cud import users as users_cud, tasks as tasks_cud
from common.message_bus.kafka_consumer import EventSpec, HandlerRegistry, HandlerSpec, run_consumer


async def handle_user_created(uow: AnalyticsUoW, event: users_cud.UserCreated) -> None:
    new_user = User(public_id=event.data['public_id'], role=SystemRole(event.data['role']))
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)
        await uow.commit()


async def handle_task_created(uow: AnalyticsUoW, event: tasks_cud.TaskCreated) -> None:
    new_task = Task(
        public_id=event.data['public_id'],
        description=event.data['description'],
        jira_id=event.data['jira_id'],
        status=TaskStatus(event.data['status']),
    )
    async with uow:
        await uow.tasks.create(new_task)
        await uow.commit()

    logger.info('Created new task {!r} from cud event', new_task)


async def handle_task_updated(uow: AnalyticsUoW, event: tasks_cud.TaskUpdated) -> None:
    new_status = TaskStatus(event.data['status'])
    task_upd = Task(
        public_id=event.data['public_id'],
        description=event.data['description'],
        jira_id=event.data['jira_id'],
        status=new_status,
        completed_at=datetime.fromtimestamp(event.created_at) if new_status == TaskStatus.DONE else None,
    )
    async with uow:
        try:
            # Avoid task prices override to 0s if taskman event arrives after accounting one
            existing_task = await uow.tasks.get_by_id(task_upd.public_id)
            task_upd.fee = existing_task.fee
            task_upd.profit = existing_task.profit
        except TaskNotFound:
            pass

        await uow.tasks.update(task_upd)
        await uow.commit()

    logger.info('Update task {!r} by cud event', task_upd)


async def handle_task_updated_prices(uow: AnalyticsUoW, event: tasks_cud.TaskUpdatedPrices) -> None:
    new_status = TaskStatus(event.data['status'])
    task_upd = Task(
        public_id=event.data['public_id'],
        description=event.data['description'],
        jira_id=event.data['jira_id'],
        status=new_status,
        fee=event.data['fee'],
        profit=event.data['profit'],
        completed_at=datetime.fromtimestamp(event.created_at) if new_status == TaskStatus.DONE else None,
    )
    async with uow:
        await uow.tasks.update(task_upd)
        await uow.commit()

    logger.info('Update task with prices {!r} by cud event', task_upd)


async def handle_transaction_applied(uow: AnalyticsUoW, event: trans_be.TransactionApplied) -> None:
    transaction = TransactionLogRecord(
        public_id=event.data['public_id'],
        public_user_id=event.data['public_user_id'],
        type=event.data['type'],
        credit=event.data['credit'],
        debit=event.data['debit'],
        created_at=event.data['applied_at'],
    )
    async with uow:
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Added new transaction {!r}', transaction)


def init_handler_registry(uow: AnalyticsUoW) -> HandlerRegistry:
    return {
        EventSpec(name='UserCreated', domain='users', version=1): HandlerSpec(
            model=users_cud.UserCreated,
            handler=partial(handle_user_created, uow),
        ),
        EventSpec(name='TaskCreated', domain='taskman', version=2): HandlerSpec(
            model=tasks_cud.TaskCreated,
            handler=partial(handle_task_created, uow),
        ),
        EventSpec(name='TaskUpdated', domain='taskman', version=2): HandlerSpec(
            model=tasks_cud.TaskUpdated,
            handler=partial(handle_task_updated, uow),
        ),
        EventSpec(name='TaskUpdated', domain='accounting', version=1): HandlerSpec(
            model=tasks_cud.TaskUpdatedPrices,
            handler=partial(handle_task_updated_prices, uow),
        ),
        EventSpec(name='TransactionApplied', domain='accounting', version=1): HandlerSpec(
            model=trans_be.TransactionApplied,
            handler=partial(handle_transaction_applied, uow),
        ),
    }


async def poll_events() -> None:
    pool: asyncpg.Pool | None = await asyncpg.create_pool(
        dsn='postgres://postgres:password12345@localhost:5432',
        database='analytics',
    )
    if pool is None:
        raise ValueError('Connection to database failed, could not start service')

    topics = {'user-streaming', 'task-streaming', 'accounting'}

    uow = PgAnalyticsUoW(pool)
    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'], group_id='analytics')
    handlers = init_handler_registry(uow)

    logger.info('Start listening for events on topics {}', topics)
    await run_consumer(consumer, handlers)


def start_poller():
    asyncio.run(poll_events())


if __name__ == '__main__':
    start_poller()
