from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, AsyncSession
from config import env


engine = create_async_engine(
    env.POSTGRES_DSN,
    echo=True
)

AsyncDatabaseSession = AsyncSession(
    engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass
