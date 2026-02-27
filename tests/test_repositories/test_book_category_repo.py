from dataclasses import dataclass
from typing import Type

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import BookCategoryRepository, errors
from schemas import Category

FAKE_BOOK_CATEGORIES = {"Rob", "Linda", "Gray", "Lima", "Mike", "Duke"}


@pytest_asyncio.fixture
async def seed_categories(async_session: AsyncSession):
  async_session.add_all(
    categories := [Category(name=name) for name in FAKE_BOOK_CATEGORIES]
  )
  await async_session.flush()
  return categories


@pytest.fixture
def book_category_repo(async_session: AsyncSession):
  return BookCategoryRepository(async_session)


@dataclass(frozen=True)
class GetAllTestCase:
  kwargs: dict
  expected_len: int


get_all_test_cases = [
  pytest.param(
    GetAllTestCase(kwargs={}, expected_len=len(FAKE_BOOK_CATEGORIES)),
    id="without-skip-n-limit",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2}, expected_len=len(FAKE_BOOK_CATEGORIES) - 2),
    id="with-skip-only",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"limit": 3}, expected_len=3),
    id="with-limit-only-lt-total",
  ),
  pytest.param(
    GetAllTestCase(
      kwargs={"limit": len(FAKE_BOOK_CATEGORIES)},
      expected_len=len(FAKE_BOOK_CATEGORIES),
    ),
    id="with-limit-only-eq-total",
  ),
  pytest.param(
    GetAllTestCase(
      kwargs={"limit": len(FAKE_BOOK_CATEGORIES) + 1},
      expected_len=len(FAKE_BOOK_CATEGORIES),
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
  book_category_repo: BookCategoryRepository, case: GetAllTestCase, seed_categories
):
  assert len(await book_category_repo.get_all(**case.kwargs)) == case.expected_len


@dataclass(frozen=True)
class GetByNamesTestCase:
  category_names: list[str]
  strict: bool = False
  expected_names: list[str] | None = None
  expected_exception: Type[Exception] | None = None


get_by_names_test_cases = [
  pytest.param(
    GetByNamesTestCase(
      category_names=[*FAKE_BOOK_CATEGORIES, "Unknown"],
      strict=True,
      expected_names=[*FAKE_BOOK_CATEGORIES],
    ),
    id="strict-with-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      category_names=[*FAKE_BOOK_CATEGORIES],
      strict=True,
      expected_names=[*FAKE_BOOK_CATEGORIES],
    ),
    id="strict-without-unknown",
  ),
  pytest.param(
    GetByNamesTestCase(
      category_names=[*FAKE_BOOK_CATEGORIES, "Unknown"],
      strict=False,
      expected_names=[*FAKE_BOOK_CATEGORIES],
    ),
    id="non-strict-with-unknown",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_by_names_test_cases)
async def test_get_by_names(
  book_category_repo: BookCategoryRepository, case: GetByNamesTestCase, seed_categories
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      authors = await book_category_repo.get_by_names(
        category_names=case.category_names
      )
      print(f"{len(authors) = }")

  else:
    authors = await book_category_repo.get_by_names(category_names=case.category_names)
    assert set(a.name for a in authors) == set(case.expected_names)


@dataclass(frozen=True)
class CreateTestCase:
  category_names: list[str]
  expected_exception: Type[Exception] | None = None


create_test_cases = [
  pytest.param(CreateTestCase(category_names=[]), id="no-author-names"),
  pytest.param(
    CreateTestCase(category_names=["Rob", "Gray", "Millie"]), id="unique-author-names"
  ),
  pytest.param(
    CreateTestCase(
      category_names=["Rob", "Gray", "Gray"], expected_exception=errors.AlreadyExists
    ),
    id="duplicate-author-names",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", create_test_cases)
async def test_create(
  book_category_repo: BookCategoryRepository,
  async_session: AsyncSession,
  case: CreateTestCase,
):
  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await book_category_repo.create(category_names=case.category_names)
    return

  await book_category_repo.create(category_names=case.category_names)

  authors = (await async_session.scalars(select(Category))).all()
  assert len(authors) == len(case.category_names)
  assert set(a.name for a in authors) == set(case.category_names)


@dataclass(frozen=True)
class DeleteTestCase:
  seed_categories: list[Category]
  category_ids: list[int]
  expected_len: int | None = None
  expected_exception: Type[Exception] | None = None


delete_test_cases = [
  pytest.param(
    DeleteTestCase(
      seed_categories=[
        Category(id=id, name=name) for id, name in enumerate(FAKE_BOOK_CATEGORIES)
      ],
      category_ids=[],
      expected_len=len(FAKE_BOOK_CATEGORIES),
    ),
    id="delete-nothing-with-no-author-ids",
  ),
  pytest.param(
    DeleteTestCase(
      seed_categories=[
        Category(id=id, name=name) for id, name in enumerate(FAKE_BOOK_CATEGORIES)
      ],
      category_ids=[1, 2, 3],
      expected_len=len(FAKE_BOOK_CATEGORIES) - 3,
    ),
    id="delete-existent-author-ids",
  ),
  pytest.param(
    DeleteTestCase(
      seed_categories=[], category_ids=[1e5], expected_exception=errors.NotFound
    ),
    id="delete-non-existent-author-ids",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", delete_test_cases)
async def test_delete(
  book_category_repo: BookCategoryRepository,
  async_session: AsyncSession,
  case: DeleteTestCase,
):
  async_session.add_all(case.seed_categories)
  await async_session.flush()

  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await book_category_repo.delete(category_ids=case.category_ids)
    return

  await book_category_repo.delete(category_ids=case.category_ids)

  authors = (await async_session.scalars(select(Category))).all()
  assert len(authors) == case.expected_len
