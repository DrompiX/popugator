from datetime import date
from typing import Any

from asyncpg.connection import Connection

from analytics.transactions.models import TransactionLogRecord
from analytics.transactions.repo import TransactionRepo


class PostgresTransactionRepo(TransactionRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def add(self, record: TransactionLogRecord) -> None:
        query = '''
            INSERT INTO transactions(public_id, public_user_id, credit, debit, created_at, type)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (public_id) DO NOTHING
        '''
        r = record
        args = (r.public_id, r.public_user_id, r.credit, r.debit, r.created_at, r.type)
        await self._conn.execute(query, *args)

    async def get_balance_by_user(self, d: date) -> dict[str, int]:
        query = '''
            SELECT public_user_id, sum(debit) - sum(credit) AS balance
            FROM transactions
            WHERE date(created_at) = $1
            GROUP BY public_user_id
        '''
        rows: list[dict[str, Any]] = await self._conn.fetch(query, d)
        return {r['public_user_id']: r['balance'] for r in rows}

    async def get_management_income(self, start: date, end: date) -> int:
        query = '''
            SELECT sum(credit) - sum(debit)
            FROM transactions
            WHERE date(created_at) BETWEEN SYMMETRIC $1 AND $2
            AND type in ('deposit', 'withdrawal')
        '''
        result: int | None = await self._conn.fetchval(query, start, end)
        return result if result is not None else 0
