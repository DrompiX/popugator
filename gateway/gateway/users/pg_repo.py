from typing import Any, Optional
from asyncpg.connection import Connection
from asyncpg.exceptions import UniqueViolationError

from gateway.users.models import User
from gateway.users.repo import UserAlreadyExists, UserNotFound, UserRepo


class PostgresUserRepo(UserRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create_user(self, user: User) -> None:
        query = '''
            INSERT INTO users(username, public_id, role) VALUES ($1, $2, $3)
            ON CONFLICT (public_id) DO NOTHING
        '''
        try:
            await self._conn.execute(query, user.username, user.public_id, user.role)
        except UniqueViolationError:
            raise UserAlreadyExists(user.username)

    async def get_by_username(self, username: str) -> User:
        query = 'SELECT * FROM users WHERE username = $1'
        row: Optional[dict[str, Any]] = await self._conn.fetchrow(query, username)
        if row is None:
            raise UserNotFound(username)

        return User.parse_obj(row)
