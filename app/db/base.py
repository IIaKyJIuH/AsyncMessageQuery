from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config import settings
from ..utils.retry import async_retry

engine = create_async_engine(settings.database_url, pool_pre_ping=True)


class BaseModel(DeclarativeBase):
    pass


@async_retry
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
