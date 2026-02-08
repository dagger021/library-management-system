from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constants import BookStatus
from core.db import Base

from .mixins import CreatedAtMixin, IntPkMixin, UuidPkMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .member import BookBorrow

__all__ = (
  "Book",
  "BookCopy",
  "Publisher",
  "Author",
  "Category",
  "BookAuthorAssociation",
  "BookCategoryAssociation",
)


class BookCategoryAssociation(Base):
  __tablename__ = "book_categories"

  book_id: Mapped[UUID] = mapped_column(
    ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
  )
  category_id: Mapped[int] = mapped_column(
    ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
  )


class BookAuthorAssociation(Base):
  __tablename__ = "book_authors"

  book_id: Mapped[UUID] = mapped_column(
    ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
  )
  author_id: Mapped[int] = mapped_column(
    ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
  )


class Author(Base, IntPkMixin):
  __tablename__ = "authors"

  name: Mapped[str] = mapped_column(String(100), unique=True)

  # Relationships
  books: Mapped[list["Book"]] = relationship(
    secondary=BookAuthorAssociation.__tablename__, back_populates="authors"
  )


class Publisher(Base, IntPkMixin):
  __tablename__ = "publishers"

  name: Mapped[str] = mapped_column(String(100), unique=True)

  # Relationships
  books: Mapped[list["Book"]] = relationship(back_populates="publisher")


class Category(Base, IntPkMixin):
  __tablename__ = "categories"

  name: Mapped[str] = mapped_column(String(50), unique=True)

  # Relationships
  books: Mapped[list["Book"]] = relationship(
    secondary=BookCategoryAssociation.__tablename__, back_populates="categories"
  )


class Book(Base, UuidPkMixin):
  __tablename__ = "books"

  title: Mapped[str] = mapped_column(String(255))
  isbn: Mapped[str] = mapped_column(String(20), unique=True)
  publisher_id: Mapped[int] = mapped_column(
    ForeignKey("publishers.id", ondelete="CASCADE")
  )
  published_year: Mapped[int]

  # Relationships
  publisher: Mapped[Publisher] = relationship(back_populates="books")
  authors: Mapped[list[Author]] = relationship(
    secondary=BookAuthorAssociation.__tablename__, back_populates="books"
  )
  categories: Mapped[list[Category]] = relationship(
    secondary=BookCategoryAssociation.__tablename__, back_populates="books"
  )
  copies: Mapped[list["BookCopy"]] = relationship(back_populates="book")


class BookCopy(Base, IntPkMixin, CreatedAtMixin):
  __tablename__ = "book_copies"

  book_id: Mapped[UUID] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
  barcode: Mapped[str] = mapped_column(String(50), unique=True)
  status: Mapped[BookStatus] = mapped_column(
    Enum(BookStatus, name="book_status_enum", native_enum=True),
    default=BookStatus.AVAILABLE,
  )

  # Relationship
  book: Mapped[Book] = relationship(back_populates="copies")
  borrows: Mapped[list["BookBorrow"]] = relationship(back_populates="copy")
