from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel

from core.dependencies import get_publisher_service
from services import PublisherService

from .commons import skip_n_limit
from repositories.errors import NotFound

publisher_router = APIRouter(prefix="/publishers", tags=['publishers'])


class Publisher(BaseModel):
  id: int
  name: str


@publisher_router.get("/", status_code=status.HTTP_200_OK)
async def get_all(
  skip_n_limit: Annotated[dict, Depends(skip_n_limit)],
  names: Annotated[list[str] | None, Query()] = None,
  publisher_svc: PublisherService = Depends(get_publisher_service),
):
  publishers_db = await publisher_svc.get_all(names=names or [], **skip_n_limit)
  return [Publisher(id=c.id, name=c.name) for c in publishers_db]


@publisher_router.post("/", status_code=status.HTTP_201_CREATED)
async def create(
  names: list[str],
  publisher_svc: PublisherService = Depends(get_publisher_service),
):
  await publisher_svc.create(publisher_names=names)


@publisher_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many_by_ids(
  publisher_ids: list[int],
  publisher_svc: PublisherService = Depends(get_publisher_service),
):
  try:
    await publisher_svc.delete(publisher_ids=publisher_ids)

  except NotFound as e:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.msg)


@publisher_router.delete(
  "/{publisher_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_one_by_id(
  publisher_id: int,
  publisher_svc: PublisherService = Depends(get_publisher_service),
):
  try:
    await publisher_svc.delete(publisher_ids=[publisher_id])

  except NotFound:
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="publisher not found")
