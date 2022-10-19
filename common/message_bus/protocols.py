from typing import Any, Protocol


class MBProducer(Protocol):
    def __call__(self, key: str, value: str) -> Any:
        ...


class EventHandler(Protocol):
    async def __call__(self, event: Any) -> None:
        ...
