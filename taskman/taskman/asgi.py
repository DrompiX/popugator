import os
import sys
from threading import Thread
from typing import Any

import asyncpg
from fastapi import FastAPI
from loguru import logger

from common.message_bus.kafka_producer import get_kafka_producer, make_mb_producer
from taskman import listener
from taskman.db.uow import PgTaskmanUoW
from taskman.api.router import router

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True, diagnose=False)


def preconfigure(app: FastAPI) -> Any:
    async def async_launch():
        logger.info('Configuring service...')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        pool: asyncpg.Pool | None = await asyncpg.create_pool(
            dsn=f'postgres://postgres:password12345@{host}:5432',
            database='taskman',
        )
        if pool is None:
            raise ValueError('Connection to database failed, could not start service')

        app.state.uow = PgTaskmanUoW(pool)

        # Configure message broker
        kafka_srv = os.getenv('KAFKA_ADDR', 'localhost:29092')
        kafka_producer = get_kafka_producer([kafka_srv], linger_ms=2)
        app.state.tasks_cud = make_mb_producer(kafka_producer, topic='task-streaming', sync=False)
        app.state.tasks_be = make_mb_producer(kafka_producer, topic='task-lifecycle', sync=False)

        # Start event consumer
        app.state.listener = Thread(target=listener.start_poller, daemon=True)
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
