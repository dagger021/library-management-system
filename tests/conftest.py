from os import environ

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.db import Base

load_dotenv()
TEST_DB_URL_ASYNC = environ["TEST_DB_URL_ASYNC"]


@pytest.fixture(scope="session")
def async_engine():
  return create_async_engine(TEST_DB_URL_ASYNC, echo=False, poolclass=NullPool)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_entities_lifecycle(async_engine: AsyncEngine):
  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

  yield

  async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session(async_engine: AsyncEngine):
  async with async_sessionmaker(async_engine, expire_on_commit=False)() as session:
    yield session
    # await session.rollback()
