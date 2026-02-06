from .base import BaseService
from src.repositories import BookCategoryRepository


class BookCategoryService(BaseService):
  def __init__(self, book_category_repo: BookCategoryRepository):
    self.book_category_repo = book_category_repo

  async def create(self, category_names: list[str]):
    await self.book_category_repo.create(category_names=category_names)
    await self.book_category_repo.commit()

  async def delete(self, category_ids: list[int]):
    await self.book_category_repo.delete(category_ids=category_ids)
    await self.book_category_repo.commit()

  async def get_all(
    self, names: list[str] = [], skip: int | None = 0, limit: int | None = None
  ):
    if len(names) == 0:
      return await self.book_category_repo.get_all(skip=skip, limit=limit)
    return await self.book_category_repo.get_by_names(
      names=names, skip=skip, limit=limit
    )
