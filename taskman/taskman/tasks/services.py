import random

from common.events.base import Event
from common.events.business.tasks import TaskAdded, TaskAssigned, TaskCompleted
from common.message_bus.protocols import MBProducer
from taskman.tasks.models import Task, UnassignedTask
from taskman.db.uow import TaskmanUoW
from taskman.users.models import TASK_DOERS_GROUP


class TaskAssignFailed(Exception):
    pass


class CompltetionError(Exception):
    pass


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# TODO: produce messages (CUD) to kafka #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #


async def add_task(
    uow: TaskmanUoW,
    tasks_cud: MBProducer,
    taskman_be: MBProducer,
    new_task: UnassignedTask,
) -> Task:
    async with uow:
        users = await uow.users.get_all()
        if not users:
            raise TaskAssignFailed('Worker list is empty')

        possible_assignees = [u for u in users if u.role in TASK_DOERS_GROUP]
        assingee = random.choice(possible_assignees)
        task = Task(**new_task.dict(), assignee=assingee.public_id)

        await uow.tasks.create(task)
        await uow.commit()

    task_added = Event(
        event_name='TaskAdded',
        data=TaskAdded(
            public_task_id=task.public_id,
            task_status=task.status,
            assignee_id=task.assignee,
        ),
    )
    taskman_be(key=task.public_id, value=task_added.json())
    return task


async def shuffle_tasks(uow: TaskmanUoW, taskman_be: MBProducer) -> None:
    async with uow:
        users = await uow.users.get_all()
        if not users:
            raise TaskAssignFailed('Worker list is empty')

        tasks = await uow.tasks.get_all_open()
        if not tasks:
            return

        possible_assignees = [u for u in users if u.role in TASK_DOERS_GROUP]
        assingees = random.choices(possible_assignees, k=len(tasks))
        for task, new_assignee in zip(tasks, assingees):
            task.assignee = new_assignee.public_id
            await uow.tasks.update(task)

        await uow.commit()

    for task in tasks:
        assigned = Event(
            event_name='TaskAssigned',
            data=TaskAssigned(public_task_id=task.public_id, assignee_id=task.assignee),
        )
        taskman_be(key=task.public_id, value=assigned.json())


async def complete_task(uow: TaskmanUoW, taskman_be: MBProducer, task_id: str, user_id: str) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(task_id)
        if task.assignee != user_id:
            raise CompltetionError('Task belongs to another worker')

        task.mark_completed()
        await uow.tasks.update(task)
        await uow.commit()

    task_completed = Event(
        event_name='TaskCompleted',
        data=TaskCompleted(public_task_id=task_id, assignee_id=user_id),
    )
    taskman_be(key=task.public_id, value=task_completed.json())
