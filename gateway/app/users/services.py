from users.models import User
from users.repo import UserRepo


async def create_user(repo: UserRepo, user: User) -> None:
    # TODO: create event and send to MQ
    await repo.create_user(user)


async def get_user(repo: UserRepo, username: str) -> User:
    return await repo.get_user(username)
