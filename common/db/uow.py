from abc import ABC, abstractmethod
from typing import Any


class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> Any:
        pass

    async def __aexit__(self, *args: Any) -> Any:
        await self.rollback()
