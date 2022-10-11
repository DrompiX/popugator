import sys
from typing import Callable, Coroutine

import httpx
from fastapi import FastAPI
from kafka import KafkaProducer
from loguru import logger
from common.message_bus.kafka import make_mb_producer
from users.repo import FakeUserRepo

from users.router import router as users_router
from proxy.router import router as proxy_router

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True)


def preconfigure(app: FastAPI) -> Callable[[], Coroutine[None, None, None]]:
    async def async_launch():
        logger.info('Configuring service...')
        app.state.user_repo = FakeUserRepo()
        app.state.proxy_client = httpx.AsyncClient(follow_redirects=True)
        kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9095'])
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
