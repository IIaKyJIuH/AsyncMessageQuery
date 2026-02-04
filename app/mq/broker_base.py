from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Self

from ..utils.retry import async_retry

type MessageHandler[T] = Callable[[T], Awaitable[None]]


class BrokerBase(ABC):
    @abstractmethod
    @async_retry
    async def connect(self) -> None:
        raise NotImplementedError(...)

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError(...)

    @abstractmethod
    async def publish(self, task_id: str) -> None:
        raise NotImplementedError(...)

    @abstractmethod
    async def consume(self, handler: MessageHandler) -> None:
        raise NotImplementedError(...)

    @abstractmethod
    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        await self.close()
