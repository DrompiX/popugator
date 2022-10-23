import json
from dataclasses import dataclass
from typing import Any, Type, cast

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from loguru import logger

from common.events.base import Event
from common.message_bus.protocols import EventHandler


class HandlerNotFound(Exception):
    pass


@dataclass(frozen=True)
class EventSpec:
    name: str
    domain: str
    version: int


@dataclass(frozen=True)
class HandlerSpec:
    model: Type[Event]
    handler: EventHandler


HandlerRegistry = dict[EventSpec, HandlerSpec]


async def run_consumer(consumer: KafkaConsumer, handlers: HandlerRegistry) -> None:
    msg: ConsumerRecord
    for msg in consumer:
        try:
            json_event = json.loads(cast(str, msg.value))
        except json.JSONDecodeError:
            logger.exception('Could not parse event from msg {}', msg)
            continue

        try:
            await process_event(json_event, handlers)
            logger.info('Consumed from topic {} message {}', msg.topic, json_event)
        except HandlerNotFound as err:
            logger.warning('Consumer could not handle valid event: {}', err)
        except Exception as err:
            logger.exception('Failed to process event({}): {}', json_event, err)


async def process_event(
    json_event: dict[str, Any],
    handlers: HandlerRegistry,
) -> None:
    match json_event:
        case {'name': name, 'domain': domain, 'version': version}:
            event_spec = EventSpec(name, domain, version)
        case _:
            raise ValueError('Event does not contain meta info with name, domain, version or data')

    handler_spec = handlers.get(event_spec)
    if handler_spec is None:
        raise HandlerNotFound(f'No handler for event {json_event}')

    event_data = handler_spec.model.parse_obj(json_event)
    await handler_spec.handler(event_data)
