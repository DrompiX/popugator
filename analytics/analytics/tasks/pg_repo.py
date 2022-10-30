from datetime import date
from typing import Any, Optional

from asyncpg.connection import Connection

from analytics.tasks.models import Task, TaskStatus
from analytics.tasks.repo import TaskNotFound, TaskRepo


class PostgresTaskRepo(TaskRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create(self, task: Task) -> None:
        query = '''
            INSERT INTO tasks(public_id, jira_id, description, status, fee, profit)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (public_id) DO NOTHING
        '''
        args = (task.public_id, task.jira_id, task.description, task.status, task.fee, task.profit)
        await self._conn.execute(query, *args)

    async def update(self, task: Task) -> None:
        query = '''
            UPDATE tasks SET (description, status, fee, profit, completed_at) = ($2, $3, $4, $5, $6)
            WHERE public_id = $1
        '''
        args = (task.public_id, task.description, task.status, task.fee, task.profit, task.completed_at)
        await self._conn.execute(query, *args)

    async def get_by_id(self, task_id: str) -> Task:
        query = 'SELECT * FROM tasks WHERE public_id = $1'
        row: Optional[dict[str, Any]] = await self._conn.fetchrow(query, task_id)
        if row is None:
            raise TaskNotFound(task_id)

        return Task.parse_obj(row)

    async def get_most_expensive(self, start: date, end: date) -> Optional[Task]:
        query = '''
            SELECT *
            FROM tasks
            WHERE date(completed_at) BETWEEN SYMMETRIC $1 AND $2
            AND status = $3
            ORDER BY profit DESC
        '''
        result: dict[str, Any] | None = await self._conn.fetchrow(query, start, end, TaskStatus.DONE)
        return Task.parse_obj(result) if result else None
