from contextlib import asynccontextmanager
from typing import cast
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mq.broker_base import BrokerBase

from .db import get_session, init_db
from .enums import TaskStatus
from .models import Task
from .mq import RabbitBroker
from .schemas import TaskCreate, TaskCreated, TaskRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with RabbitBroker() as broker:
        app.state.broker = broker
        yield


app = FastAPI(title="bobr_task", lifespan=lifespan)


@app.post("/tasks", response_model=TaskCreated)
async def create_task(
    payload: TaskCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TaskCreated:
    task = Task(payload=payload.payload, status=TaskStatus.PENDING)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    broker = cast(BrokerBase, request.app.state.broker)
    try:
        await broker.publish(str(task.id))
    except Exception as exc:
        task.status = TaskStatus.FAILED
        task.result = f"Queue publish failed: {exc}"
        await session.commit()
        raise HTTPException(status_code=500, detail="Failed to enqueue task") from exc

    return TaskCreated(id=task.id)


@app.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, session: AsyncSession = Depends(get_session)) -> TaskRead:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)
