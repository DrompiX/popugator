from typing import Any, Optional
from asyncpg.connection import Connection

from analytics.users.models import User
from analytics.users.repo import UserNotFound, UserRepo


class PostgresUserRepo(UserRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create_user(self, user: User) -> None:
        query = '''
            INSERT INTO users(public_id) VALUES ($1)
            ON CONFLICT (public_id) DO NOTHING
        '''
        await self._conn.execute(query, user.public_id)

    async def get_by_id(self, public_id: str) -> User:
        query = 'SELECT * FROM users WHERE public_id = $1'
        row: Optional[dict[str, Any]] = await self._conn.fetchrow(query, public_id)
        if row is None:
            raise UserNotFound(public_id)

        return User.parse_obj(row)

    async def get_all(self) -> list[User]:
        query = 'SELECT * FROM users'
        rows: list[dict[str, Any]] = await self._conn.fetch(query)
        return [User.parse_obj(r) for r in rows]
