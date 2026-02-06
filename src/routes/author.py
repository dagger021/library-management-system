from typing import Annotated

from fastapi import APIRouter, Query, status, Depends
from pydantic import BaseModel

from src.core.dependencies import AuthorService, get_author_service
from .commons import skip_n_limit

author_router = APIRouter()


class Author(BaseModel):
  id: int
  name: str


@author_router.get("/authors", status_code=status.HTTP_200_OK)
async def get_all(
  skip_n_limit: Annotated[dict, Depends(skip_n_limit)],
  names: Annotated[list[str] | None, Query()] = None,
  author_svc: AuthorService = Depends(get_author_service),
):
  authors_db = await author_svc.get_all(names=names or [], **skip_n_limit)
  return [Author(id=a.id, name=a.name) for a in authors_db]


@author_router.post("/authors", status_code=status.HTTP_201_CREATED)
async def create(
  names: list[str], author_svc: AuthorService = Depends(get_author_service)
):
  await author_svc.create(names)


@author_router.delete("/authors", status_code=status.HTTP_404_NOT_FOUND)
async def delete_many_by_ids(
  author_ids: Annotated[list[int] | None, Query()] = None,
  author_svc: AuthorService = Depends(get_author_service),
):
  await author_svc.delete(author_ids=author_ids or [])


@author_router.delete("/authors/{author_id}", status_code=status.HTTP_404_NOT_FOUND)
async def delete_one_by_id(
  author_id: int, author_svc: AuthorService = Depends(get_author_service)
):
  await author_svc.delete(author_ids=[author_id])
