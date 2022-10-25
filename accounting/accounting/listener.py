import asyncio
from functools import partial
import random

import asyncpg
from kafka import KafkaConsumer, KafkaProducer
from loguru import logger

from accounting.transactions.models import TransactionLogRecord
from accounting.db.uow import AccountingUoW, PgAccountingUoW
from accounting.tasks.models import Task, TaskStatus
from accounting.users.models import SystemRole, User
from common.events.business import tasks as tasks_be
from common.events.business.transactions import TransactionApplied, TransactionType
from common.events.cud import users as users_cud
from common.events.cud.tasks import TaskUpdatedPrices
from common.message_bus.kafka_consumer import EventSpec, HandlerRegistry, HandlerSpec, run_consumer
from common.message_bus.kafka_producer import make_mb_producer
from common.message_bus.protocols import MBProducer


async def handle_user_created(uow: AccountingUoW, event: users_cud.UserCreated) -> None:
    new_user = User(public_id=event.data['public_id'], role=SystemRole(event.data['role']))
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)
        await uow.commit()


async def handle_task_added(
    uow: AccountingUoW,
    trans_produce: MBProducer,
    cud_tasks_produce: MBProducer,
    event: tasks_be.TaskAdded,
) -> None:
    fee, profit = random.randint(10, 20), random.randint(20, 40)
    new_task = Task(
        public_id=event.data['public_id'],
        jira_id=event.data['jira_id'],
        description=event.data['description'],
        fee=fee,
        profit=profit,
    )
    async with uow:
        await uow.tasks.create(new_task)
        transaction = TransactionLogRecord(
            public_user_id=event.data['assignee_id'],
            type=TransactionType.WITHDRAWAL,
            description=f'Deduct assignment fee for task - {new_task.get_full_name()}',
            debit=0,
            credit=new_task.fee,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Created new task {!r} from cud event', new_task)
    logger.info('Applied new transaction {!r}', transaction)

    # Send CUD event with updated prices info
    upd_task = TaskUpdatedPrices(
        version=1,
        data={
            'public_id': new_task.public_id,
            'description': new_task.description,
            'assignee_id': event.data['assignee_id'],
            'jira_id': new_task.jira_id,
            'status': TaskStatus.OPEN,
            'fee': new_task.fee,
            'profit': new_task.profit,
        },
    )
    cud_tasks_produce(key=upd_task.data['assignee_id'], value=upd_task.json())

    # Send event that money were removed from user balance
    fee_event = TransactionApplied(
        version=1,
        data={
            'public_id': transaction.public_id,
            'public_user_id': event.data['assignee_id'],
            'type': transaction.type,
            'debit': transaction.debit,
            'credit': transaction.credit,
            'applied_at': transaction.created_at,
        },
    )
    trans_produce(key=event.data['assignee_id'], value=fee_event.json())


async def handle_task_assigned(uow: AccountingUoW, produce: MBProducer, event: tasks_be.TaskAssigned) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(event.data['public_id'])
        transaction = TransactionLogRecord(
            public_user_id=event.data['assignee_id'],
            type=TransactionType.WITHDRAWAL,
            description=f'Deduct assignment fee for task - {task.get_full_name()}',
            debit=0,
            credit=task.fee,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Applied new transaction {!r}', transaction)

    # Send event that money were removed from user balance
    fee_event = TransactionApplied(
        version=1,
        data={
            'public_id': transaction.public_id,
            'public_user_id': event.data['assignee_id'],
            'type': transaction.type,
            'debit': transaction.debit,
            'credit': transaction.credit,
            'applied_at': transaction.created_at,
        },
    )
    produce(key=event.data['assignee_id'], value=fee_event.json())


async def handle_task_completed(uow: AccountingUoW, produce: MBProducer, event: tasks_be.TaskCompleted) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(event.data['public_id'])
        transaction = TransactionLogRecord(
            public_user_id=event.data['assignee_id'],
            type=TransactionType.DEPOSIT,
            description=f'Add completion profit for task {task.get_full_name()}',
            debit=task.profit,
            credit=0,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Applied new transaction {!r}', transaction)

    # Send event that money were added to user balance
    profit_event = TransactionApplied(
        version=1,
        data={
            'public_id': transaction.public_id,
            'public_user_id': transaction.public_user_id,
            'type': transaction.type,
            'debit': transaction.debit,
            'credit': transaction.credit,
            'applied_at': transaction.created_at,
        },
    )
    produce(key=event.data['assignee_id'], value=profit_event.json())


async def handle_transaction_applied(event: TransactionApplied) -> None:
    match event.data['type']:
        case TransactionType.PAYMENT:
            # NOTE: here will be an actual payment logic
            logger.info('Sending real money to user via <payment method>')
        case _:
            pass


def init_handler_registry(uow: AccountingUoW, accounting_be: MBProducer, tasks_cud: MBProducer) -> HandlerRegistry:
    return {
        EventSpec(name='UserCreated', domain='users', version=1): HandlerSpec(
            model=users_cud.UserCreated,
            handler=partial(handle_user_created, uow),
        ),
        EventSpec(name='TaskAdded', domain='taskman', version=2): HandlerSpec(
            model=tasks_be.TaskAdded,
            handler=partial(handle_task_added, uow, accounting_be, tasks_cud),
        ),
        EventSpec(name='TaskAssigned', domain='taskman', version=1): HandlerSpec(
            model=tasks_be.TaskAssigned,
            handler=partial(handle_task_assigned, uow, accounting_be),
        ),
        EventSpec(name='TaskCompleted', domain='taskman', version=1): HandlerSpec(
            model=tasks_be.TaskCompleted,
            handler=partial(handle_task_completed, uow, accounting_be),
        ),
        EventSpec(name='TransactionApplied', domain='accounting', version=1): HandlerSpec(
            model=TransactionApplied,
            handler=handle_transaction_applied,
        ),
    }


async def poll_events() -> None:
    pool: asyncpg.Pool | None = await asyncpg.create_pool(
        dsn='postgres://postgres:password12345@localhost:5432',
        database='accounting',
    )
    if pool is None:
        raise ValueError('Connection to database failed, could not start service')

    topics = {'user-streaming', 'task-streaming', 'task-lifecycle', 'accounting'}

    uow = PgAccountingUoW(pool)
    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'], group_id='accounting')
    producer = KafkaProducer(bootstrap_servers=['localhost:9095'], linger_ms=2)
    accounting_be = make_mb_producer(producer, topic='accounting', sync=True)
    tasks_cud = make_mb_producer(producer, topic='task-streaming', sync=True)
    handlers = init_handler_registry(uow, accounting_be, tasks_cud)

    logger.info('Start listening for events on topics {}', topics)
    await run_consumer(consumer, handlers)


def start_poller():
    asyncio.run(poll_events())


if __name__ == '__main__':
    start_poller()
