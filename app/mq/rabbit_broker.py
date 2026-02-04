import asyncio
from collections.abc import Awaitable, Callable

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.channel import AbstractChannel
from aio_pika.queue import AbstractQueue
from aio_pika.robust_connection import AbstractRobustConnection

from ..config import settings
from ..mq.broker_base import BrokerBase
from ..utils.retry import async_retry

MessageHandler = Callable[[aio_pika.message.AbstractIncomingMessage], Awaitable[None]]


class RabbitBroker(BrokerBase):
    def __init__(self, url: str | None = None, queue_name: str | None = None) -> None:
        self.url = url or settings.rabbit_url
        self.queue_name = queue_name or settings.queue_name
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.queue: AbstractQueue | None = None

    @async_retry
    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def publish(self, task_id: str) -> None:
        if not self.channel:
            raise RuntimeError("RabbitMQ channel is not initialized")
        message = Message(
            body=task_id.encode("utf-8"), delivery_mode=DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(
            message, routing_key=self.queue_name
        )

    async def consume(self, handler: MessageHandler) -> None:
        if not self.queue:
            raise RuntimeError("RabbitMQ queue is not initialized")
        await self.queue.consume(handler, no_ack=False)
        await asyncio.Event().wait()
