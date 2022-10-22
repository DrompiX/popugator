from abc import ABC, abstractmethod

from taskman.users.models import User


class UserAlreadyExists(Exception):
    def __init__(self, public_id: str) -> None:
        super().__init__(f'User with name {public_id} already exists')
        self.public_id = public_id


class UserNotFound(Exception):
    def __init__(self, public_id: str) -> None:
        super().__init__(f'User with id {public_id} not found')
        self.public_id = public_id


class UserRepo(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, public_id: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[User]:
        raise NotImplementedError


class FakeUserRepo(UserRepo):
    def __init__(self) -> None:
        self.user_store: dict[str, User] = {}

    async def create_user(self, user: User) -> None:
        if user.public_id in self.user_store:
            raise UserAlreadyExists(user.public_id)

        self.user_store[user.public_id] = user

    async def get_by_id(self, public_id: str) -> User:
        if public_id not in self.user_store:
            raise UserNotFound(public_id)

        return self.user_store[public_id]

    async def get_all(self) -> list[User]:
        return list(self.user_store.values())
