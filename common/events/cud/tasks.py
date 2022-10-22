from pydantic import Field

from common.events.base import Event, EventData


class TaskData(EventData):
    public_id: str
    jira_id: str
    description: str
    assignee_id: str
    status: str


#################################
# TaskCreated event description #
#################################


class TaskCreated(Event):
    name: str = Field(default='TaskCreated', const=True)
    domain: str = Field(default='taskman', const=True)
    data: TaskData


#################################
# TaskUpdated event description #
#################################


class TaskUpdated(Event):
    name: str = Field(default='TaskUpdated', const=True)
    data: TaskData
