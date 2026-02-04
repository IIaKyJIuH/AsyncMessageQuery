import asyncio
import random
from uuid import UUID

import aio_pika

from .db import AsyncSessionLocal, init_db
from .enums import TaskStatus
from .models import Task
from .mq import RabbitBroker


async def handle_message(message: aio_pika.message.AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        task_id_raw = message.body.decode("utf-8")
        try:
            task_id = UUID(task_id_raw)
        except ValueError:
            return

        async with AsyncSessionLocal() as session:
            task = await session.get(Task, task_id)
            if not task:
                return

            task.status = TaskStatus.PROCESSING
            await session.commit()

            try:
                await asyncio.sleep(random.uniform(2, 5))
                if random.random() > 0.7:
                    raise ValueError("Random failure simulation")
                task.result = f"Processed payload: {task.payload}"
                task.status = TaskStatus.DONE
            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.result = f"Processing failed: {exc}"

            await session.commit()


async def main() -> None:
    await init_db()
    async with RabbitBroker() as broker:
        await broker.consume(handle_message)


if __name__ == "__main__":
    asyncio.run(main())
