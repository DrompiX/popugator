from typing import Any, Optional

from asyncpg.connection import Connection

from taskman.tasks.models import Task, TaskStatus
from taskman.tasks.repo import TaskNotFound, TaskRepo


class PostgresTaskRepo(TaskRepo):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    async def create(self, task: Task) -> None:
        query = '''
            INSERT INTO tasks(public_id, assignee_id, jira_id, description, status)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (public_id) DO NOTHING
        '''
        args = (task.public_id, task.assignee_id, task.jira_id, task.description, task.status)
        await self._conn.execute(query, *args)

    async def update(self, task: Task) -> None:
        query = '''
            UPDATE tasks SET (assignee_id, jira_id, description, status) = ($2, $3, $4, $5)
            WHERE public_id = $1
        '''
        args = (task.public_id, task.assignee_id, task.jira_id, task.description, task.status)
        await self._conn.execute(query, *args)

    async def get_by_id(self, task_id: str) -> Task:
        query = 'SELECT * FROM tasks WHERE public_id = $1'
        row: Optional[dict[str, Any]] = await self._conn.fetchrow(query, task_id)
        if row is None:
            raise TaskNotFound(task_id)

        return Task.parse_obj(row)

    async def get_all(self) -> list[Task]:
        query = 'SELECT * FROM tasks'
        rows: list[dict[str, Any]] = await self._conn.fetch(query)
        return [Task.parse_obj(r) for r in rows]

    async def get_all_open(self) -> list[Task]:
        query = 'SELECT * FROM tasks WHERE status = $1'
        rows: list[dict[str, Any]] = await self._conn.fetch(query, TaskStatus.OPEN)
        return [Task.parse_obj(r) for r in rows]
