import asyncio
from dataclasses import dataclass
import json
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


def run_consumer(consumer: KafkaConsumer, handlers: HandlerRegistry) -> None:
    loop = asyncio.new_event_loop()

    msg: ConsumerRecord
    for msg in consumer:
        try:
            json_event = json.loads(cast(str, msg.value))
        except json.JSONDecodeError:
            logger.exception('Could not parse event from msg {}', msg)
            continue

        try:
            process_event(json_event, handlers, loop)
        except HandlerNotFound as err:
            logger.warning('Consumer could not handle valid event: {}', err)
        except Exception as err:
            logger.exception('Failed to process event({}): {}', json_event, err)


def process_event(
    json_event: dict[str, Any],
    handlers: HandlerRegistry,
    loop: asyncio.AbstractEventLoop,
) -> None:
    match json_event:
        case {'name': name, 'domain': domain, 'version': version, 'data': event_data}:
            event_spec = EventSpec(name, domain, version)
        case _:
            raise ValueError('Event does not contain meta info with name, domain, version or data')

    handler_spec = handlers.get(event_spec)
    if handler_spec is None:
        raise HandlerNotFound(f'No handler for event {json_event}')

    event_data = handler_spec.model.parse_obj(event_data)
    loop.run_until_complete(handler_spec.handler(event_data))
