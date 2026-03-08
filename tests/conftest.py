import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from config import get_config, Config

from core.db import Base


@pytest.fixture(scope="session")
def app_cfg():
  """Fixture to provide application-level config."""
  cfg = get_config()
  # modify config for testing
  cfg.ACCESS_JWT_TIMEOUT = 2  # 2 seconds for testing

  return cfg


@pytest.fixture(scope="session")
def async_engine(app_cfg: Config):
  return create_async_engine(app_cfg.TEST_DB_URL_ASYNC, echo=False, poolclass=NullPool)


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
