import os
import sys
from threading import Thread
from typing import Any

import asyncpg
from fastapi import FastAPI
from loguru import logger

from accounting import listener
from accounting.db.uow import PgAccountingUoW
from accounting.api.router import router

logger.remove()
logger.add(sink=sys.stdout, level='INFO', backtrace=False, colorize=True, diagnose=False)


def preconfigure(app: FastAPI) -> Any:
    async def async_launch():
        logger.info('Configuring service...')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        pool: asyncpg.Pool | None = await asyncpg.create_pool(
            dsn=f'postgres://postgres:password12345@{host}:5432',
            database='accounting',
        )
        if pool is None:
            raise ValueError('Connection to database failed, could not start service')

        app.state.uow = PgAccountingUoW(pool)

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
