from datetime import date
from typing import Any

from asyncpg.connection import Connection

from accounting.transactions.models import TransactionLogRecord
from accounting.transactions.repo import TransactionRepo


class PostgresTransactionRepo(TransactionRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def add(self, record: TransactionLogRecord) -> None:
        query = '''
            INSERT INTO transactions(public_id, public_user_id, description, credit, debit, created_at, type)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (public_id) DO NOTHING
        '''
        r = record
        args = (r.public_id, r.public_user_id, r.description, r.credit, r.debit, r.created_at, r.type)
        await self._conn.execute(query, *args)

    async def get_by_user_id(self, public_id: str) -> list[TransactionLogRecord]:
        query = 'SELECT * FROM transactions WHERE public_user_id = $1 ORDER BY created_at ASC'
        rows: list[dict[str, Any]] = await self._conn.fetch(query, public_id)
        return [TransactionLogRecord.parse_obj(r) for r in rows]

    async def get_all_by_date(self, d: date) -> list[TransactionLogRecord]:
        query = 'SELECT * FROM transactions WHERE date(created_at) = $1 ORDER BY created_at ASC'
        rows: list[dict[str, Any]] = await self._conn.fetch(query, d)
        return [TransactionLogRecord.parse_obj(r) for r in rows]

    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        query = '''
            SELECT public_user_id, sum(debit) - sum(credit) AS balance
            FROM transactions
            WHERE date(created_at) = $1
            GROUP BY public_user_id
        '''
        rows: list[dict[str, Any]] = await self._conn.fetch(query, d)
        return {r['public_user_id']: r['balance'] for r in rows}
