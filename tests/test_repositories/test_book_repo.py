import random
from dataclasses import dataclass, field
from typing import Type
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from test_repositories.test_author_repo import seed_authors  # noqa: F401
from test_repositories.test_book_category_repo import seed_categories  # noqa: F401
from test_repositories.test_publisher_repo import seed_publishers  # noqa: F401

from repositories import BookRepository, errors
from schemas import Author, Book, Category, Publisher

FAKE_BOOKS = [
  dict(
    title="Book Title %d" % i,
    isbn="book-isbn-%d" % i,
    published_year=2000 + i,
  )
  for i in range(1, 6)
]


@pytest_asyncio.fixture
async def seed_books(async_session: AsyncSession, seed_publishers: list[Publisher]):  # noqa: F811
  async_session.add_all(
    books := [
      Book(**b, publisher_id=random.choice(seed_publishers).id) for b in FAKE_BOOKS
    ]
  )
  await async_session.flush()
  return books


@pytest.fixture
def book_repo(async_session: AsyncSession):
  return BookRepository(async_session)


@dataclass(frozen=True)
class GetAllTestCase:
  expected_len: int
  kwargs: dict = field(default_factory=dict)
  book_ids: set[UUID] | None = None


get_all_test_cases = [
  pytest.param(
    GetAllTestCase(expected_len=len(FAKE_BOOKS)),
    id="without-book_ids",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2}, expected_len=len(FAKE_BOOKS) - 2),
    id="without-book_ids-with-skip",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"limit": 3}, expected_len=3),
    id="without-book_ids-with-limit",
  ),
  pytest.param(
    GetAllTestCase(kwargs={"skip": 2, "limit": 3}, expected_len=3),
    id="without-book_ids-with-skip-n-limit",
  ),
  pytest.param(
    GetAllTestCase(expected_len=3, book_ids=[1, 2, 3]),
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_all_test_cases)
async def test_get_all(
  book_repo: BookRepository, case: GetAllTestCase, seed_books: list[Book]
):
  book_ids: set[UUID] | None = None
  if case.book_ids is not None:
    book_ids = {b.id for b in random.choices(seed_books, k=len(case.book_ids))}

  books = await book_repo.get_all(**case.kwargs, book_ids=book_ids)

  assert len(books) == (case.expected_len) or (
    book_ids is not None and len(books) == len(book_ids)
  )


@dataclass(frozen=True)
class GetByIsbnTestCase:
  isbn: str
  expect_book: bool


get_by_isbn_test_cases = [
  pytest.param(
    GetByIsbnTestCase(isbn=FAKE_BOOKS[0]["isbn"], expect_book=True), id="existing-isbn"
  ),
  pytest.param(
    GetByIsbnTestCase(isbn="invalid-isbn", expect_book=False), id="non-existing-isbn"
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", get_by_isbn_test_cases)
async def test_get_by_isbn(
  book_repo: BookRepository, case: GetByIsbnTestCase, seed_books: list[Book]
):
  book = await book_repo.get_by_isbn(isbn=case.isbn)
  # if book is expected, it has to be not None, otherwise it has to be None.
  assert (case.expect_book and book is not None) or book is None


@dataclass(frozen=True)
class CreateTestCase:
  title: str
  isbn: str
  published_year: int
  # publisher: Publisher # provide in test case
  n_authors: int = 0
  n_categories: int = 0

  expected_exception: Type[Exception] | None = None


create_test_cases = [
  pytest.param(
    CreateTestCase(
      title="Book Title",
      isbn="book-isbn-n",
      published_year=2026,
    ),
    id="without-authors-n-categories",
  ),
  pytest.param(
    CreateTestCase(
      title="Book Title",
      isbn="book-isbn-n",
      published_year=2026,
      n_authors=2,
    ),
    id="with-authors-n-without-categories",
  ),
  pytest.param(
    CreateTestCase(
      title="Book Title",
      isbn="book-isbn-n",
      published_year=2026,
      n_categories=3,
    ),
    id="without-authors-but-with-categories",
  ),
  pytest.param(
    CreateTestCase(
      title="Book Title",
      isbn="book-isbn-n",
      published_year=2026,
      n_authors=2,
      n_categories=3,
    ),
    id="with-authors-n-categories",
  ),
  pytest.param(
    CreateTestCase(
      title="Book Title",
      isbn=FAKE_BOOKS[0]["isbn"],  # already existing isbn
      published_year=2026,
      expected_exception=errors.AlreadyExists,
    ),
    id="duplicate-isbn",
  ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", create_test_cases)
async def test_create(
  book_repo: BookRepository,
  case: CreateTestCase,
  seed_books: list[Book],
  seed_publishers: list[Publisher],  # noqa: F811
  seed_authors: list[Author],  # noqa: F811
  seed_categories: list[Category],  # noqa: F811
):
  publisher = random.choice(seed_publishers)
  authors = random.sample(seed_authors, k=case.n_authors)
  categories = random.sample(seed_categories, k=case.n_categories)

  if case.expected_exception is not None:
    with pytest.raises(case.expected_exception):
      await book_repo.create(
        title=case.title,
        isbn=case.isbn,
        publisher=publisher,  # any random existing publisher
        published_year=case.published_year,
        authors=authors,
        categories=categories,
      )
    return

  book = await book_repo.create(
    title=case.title,
    isbn=case.isbn,
    publisher=publisher,  # any random existing publisher
    published_year=case.published_year,
    authors=authors,
    categories=categories,
  )
  assert book.isbn == case.isbn
  assert book.title == case.title
  assert len(book.authors) == case.n_authors
  assert len(book.categories) == case.n_categories
