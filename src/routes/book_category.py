from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from src.core.dependencies import get_book_category_service
from src.services import BookCategoryService

from .commons import skip_n_limit

book_category_router = APIRouter()


class BookCategory(BaseModel):
  id: int
  name: str


@book_category_router.get("/categories", status_code=status.HTTP_200_OK)
async def get_all(
  skip_n_limit: Annotated[dict, Depends(skip_n_limit)],
  names: Annotated[list[str] | None, Query()] = None,
  book_category_svc: BookCategoryService = Depends(get_book_category_service),
):
  categories_db = await book_category_svc.get_all(names=names or [], **skip_n_limit)
  return [BookCategory(id=c.id, name=c.name) for c in categories_db]


@book_category_router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create(
  names: list[str],
  book_category_svc: BookCategoryService = Depends(get_book_category_service),
):
  await book_category_svc.create(category_names=names)


@book_category_router.delete("/categories", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many_by_ids(
  category_ids: list[int],
  book_category_svc: BookCategoryService = Depends(get_book_category_service),
):
  await book_category_svc.delete(category_ids=category_ids)


@book_category_router.delete(
  "/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_one_by_id(
  category_id: int,
  book_category_svc: BookCategoryService = Depends(get_book_category_service),
):
  await book_category_svc.delete(category_ids=[category_id])
