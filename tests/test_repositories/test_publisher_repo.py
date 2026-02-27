from dataclasses import dataclass, field
from typing import Type

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import PublisherRepository, errors
from schemas import Publisher

FAKE_PUBLISHERS = {"openbooks", "darkbooks", "lighthouse", "greenpubs", "paperbacks"}


@pytest_asyncio.fixture
async def seed_publishers(async_session: AsyncSession):
  publishers = [Publisher(name=name) for name in FAKE_PUBLISHERS]
  async_session.add_all(publishers)
  await async_session.flush()
  return publishers


@pytest.fixture
def publisher_repo(async_session: AsyncSession):
  return PublisherRepository(session=async_session)


@dataclass(frozen=True)
class GetAllTestCase:
  expected_len: int
  kwargs: dict = field(default_factory=dict)


get_all_test_cases = [
  pytest.param(
    GetAllTestCase(kwargs={}, expected_len=len(FAKE_PUBLISHERS)),
    id="without-skip-n-limit",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2}, expected_len=len(FAKE_PUBLISHERS) - 2),
    id="with-skip-only",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"limit": 3}, expected_len=3),
    id="with-limit-only-lt-total",
  ),
  pytest.param(
    GetAllTestCase(
      kwargs={"limit": len(FAKE_PUBLISHERS)}, expected_len=len(FAKE_PUBLISHERS)
    ),
    id="with-limit-only-eq-total",
  ),
  pytest.param(
    GetAllTestCase(
      kwargs={"limit": len(FAKE_PUBLISHERS) + 1}, expected_len=len(FAKE_PUBLISHERS)
    ),
    id="with-limit-only-gt-total",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2, "limit": 3}, expected_len=3),
    id="with-skip-n-limit",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_all_test_cases)
async def test_get_all(
  publisher_repo: PublisherRepository, case: GetAllTestCase, seed_publishers
):
  assert len(await publisher_repo.get_all(**case.kwargs)) == case.expected_len


@dataclass(frozen=True)
class GetByNamesTestCase:
  publisher_names: list[str]
  strict: bool = False
  expected_names: list[str] | None = None
  expected_exception: Type[Exception] | None = None


get_by_names_test_cases = [
  pytest.param(
    GetByNamesTestCase(
      publisher_names=[*FAKE_PUBLISHERS, "Unknown"],
      strict=True,
      expected_exception=errors.NotFound,
    ),
    id="strict-with-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      publisher_names=[*FAKE_PUBLISHERS], strict=True, expected_names=[*FAKE_PUBLISHERS]
    ),
    id="strict-without-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      publisher_names=[*FAKE_PUBLISHERS, "Unknown"], expected_names=[*FAKE_PUBLISHERS]
    ),
    id="non-strict-with-unknown",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_by_names_test_cases)
async def test_get_by_names(
  publisher_repo: PublisherRepository, case: GetByNamesTestCase, seed_publishers
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await publisher_repo.get_by_names(
        publisher_names=case.publisher_names, strict=case.strict
      )
    return

  publishers = await publisher_repo.get_by_names(
    publisher_names=case.publisher_names, strict=case.strict
  )
  assert set(p.name for p in publishers) == set(case.expected_names)


@dataclass(frozen=True)
class CreateTestCase:
  publisher_names: list[str]
  expected_exception: Type[Exception] | None = None


create_test_cases = [
  pytest.param(
    CreateTestCase(publisher_names=["penguins", "lighthouse", "greenpubs"]),
    id="unique-publisher-names",
  ),
  pytest.param(
    CreateTestCase(
      publisher_names=["penguins", "lighthouse", "penguins"],
      # expected_exception=IntegrityError,
      expected_exception=errors.AlreadyExists,
    ),
    id="duplicate-publisher-names",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", create_test_cases)
async def test_create(
  publisher_repo: PublisherRepository, async_session: AsyncSession, case: CreateTestCase
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await publisher_repo.create(publisher_names=case.publisher_names)
    return

  await publisher_repo.create(publisher_names=case.publisher_names)

  publishers = (await async_session.scalars(select(Publisher))).all()
  assert len(publishers) == len(case.publisher_names)
  assert set(p.name for p in publishers) == set(case.publisher_names)


@dataclass(frozen=True)
class DeleteTestCase:
  seed_publishers: list[str]
  publisher_ids: list[int]
  expected_len: int | None = None
  expected_exception: Type[Exception] | None = None


delete_test_cases = [
  pytest.param(
    DeleteTestCase(
      seed_publishers=[
        Publisher(id=id, name=name) for id, name in enumerate(FAKE_PUBLISHERS)
      ],
      publisher_ids=[],
      expected_len=len(FAKE_PUBLISHERS),
    ),
  ),
  pytest.param(
    DeleteTestCase(
      seed_publishers=[
        Publisher(id=id, name=name) for id, name in enumerate(FAKE_PUBLISHERS)
      ],
      publisher_ids=[1, 2, 3],
      expected_len=len(FAKE_PUBLISHERS) - 3,
    )
  ),
  pytest.param(
    DeleteTestCase(
      seed_publishers=[
        Publisher(id=id, name=name) for id, name in enumerate(FAKE_PUBLISHERS)
      ],
      publisher_ids=[1e5],
      expected_exception=errors.NotFound,
    )
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", delete_test_cases)
async def test_delete(
  publisher_repo: PublisherRepository, case: DeleteTestCase, async_session: AsyncSession
):
  async_session.add_all(case.seed_publishers)
  await async_session.flush()

  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await publisher_repo.delete(publisher_ids=case.publisher_ids)
    return

  await publisher_repo.delete(publisher_ids=case.publisher_ids)

  publishers = (await async_session.scalars(select(Publisher))).all()
  assert len(publishers) == case.expected_len
