from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..enums import TaskStatus


class TaskCreate(BaseModel):
    payload: str = Field(min_length=1)


class TaskCreated(BaseModel):
    id: UUID


class TaskRead(BaseModel):
    id: UUID
    payload: str
    status: TaskStatus
    result: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
