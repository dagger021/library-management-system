from uuid import UUID

from repositories import (
  AuthorRepository,
  BookCategoryRepository,
  BookRepository,
  PublisherRepository,
)
from repositories import (
  errors as repo_errors,
)

from .base import BaseService
from .errors import (
  AuthorNotFound,
  BookCategoryNotFound,
  BookNotFound,
  PublisherNotFound,
)


class BookService(BaseService):
  def __init__(
    self,
    book_repo: BookRepository,
    author_repo: AuthorRepository,
    publisher_repo: PublisherRepository,
    book_category_repo: BookCategoryRepository,
  ):
    self.book_repo = book_repo
    self.author_repo = author_repo
    self.publisher_repo = publisher_repo
    self.book_category_repo = book_category_repo

  async def create(
    self,
    title: str,
    isbn: str,
    published_year: int,
    published_by: str,
    authors: list[str],
    categories: list[str],
  ):
    """Create book record with publisher, author(s), category(s).

    Args:
      title (str): book title
      isbn (str): book's ISBN
      published_year (str): book's year of publish
      published_by (str): book's publisher
      authors: (list[str]): book's authors
      categories: (list[str]): book's categories

    Raises:
      AuthorNotFound: if one or more authors not exist
      BookCategoryNotFound: if one or more categories not exist
      PublisherNotFound: if the publisher does not exist
    """
    print("service: creating book")
    if (publisher := await self.publisher_repo.get_by_name(published_by)) is None:
      raise PublisherNotFound

    try:
      _authors = await self.author_repo.get_by_names(authors, strict=True)
    except repo_errors.NotFound as e:
      raise AuthorNotFound(e.msg)

    try:
      _categories = await self.book_category_repo.get_by_names(categories, strict=True)
    except repo_errors.NotFound as e:
      raise BookCategoryNotFound(e.msg)

    book = await self.book_repo.create(
      title=title,
      isbn=isbn,
      publisher=publisher,
      published_year=published_year,
      authors=_authors,
      categories=_categories,
    )
    await self.book_repo.commit()

    print("service: created book", book.id, book.isbn)

  async def get_by_isbn(self, *, isbn: str):
    if book := await self.book_repo.get_by_isbn(isbn):
      return book
    raise BookNotFound

  async def get_all(
    self,
    *,
    skip: int | None = 0,
    limit: int | None = None,
    author_names: list[str] | None = None,
    category_names: list[str] | None = None,
    publisher_names: list[str] | None = None,
  ):
    """
    Returns all books searched by authors, categories, and publishers.

    Args:
      limit (int | None): atmost number of books to return
      skip (int | None): skips number of books from start
      authors_names (list[str] | None): search by authors
      category_names (list[str] | None): search by book categories
      publisher_names (list[str] | None): search by publishers

    Returns:
      list[Book]: searched list of books
    """
    book_ids: set[UUID] = set()
    if author_names is not None and len(author_names) > 0:
      authors = await self.author_repo.get_by_names(author_names)
      book_ids.union([b.id for a in authors for b in a.books])

    if category_names is not None and len(category_names) > 0:
      categories = await self.book_category_repo.get_by_names(category_names)
      book_ids.union([b.id for c in categories for b in c.books])

    if publisher_names is not None and len(publisher_names) > 0:
      publishers = await self.publisher_repo.get_by_names(publisher_names)
      book_ids.union([b.id for p in publishers for b in p.books])

    return await self.book_repo.get_all(limit=limit, skip=skip, book_ids=book_ids)
