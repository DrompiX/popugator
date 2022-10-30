from functools import partial
import random

from kafka import KafkaConsumer, KafkaProducer
from loguru import logger

from accounting.transactions.models import TransactionLogRecord
from accounting.db.uow import FakeUoW, AccountingUoW
from accounting.tasks.models import Task
from accounting.users.models import User
from common.events.base import Event
from common.events.business import tasks as tasks_be
from common.events.business.transactions import TransactionApplied, TransactionType
from common.events.cud import users as users_cud
from common.message_bus.kafka_consumer import EventSpec, HandlerRegistry, HandlerSpec, run_consumer
from common.message_bus.kafka_producer import make_mb_producer
from common.message_bus.protocols import MBProducer


async def handle_user_created(uow: AccountingUoW, event: users_cud.UserCreated) -> None:
    new_user = User(public_id=event.public_id)
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)
        await uow.commit()


async def handle_task_added(uow: AccountingUoW, produce: MBProducer, event: tasks_be.TaskAdded) -> None:
    fee, profit = random.randint(10, 20), random.randint(20, 40)
    new_task = Task(
        public_id=event.public_id,
        jira_id=event.jira_id,
        description=event.description,
        fee=fee,
        profit=profit,
    )
    async with uow:
        await uow.tasks.create(new_task)
        transaction = TransactionLogRecord(
            public_user_id=event.assignee_id,
            description=f'Deduct assignment fee for task - {new_task.get_full_name()}',
            debit=0,
            credit=new_task.fee,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    # Send event that money were removed from user balance
    fee_event = Event(
        name='TransactionApplied',
        data=TransactionApplied(
            public_user_id=event.assignee_id,
            type=TransactionType.WITHDRAWAL,
            amount=new_task.fee,
            applied_at=transaction.created_at,
        ),
    )
    produce(key=event.assignee_id, value=fee_event.json())

    logger.info('Created new task {!r} from cud event', new_task)
    logger.info('Applied new transaction {!r}', transaction)


async def handle_task_assigned(uow: AccountingUoW, produce: MBProducer, event: tasks_be.TaskAssigned) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(event.public_id)
        transaction = TransactionLogRecord(
            public_user_id=event.assignee_id,
            description=f'Deduct assignment fee for task - {task.get_full_name()}',
            debit=0,
            credit=task.fee,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Applied new transaction {!r}', transaction)

    # Send event that money were removed from user balance

    fee_event = Event(
        name='TransactionApplied',
        data=TransactionApplied(
            public_user_id=event.assignee_id,
            type=TransactionType.WITHDRAWAL,
            amount=task.fee,
            applied_at=transaction.created_at,
        ),
    )
    produce(key=event.assignee_id, value=fee_event.json())


async def handle_task_completed(uow: AccountingUoW, produce: MBProducer, event: tasks_be.TaskCompleted) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(event.public_id)
        transaction = TransactionLogRecord(
            public_user_id=event.assignee_id,
            description=f'Add completion profit for task {task.get_full_name()}',
            debit=task.profit,
            credit=0,
        )
        await uow.transactions.add(transaction)
        await uow.commit()

    logger.info('Applied new transaction {!r}', transaction)

    # Send event that money were added to user balance
    profit_event = Event(
        name='TransactionApplied',
        data=TransactionApplied(
            public_user_id=event.assignee_id,
            type=TransactionType.PROFIT,
            amount=task.profit,
            applied_at=transaction.created_at,
        ),
    )
    produce(key=event.assignee_id, value=profit_event.json())


async def handle_transaction_applied(event: TransactionApplied) -> None:
    match TransactionApplied.type:
        case TransactionType.PAYMENT:
            # NOTE: here will be an actual payment logic
            logger.info('Sending real money to user via <payment method>')
        case _:
            pass


def init_handler_registry(uow: AccountingUoW, accounting_be: MBProducer) -> HandlerRegistry:
    return {
        EventSpec(name='UserCreated', version=1): HandlerSpec(
            model=users_cud.UserCreated,
            handler=partial(handle_user_created, uow),
        ),
        EventSpec(name='TaskAdded', version=2): HandlerSpec(
            model=tasks_be.TaskAdded,
            handler=partial(handle_task_added, uow, accounting_be),
        ),
        EventSpec(name='TaskAssigned', version=1): HandlerSpec(
            model=tasks_be.TaskAssigned,
            handler=partial(handle_task_assigned, uow, accounting_be),
        ),
        EventSpec(name='TaskCompleted', version=1): HandlerSpec(
            model=tasks_be.TaskCompleted,
            handler=partial(handle_task_completed, uow, accounting_be),
        ),
        EventSpec(name='TransactionApplied', version=1): HandlerSpec(
            model=TransactionApplied,
            handler=handle_transaction_applied,
        ),
    }


if __name__ == '__main__':
    uow = FakeUoW()
    topics = {'user-streaming', 'task-streaming', 'task-lifecycle', 'accounting'}

    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
    producer = KafkaProducer(bootstrap_servers=['localhost:9095'], linger_ms=2)

    accounting_be = make_mb_producer(producer, topic='accounting', sync=True)
    handlers = init_handler_registry(uow, accounting_be)

    logger.info('Start polling events on topics {}', topics)
    run_consumer(consumer, handlers)
