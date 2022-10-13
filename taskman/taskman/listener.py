import asyncio
import json
from typing import cast

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from loguru import logger

from common.events.base import Event
from common.events.cud.users import UserCreated
from taskman.db.uow import FakeUoW, TaskmanUoW
from taskman.users.models import SystemRole, User


async def handle_user_created(uow: TaskmanUoW, event: UserCreated) -> None:
    new_user = User(username=event.username, public_id=event.public_id, role=SystemRole(event.role))
    async with uow:
        await uow.users.create_user(user=new_user)
        logger.info('Created new user {!r} from cud event', new_user)


def launch(uow: TaskmanUoW):
    loop = asyncio.new_event_loop()
    topics = {'user-streaming'}
    consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
    msg: ConsumerRecord
    logger.info('Start listening for events on topics {}', topics)
    for msg in consumer:
        logger.info('Received new message: {}', msg)
        try:
            json_event = json.loads(cast(str, msg.value))
            event = Event.parse_obj(json_event)
        except (json.JSONDecodeError, ValueError):
            logger.exception('Could not parse event from msg {}', msg)
            continue

        try:
            match event.event_name:
                case 'UserCreated':
                    user_created = UserCreated.parse_obj(json_event['data'])
                    loop.run_until_complete(handle_user_created(uow, user_created))
                case _:
                    logger.warning('Received unknow event_name: {}', event.event_name)
                    continue
        except Exception:
            logger.exception('Failed to process event: {}', event)


if __name__ == '__main__':
    try:
        uow = FakeUoW()
        launch(uow)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        exit(1)
