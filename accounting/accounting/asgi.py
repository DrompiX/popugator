import sys
from threading import Thread
from typing import Any

from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
from loguru import logger

from accounting import listener
from accounting.db.uow import FakeUoW
from accounting.api.router import router
from common.message_bus.kafka_consumer import run_consumer
from common.message_bus.kafka_producer import make_mb_producer

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True, diagnose=False)


def preconfigure(app: FastAPI) -> Any:
    async def async_launch():
        logger.info('Configuring service...')
        app.state.uow = FakeUoW()
        kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9095'], linger_ms=2)
        app.state.accounting_be = make_mb_producer(kafka_producer, topic='accounting')

        # initialize event consuming part
        topics = {'user-streaming', 'task-streaming', 'task-lifecycle'}
        consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
        handlers = listener.init_handler_registry(app.state.uow, app.state.accounting_be)
        app.state.listener = Thread(target=run_consumer, args=(consumer, handlers), daemon=True)
        app.state.listener.start()

        logger.info('Done with configuration')

    return async_launch


def cleanup(app: FastAPI) -> Any:
    async def async_shutdown():
        logger.info('Shutting down service...')
        logger.info('Done with shutting down')

    return async_shutdown


def get_application() -> FastAPI:
    app = FastAPI()
    app.add_event_handler('startup', preconfigure(app))
    app.add_event_handler('shutdown', cleanup(app))
    app.include_router(router)
    return app


app = get_application()
