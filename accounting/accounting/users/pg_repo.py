from typing import Any, Optional
from asyncpg.connection import Connection

from accounting.users.models import User
from accounting.users.repo import UserNotFound, UserRepo


class PostgresUserRepo(UserRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create_user(self, user: User) -> None:
        query = '''
            INSERT INTO users(public_id, role) VALUES ($1, $2)
            ON CONFLICT (public_id) DO NOTHING
        '''
        await self._conn.execute(query, user.public_id, user.role)

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
