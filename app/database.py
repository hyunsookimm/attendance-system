from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=(settings.env == "development"),
    pool_pre_ping=True,
    pool_recycle=300,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session
