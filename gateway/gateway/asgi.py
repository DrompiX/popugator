import os
import sys
from typing import Callable, Coroutine

import asyncpg
import httpx
from fastapi import FastAPI
from loguru import logger

from common.message_bus.kafka_producer import get_kafka_producer, make_mb_producer
from gateway.api.routers.users import router as users_router
from gateway.api.routers.proxy import router as proxy_router
from gateway.users.pg_repo import PostgresUserRepo

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True)


def preconfigure(app: FastAPI) -> Callable[[], Coroutine[None, None, None]]:
    async def async_launch():
        logger.info('Configuring service...')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        conn: asyncpg.Connection = await asyncpg.connect(
            dsn=f'postgres://postgres:password12345@{host}:5432',
            database='gateway',
        )
        app.state.user_repo = PostgresUserRepo(conn)
        app.state.proxy_client = httpx.AsyncClient(follow_redirects=True)

        # Configure message broker
        kafka_srv = os.getenv('KAFKA_ADDR', 'localhost:29092')
        kafka_producer = get_kafka_producer([kafka_srv])
        app.state.user_stream_producer = make_mb_producer(kafka_producer, topic='user-streaming', sync=True)

        logger.info('Done with configuration')

    return async_launch


def cleanup(app: FastAPI) -> Callable[[], Coroutine[None, None, None]]:
    async def async_shutdown():
        logger.info('Shutting down service...')

    return async_shutdown


def get_application() -> FastAPI:
    app = FastAPI()
    app.add_event_handler('startup', preconfigure(app))
    app.add_event_handler('shutdown', cleanup(app))
    app.include_router(users_router)
    app.include_router(proxy_router)
    return app


app = get_application()
