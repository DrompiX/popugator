import asyncio
from functools import partial

import asyncpg
from kafka import KafkaConsumer
from loguru import logger

from common.events.cud.users import UserCreated
from taskman.db.uow import PgTaskmanUoW, TaskmanUoW
from taskman.users.models import SystemRole, User
from common.message_bus.kafka_consumer import EventSpec, HandlerRegistry, HandlerSpec, run_consumer


async def handle_user_created(uow: TaskmanUoW, event: UserCreated) -> None:
    new_user = User(
        username=event.data['username'],
        public_id=event.data['public_id'],
        role=SystemRole(event.data['role']),
    )
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)
        await uow.commit()


async def poll_events() -> None:
    pool: asyncpg.Pool | None = await asyncpg.create_pool(
        dsn='postgres://postgres:password12345@localhost:5432',
        database='taskman',
    )
    if pool is None:
        raise ValueError('Connection to database failed, could not start service')

    uow = PgTaskmanUoW(pool)
    topics = {'user-streaming'}

    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'], group_id='taskman')
    handlers: HandlerRegistry = {
        EventSpec(name='UserCreated', version=1, domain='users'): HandlerSpec(
            model=UserCreated,
            handler=partial(handle_user_created, uow),
        ),
    }

    logger.info('Start listening for events on topics {}', topics)
    await run_consumer(consumer, handlers)


def start_poller():
    asyncio.run(poll_events())


if __name__ == '__main__':
    start_poller()
