from .base import BaseService
from repositories import AuthorRepository


class AuthorService(BaseService):
  def __init__(self, author_repo: AuthorRepository):
    self.author_repo = author_repo

  async def create(self, author_names: list[str]):
    await self.author_repo.create(author_names=author_names)
    await self.author_repo.commit()

  async def delete(self, author_ids: list[int]):
    await self.author_repo.delete(author_ids=author_ids)
    await self.author_repo.commit()

  async def get_all(self, names: list[str] = [], **kwargs):
    if len(names) > 0:
      return await self.author_repo.get_by_names(author_names=names, **kwargs)
    return await self.author_repo.get_all(**kwargs)
