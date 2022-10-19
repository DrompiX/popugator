from common.events.base import Event
from common.events.cud.users import UserCreated
from common.message_bus.protocols import MBProducer
from gateway.users.models import User
from gateway.users.repo import UserRepo


async def create_user(repo: UserRepo, produce_func: MBProducer, user: User) -> None:
    await repo.create_user(user)
    event = Event(
        name='UserCreated',
        data=UserCreated(
            public_id=user.public_id,
            username=user.username,
            role=user.role,
        ),
    )
    produce_func(key=user.public_id, value=event.json())


async def get_user(repo: UserRepo, username: str) -> User:
    return await repo.get_user(username)
