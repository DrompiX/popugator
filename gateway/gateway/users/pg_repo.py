from asyncpg.connection import Connection

from gateway.users.models import User
from gateway.users.repo import UserRepo


class PostgresUserRepo(UserRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create_user(self, user: User) -> None:
        query = 'INSERT INTO users(username, public_id, role) VALUES ($1, $2, $3)'
        await self._conn.execute(query, user.username, user.public_id, user.role)

    async def get_user(self, username: str) -> User:
        raise NotImplementedError
