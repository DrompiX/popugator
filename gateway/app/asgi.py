import sys
from typing import Callable, Coroutine

from fastapi import FastAPI
from loguru import logger

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True)


def preconfigure(app: FastAPI) -> Callable[[], Coroutine[None, None, None]]:
    async def async_launch():
        logger.info('Configuring service...')

    return async_launch


def cleanup(app: FastAPI) -> Callable[[], Coroutine[None, None, None]]:
    async def async_shutdown():
        logger.info('Shutting down service...')

    return async_shutdown


def get_application() -> FastAPI:
    app = FastAPI()
    app.add_event_handler('startup', preconfigure(app))
    app.add_event_handler('shutdown', cleanup(app))
    return app


app = get_application()
