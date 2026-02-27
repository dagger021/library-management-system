from dataclasses import dataclass
from typing import Type

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import AuthorRepository, errors
from schemas import Author

FAKE_AUTHORS = {"Rob", "Linda", "Gray", "Lima", "Mike", "Duke"}


@pytest_asyncio.fixture
async def seed_authors(async_session: AsyncSession):
  async_session.add_all(authors := [Author(name=name) for name in FAKE_AUTHORS])
  await async_session.flush()
  return authors


@pytest.fixture
def author_repo(async_session: AsyncSession):
  return AuthorRepository(async_session)


@dataclass(frozen=True)
class GetAllTestCase:
  kwargs: dict
  expected_len: int


get_all_test_cases = [
  pytest.param(
    GetAllTestCase(kwargs={}, expected_len=len(FAKE_AUTHORS)),
    id="without-skip-n-limit",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2}, expected_len=len(FAKE_AUTHORS) - 2),
    id="with-skip-only",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"limit": 3}, expected_len=3),
    id="with-limit-only-lt-total",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"limit": len(FAKE_AUTHORS)}, expected_len=len(FAKE_AUTHORS)),
    id="with-limit-only-eq-total",
  ),
  pytest.param(
    GetAllTestCase(
      kwargs={"limit": len(FAKE_AUTHORS) + 1}, expected_len=len(FAKE_AUTHORS)
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
  author_repo: AuthorRepository, case: GetAllTestCase, seed_authors
):
  assert len(await author_repo.get_all(**case.kwargs)) == case.expected_len


@dataclass(frozen=True)
class GetByNamesTestCase:
  author_names: list[str]
  strict: bool = False
  expected_names: list[str] | None = None
  expected_exception: Type[Exception] | None = None


get_by_names_test_cases = [
  pytest.param(
    GetByNamesTestCase(
      author_names=[*FAKE_AUTHORS, "Unknown"],
      strict=True,
      expected_names=[*FAKE_AUTHORS],
    ),
    id="strict-with-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      author_names=[*FAKE_AUTHORS],
      strict=True,
      expected_names=[*FAKE_AUTHORS],
    ),
    id="strict-without-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      author_names=[*FAKE_AUTHORS, "Unknown"],
      strict=False,
      expected_names=[*FAKE_AUTHORS],
    ),
    id="non-strict-with-unknown",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_by_names_test_cases)
async def test_get_by_names(
  author_repo: AuthorRepository, case: GetByNamesTestCase, seed_authors
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      authors = await author_repo.get_by_names(author_names=case.author_names)
      print(f"{len(authors) = }")

  else:
    authors = await author_repo.get_by_names(author_names=case.author_names)
    assert set(a.name for a in authors) == set(case.expected_names)


@dataclass(frozen=True)
class CreateTestCase:
  author_names: list[str]
  expected_exception: Type[Exception] | None = None


create_test_cases = [
  pytest.param(CreateTestCase(author_names=[]), id="no-author-names"),
  pytest.param(
    CreateTestCase(author_names=["Rob", "Gray", "Millie"]),
    id="unique-author-names",
  ),
  pytest.param(
    CreateTestCase(
      author_names=["Rob", "Gray", "Gray"], expected_exception=errors.AlreadyExists
    ),
    id="duplicate-author-names",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", create_test_cases)
async def test_create(
  author_repo: AuthorRepository, async_session: AsyncSession, case: CreateTestCase
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await author_repo.create(author_names=case.author_names)
    return

  await author_repo.create(author_names=case.author_names)

  authors = (await async_session.scalars(select(Author))).all()
  assert len(authors) == len(case.author_names)
  assert set(a.name for a in authors) == set(case.author_names)


@dataclass(frozen=True)
class DeleteTestCase:
  seed_authors: list[Author]
  author_ids: list[int]
  expected_len: int | None = None
  expected_exception: Type[Exception] | None = None


delete_test_cases = [
  pytest.param(
    DeleteTestCase(
      seed_authors=[Author(id=id, name=name) for id, name in enumerate(FAKE_AUTHORS)],
      author_ids=[],
      expected_len=len(FAKE_AUTHORS),
    ),
    id="delete-nothing-with-no-author-ids",
  ),
  pytest.param(
    DeleteTestCase(
      seed_authors=[Author(id=id, name=name) for id, name in enumerate(FAKE_AUTHORS)],
      author_ids=[1, 2, 3],
      expected_len=len(FAKE_AUTHORS) - 3,
    ),
    id="delete-existent-author-ids",
  ),
  pytest.param(
    DeleteTestCase(
      seed_authors=[], author_ids=[1e5], expected_exception=errors.NotFound
    ),
    id="delete-non-existent-author-ids",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", delete_test_cases)
async def test_delete(
  author_repo: AuthorRepository, async_session: AsyncSession, case: DeleteTestCase
):
  async_session.add_all(case.seed_authors)
  await async_session.flush()

  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await author_repo.delete(author_ids=case.author_ids)

  else:
    await author_repo.delete(author_ids=case.author_ids)

    authors = (await async_session.scalars(select(Author))).all()
    assert len(authors) == case.expected_len
