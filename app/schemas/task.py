from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    payload: str = Field(min_length=1)


class TaskCreated(BaseModel):
    id: UUID
