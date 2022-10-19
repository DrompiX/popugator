import asyncio
from dataclasses import dataclass
import json
from typing import Any, Type, cast
from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord
from loguru import logger
from pydantic import BaseModel

from common.events.base import Event
from common.message_bus.protocols import EventHandler


class HandlerNotFound(Exception):
    pass


@dataclass(frozen=True)
class EventSpec:
    name: str
    version: int


@dataclass(frozen=True)
class HandlerSpec:
    model: Type[BaseModel]
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
    parsed_event = Event.parse_obj(json_event)
    handler_spec = handlers.get(EventSpec(parsed_event.name, parsed_event.version))
    if handler_spec is None:
        raise HandlerNotFound(f'No handler for event {json_event}')

    event_data = handler_spec.model.parse_obj(json_event['data'])
    loop.run_until_complete(handler_spec.handler(event_data))
