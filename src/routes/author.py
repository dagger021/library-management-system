from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from core.dependencies import AuthorService, get_author_service
from repositories.errors import NotFound

from .commons import skip_n_limit

author_router = APIRouter(prefix="/authors", tags=["authors"])


class Author(BaseModel):
  id: int
  name: str


class CreateAuthor(BaseModel):
  name: str


@author_router.get("/", status_code=status.HTTP_200_OK)
async def get_all(
  skip_n_limit: Annotated[dict, Depends(skip_n_limit)],
  names: Annotated[list[str] | None, Query()] = None,
  author_svc: AuthorService = Depends(get_author_service),
):
  """Get all authors, with pagination, and filters."""
  authors_db = await author_svc.get_all(names=names or [], **skip_n_limit)
  return [Author(id=a.id, name=a.name) for a in authors_db]


@author_router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
  authors: list[CreateAuthor], author_svc: AuthorService = Depends(get_author_service)
):
  """Create one author or more than one authors."""
  await author_svc.create([a.name for a in authors])


@author_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many_by_ids(
  author_ids: list[int],
  author_svc: AuthorService = Depends(get_author_service),
):
  """Delete more than one authors by id. More efficient by using bulk deletion."""
  try:
    await author_svc.delete(author_ids=author_ids or [])
  except NotFound as e:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.msg)


@author_router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_by_id(
  author_id: int, author_svc: AuthorService = Depends(get_author_service)
):
  """Delete an author by its id."""
  try:
    await author_svc.delete(author_ids=[author_id])
  except NotFound:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="author not found")
