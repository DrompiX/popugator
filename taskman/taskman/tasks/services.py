import random

from common.events.base import Event
from common.events.business.tasks import TaskAdded, TaskAssigned, TaskCompleted
from common.events.cud.tasks import TaskCreated, TaskUpdated
from common.message_bus.protocols import MBProducer
from taskman.tasks.models import Task, UnassignedTask
from taskman.db.uow import TaskmanUoW
from taskman.users.models import TASK_DOERS_GROUP


class TaskAssignFailed(Exception):
    pass


class CompltetionError(Exception):
    pass


async def add_task(
    uow: TaskmanUoW,
    tasks_cud: MBProducer,
    tasks_be: MBProducer,
    new_task: UnassignedTask,
) -> Task:
    async with uow:
        users = await uow.users.get_all()
        possible_assignees = [u for u in users if u.role in TASK_DOERS_GROUP]
        if not possible_assignees:
            raise TaskAssignFailed('Worker list is empty')

        assingee = random.choice(possible_assignees)
        task = Task(**new_task.dict(), assignee_id=assingee.public_id)

        await uow.tasks.create(task)
        await uow.commit()

    send_events_for_new_task(task, tasks_be=tasks_be, tasks_cud=tasks_cud)
    return task


async def shuffle_tasks(uow: TaskmanUoW, tasks_be: MBProducer, tasks_cud: MBProducer) -> None:
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
            task.assignee_id = new_assignee.public_id
            await uow.tasks.update(task)

        await uow.commit()

    for task in tasks:
        send_events_for_assign(task, tasks_be=tasks_be, tasks_cud=tasks_cud)


async def complete_task(
    uow: TaskmanUoW,
    tasks_be: MBProducer,
    tasks_cud: MBProducer,
    task_id: str,
    user_id: str,
) -> None:
    async with uow:
        task = await uow.tasks.get_by_id(task_id)
        if task.assignee_id != user_id:
            raise CompltetionError('Task belongs to another worker')

        task.mark_completed()
        await uow.tasks.update(task)
        await uow.commit()

    send_events_for_complete(task, tasks_be=tasks_be, tasks_cud=tasks_cud)


##### Event senders #####


def send_events_for_new_task(task: Task, tasks_cud: MBProducer, tasks_be: MBProducer) -> None:
    added = Event(
        name='TaskAdded',
        data=TaskAdded(
            public_id=task.public_id,
            description=task.description,
            assignee_id=task.assignee_id,
        ),
    )
    tasks_be(key=task.public_id, value=added.json())

    created = Event(name='TaskCreated', data=TaskCreated(**task.dict()))
    tasks_cud(key=task.public_id, value=created.json())


def send_events_for_assign(task: Task, tasks_cud: MBProducer, tasks_be: MBProducer) -> None:
    assigned = Event(
        name='TaskAssigned',
        data=TaskAssigned(public_id=task.public_id, assignee_id=task.assignee_id),
    )
    tasks_be(key=task.public_id, value=assigned.json())

    updated = Event(name='TaskUpdated', data=TaskUpdated(**task.dict()))
    tasks_cud(key=task.public_id, value=updated.json())


def send_events_for_complete(task: Task, tasks_cud: MBProducer, tasks_be: MBProducer) -> None:
    completed = Event(
        name='TaskCompleted',
        data=TaskCompleted(public_id=task.public_id, assignee_id=task.assignee_id),
    )
    tasks_be(key=task.public_id, value=completed.json())

    updated = Event(name='TaskUpdated', data=TaskUpdated(**task.dict()))
    tasks_cud(key=task.public_id, value=updated.json())
