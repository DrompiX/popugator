from pydantic import Field
from common.events.base import Event, EventData


###############################
# TaskAdded event description #
###############################


class TaskAddedData(EventData):
    public_id: str
    jira_id: str
    description: str
    assignee_id: str


class TaskAdded(Event):
    version: int
    name: str = Field(default='TaskAdded', const=True)
    domain: str = Field(default='taskman', const=True)
    data: TaskAddedData


##################################
# TaskAssigned event description #
##################################


class TaskAssignedData(EventData):
    public_id: str
    assignee_id: str


class TaskAssigned(Event):
    version: int
    name: str = Field(default='TaskAssigned', const=True)
    domain: str = Field(default='taskman', const=True)
    data: TaskAssignedData


###################################
# TaskCompleted event description #
###################################


class TaskCompletedData(EventData):
    public_id: str
    assignee_id: str


class TaskCompleted(Event):
    version: int
    name: str = Field(default='TaskCompleted', const=True)
    domain: str = Field(default='taskman', const=True)
    data: TaskCompletedData
