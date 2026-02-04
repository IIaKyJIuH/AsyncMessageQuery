from contextlib import asynccontextmanager
from typing import cast

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.mq.broker_base import BrokerBase

from .db import get_session, init_db
from .enums import TaskStatus
from .models import Task
from .mq import RabbitBroker
from .schemas import TaskCreate, TaskCreated


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
    except Exception as exc:  # pragma: no cover - defensive
        task.status = TaskStatus.FAILED
        task.result = f"Queue publish failed: {exc}"
        await session.commit()
        raise HTTPException(status_code=500, detail="Failed to enqueue task") from exc

    return TaskCreated(id=task.id)
