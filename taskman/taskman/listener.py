from functools import partial

from kafka import KafkaConsumer
from loguru import logger

from common.events.cud.users import UserCreated
from taskman.db.uow import FakeUoW, TaskmanUoW
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


def poll_events(uow: TaskmanUoW) -> None:
    topics = {'user-streaming'}
    logger.info('Start listening for events on topics {}', topics)

    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
    handlers: HandlerRegistry = {
        EventSpec(name='UserCreated', version=1, domain='users'): HandlerSpec(
            model=UserCreated,
            handler=partial(handle_user_created, uow),
        ),
    }
    run_consumer(consumer, handlers)


if __name__ == '__main__':
    uow = FakeUoW()
    try:
        poll_events(uow)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        exit(1)
