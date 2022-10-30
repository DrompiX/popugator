from functools import partial

from kafka import KafkaConsumer
from loguru import logger

from analytics.db.uow import FakeUoW, AnalyticsUoW
from analytics.tasks.models import Task
from analytics.users.models import User
from common.events.business import transactions as trans_be
from common.events.cud import users as users_cud, tasks as tasks_cud
from common.message_bus.kafka_consumer import EventSpec, HandlerRegistry, HandlerSpec, run_consumer


async def handle_user_created(uow: AnalyticsUoW, event: users_cud.UserCreated) -> None:
    new_user = User(public_id=event.public_id)
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)
        await uow.commit()


async def handle_task_created(uow: AnalyticsUoW, event: tasks_cud.TaskCreated) -> None:
    new_task = Task(public_id=event.public_id, description=event.description, jira_id=event.jira_id)
    async with uow:
        await uow.tasks.create(new_task)
        await uow.commit()

    logger.info('Created new task {!r} from cud event', new_task)


async def handle_transaction_applied(event: trans_be.TransactionApplied) -> None:
    pass


def init_handler_registry(uow: AnalyticsUoW) -> HandlerRegistry:
    return {
        EventSpec(name='UserCreated', version=1): HandlerSpec(
            model=users_cud.UserCreated,
            handler=partial(handle_user_created, uow),
        ),
        EventSpec(name='TaskCreated', version=2): HandlerSpec(
            model=tasks_cud.TaskCreated,
            handler=partial(handle_task_created, uow),
        ),
        EventSpec(name='TransactionApplied', version=1): HandlerSpec(
            model=trans_be.TransactionApplied,
            handler=handle_transaction_applied,
        ),
    }


if __name__ == '__main__':
    uow = FakeUoW()
    topics = {'user-streaming', 'task-streaming', 'task-lifecycle', 'accounting'}

    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
    handlers = init_handler_registry(uow)

    logger.info('Start polling events on topics {}', topics)
    run_consumer(consumer, handlers)
