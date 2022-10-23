from typing import Any, Optional

from asyncpg.connection import Connection

from accounting.tasks.models import Task
from accounting.tasks.repo import TaskNotFound, TaskRepo


class PostgresTaskRepo(TaskRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create(self, task: Task) -> None:
        query = '''
            INSERT INTO tasks(public_id, jira_id, description, fee, profit)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (public_id) DO NOTHING
        '''
        args = (task.public_id, task.jira_id, task.description, task.fee, task.profit)
        await self._conn.execute(query, *args)

    async def update(self, task: Task) -> None:
        query = '''
            UPDATE tasks SET (jira_id, description) = ($2, $3)
            WHERE public_id = $1
        '''
        args = (task.public_id, task.jira_id, task.description)
        await self._conn.execute(query, *args)

    async def get_by_id(self, task_id: str) -> Task:
        query = 'SELECT * FROM tasks WHERE public_id = $1'
        row: Optional[dict[str, Any]] = await self._conn.fetchrow(query, task_id)
        if row is None:
            raise TaskNotFound(task_id)

        return Task.parse_obj(row)
