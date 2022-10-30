from abc import ABC, abstractmethod

from gateway.users.models import User


class UserAlreadyExists(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f'User with name {username} already exists')
        self.username = username


class UserNotFound(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f'User with id {username} not found')
        self.username = username


class UserRepo(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> User:
        raise NotImplementedError


class FakeUserRepo(UserRepo):
    def __init__(self) -> None:
        self.user_store: dict[str, User] = {}

    async def create_user(self, user: User) -> None:
        if user.username in self.user_store:
            raise UserAlreadyExists(user.username)

        self.user_store[user.username] = user

    async def get_by_username(self, username: str) -> User:
        if username not in self.user_store:
            raise UserNotFound(username)

        return self.user_store[username]
