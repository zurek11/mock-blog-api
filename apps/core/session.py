from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from apps.core.models.base import SoftDeleteSession
from config import settings

url_object = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    database=settings.DATABASE_NAME,
)

engine = create_async_engine(
    url=url_object,
    future=True,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE
)


async_session_maker = async_sessionmaker(
    bind=engine, expire_on_commit=False, autocommit=False, autoflush=False, class_=SoftDeleteSession
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Commit if the endpoint completes successfully
        except Exception:
            await session.rollback()  # Rollback on any exception
        finally:
            await session.close()

SessionDep = Annotated[SoftDeleteSession, Depends(get_async_session)]
