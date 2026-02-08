from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_config

_cfg = get_config()
_async_engine = create_async_engine(_cfg.DB_URL_ASYNC)
_async_session = async_sessionmaker(_async_engine, expire_on_commit=False)


class Base(DeclarativeBase): ...


async def get_async_session():
  """Returns AsyncSession instance."""
  async with _async_session() as session:
    yield session
