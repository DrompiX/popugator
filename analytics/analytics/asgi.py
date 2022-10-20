import sys
from typing import Any

from fastapi import FastAPI
from kafka import KafkaConsumer
from loguru import logger

from analytics.db.uow import FakeUoW
from analytics.api.router import router

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True, diagnose=False)


def preconfigure(app: FastAPI) -> Any:
    async def async_launch():
        logger.info('Configuring service...')
        app.state.uow = FakeUoW()
        # initialize event consuming part
        topics = {'user-streaming', 'task-streaming'}
        _consumer = KafkaConsumer(*topics, bootstrap_servers=['localhost:9095'])
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
