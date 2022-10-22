import random

from common.events.business.tasks import TaskAdded, TaskAssigned, TaskCompleted
from common.events.cud.tasks import TaskCreated, TaskData, TaskUpdated
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
    cud_produce: MBProducer,
    be_produce: MBProducer,
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

    send_events_for_new_task(task, be_produce=be_produce, cud_produce=cud_produce)
    return task


async def shuffle_tasks(uow: TaskmanUoW, be_produce: MBProducer, cud_produce: MBProducer) -> None:
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
        send_events_for_assign(task, be_produce=be_produce, cud_produce=cud_produce)


async def complete_task(
    uow: TaskmanUoW,
    be_produce: MBProducer,
    cud_produce: MBProducer,
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

    send_events_for_complete(task, tasks_be=be_produce, tasks_cud=cud_produce)


##### Event senders #####


def send_events_for_new_task(task: Task, cud_produce: MBProducer, be_produce: MBProducer) -> None:
    added = TaskAdded(
        version=2,
        data={
            'public_id': task.public_id,
            'jira_id': task.jira_id,
            'description': task.description,
            'assignee_id': task.assignee_id,
        },
    )
    be_produce(key=task.public_id, value=added.json())

    created = TaskCreated(version=2, data=TaskData(**task.dict()))
    cud_produce(key=task.public_id, value=created.json())


def send_events_for_assign(task: Task, cud_produce: MBProducer, be_produce: MBProducer) -> None:
    assigned = TaskAssigned(
        version=1,
        data={'public_id': task.public_id, 'assignee_id': task.assignee_id},
    )
    be_produce(key=task.public_id, value=assigned.json())

    updated = TaskUpdated(version=2, domain='taskman', data=TaskData(**task.dict()))
    cud_produce(key=task.public_id, value=updated.json())


def send_events_for_complete(task: Task, tasks_cud: MBProducer, tasks_be: MBProducer) -> None:
    completed = TaskCompleted(
        version=1,
        data={'public_id': task.public_id, 'assignee_id': task.assignee_id},
    )
    tasks_be(key=task.public_id, value=completed.json())

    updated = TaskUpdated(version=2, domain='taskman', data=TaskData(**task.dict()))
    tasks_cud(key=task.public_id, value=updated.json())
