from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from schemas import Author, Book, Category, Publisher

from .base import BaseRepository
from .errors import AlreadyExists
from .modifiers import modify_stmt_for_rate_limit


class BookRepository(BaseRepository):
  async def get_all(
    self,
    *,
    book_ids: set[UUID] | None = None,
    order_by: list[str] | None = None,
    **kwargs,
  ):
    stmt = select(Book)
    if book_ids is not None and len(book_ids) > 0:
      # filter by book_ids
      stmt = stmt.where(Book.id.in_(book_ids))

    stmt = modify_stmt_for_rate_limit(stmt, **kwargs)
    if order_by is not None:
      stmt = stmt.order_by(*order_by)

    return (await self.session.scalars(stmt)).all()

  async def get_by_title(self, title: str):
    return await self.session.scalar(select(Book).where(Book.title == title))

  async def create(
    self,
    *,
    title: str,
    isbn: str,
    publisher: Publisher,
    published_year: int,
    authors: Sequence[Author],
    categories: Sequence[Category],
  ):
    async with self.session.begin():
      book = Book(
        title=title,
        isbn=isbn,
        publisher=publisher,
        published_year=published_year,
        authors=authors,
        categories=categories,
      )
      self.session.add(book)

    try:
      await self.session.flush()
    except IntegrityError as e:  # violates unique isbn constriant
      await self.session.rollback()
      raise AlreadyExists from e

    return book
