from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_config

cfg = get_config()

DB_URL = "postgresql+asyncpg://%s:%s@localhost:%s/%s" % (
  cfg.POSTGRES_USER,
  cfg.POSTGRES_PASSWORD,
  cfg.POSTGRES_PORT,
  cfg.POSTGRES_DB,
)


class Base(DeclarativeBase): ...


async_engine = create_async_engine(DB_URL, future=True)


@asynccontextmanager
async def db_lifespan():
  """db_lifespan creates database entities and drops all at destruction."""

  async with async_engine.begin() as conn:
    # create all tables
    await conn.run_sync(Base.metadata.create_all)
    print("creating entities")
    yield
    # drop all tables
    await conn.run_sync(Base.metadata.drop_all)
    print("dropping entities")


# using singleton pattern to provide single instance of AsyncSession
ASYNC_SESSION: async_sessionmaker[AsyncSession] | None = None


def get_async_session():
  """Returns AsyncSession instance."""
  global ASYNC_SESSION
  if ASYNC_SESSION is None:
    ASYNC_SESSION = async_sessionmaker(async_engine)

  return ASYNC_SESSION
