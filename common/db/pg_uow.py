from typing import Any
import asyncpg
import asyncpg.transaction

from common.db.uow import UnitOfWork


class PostgresUoW(UnitOfWork):
    def __init__(self, conn_pool: asyncpg.Pool) -> None:
        self._pool = conn_pool
        self._conn: asyncpg.Connection
        self._tr: asyncpg.transaction.Transaction

    async def __aenter__(self) -> Any:
        self._conn: asyncpg.Connection = await self._pool.acquire()
        self._tr = self._conn.transaction()
        await self._tr.start()

    async def __aexit__(self, *args: Any) -> Any:
        await super().__aexit__(*args)
        await self._pool.release(self._conn)

    async def commit(self) -> None:
        await self._tr.commit()

    async def rollback(self) -> None:
        try:
            await self._tr.rollback()
        except asyncpg.exceptions.InterfaceError:
            # Transaction was already committed
            pass
