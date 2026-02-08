from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from services.errors import AuthorNotFound, PublisherNotFound, BookCategoryNotFound
from src.logger import get_logger

from core.dependencies import BookService, get_book_service

_BOOK_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "book not found")

book_router = APIRouter(prefix="/books", tags=["books"])

logger = get_logger()


class Book(BaseModel):
  title: str
  isbn: str
  published_year: int
  publisher: str
  authors: list[str] | None
  categories: list[str] | None


@book_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Book])
async def get_all(
  skip: int | None = None,
  limit: int | None = None,
  authors: Annotated[list[str] | None, Query()] = None,
  categories: Annotated[list[str] | None, Query()] = None,
  publishers: Annotated[list[str] | None, Query()] = None,
  book_svc: BookService = Depends(get_book_service),
):
  books_db = await book_svc.get_all(
    skip=skip,
    limit=limit,
    author_names=authors,
    category_names=categories,
    publisher_names=publishers,
  )

  books = [
    Book(
      title=b.title,
      isbn=b.isbn,
      publisher=b.publisher.name,
      published_year=b.published_year,
      authors=[a.name for a in b.authors],
      categories=[c.name for c in b.categories],
    )
    for b in books_db
  ]
  return books


@book_router.post("/", status_code=status.HTTP_201_CREATED)
async def create(book: Book, book_svc: BookService = Depends(get_book_service)):
  try:
    await book_svc.create(
      title=book.title,
      isbn=book.isbn,
      published_year=book.published_year,
      published_by=book.publisher,
      authors=book.authors or [],
      categories=book.categories or [],
    )
  except (AuthorNotFound, BookCategoryNotFound, PublisherNotFound) as e:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.msg)
  except Exception as e:
    logger.error(f"unexpected error: {e}")
