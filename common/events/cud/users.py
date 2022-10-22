from pydantic import Field

from common.events.base import Event, EventData

#################################
# UserCreated event description #
#################################


class UserCreatedData(EventData):
    public_id: str
    username: str
    role: str


class UserCreated(Event):
    name: str = Field(default='UserCreated', const=True)
    domain: str = Field(default='users', const=True)
    data: UserCreatedData
