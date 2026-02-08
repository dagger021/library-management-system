from .base import BaseService
from repositories import PublisherRepository


class PublisherService(BaseService):
  def __init__(self, publisher_repo: PublisherRepository):
    self.publisher_repo = publisher_repo

  async def create(self, publisher_names: list[str]):
    await self.publisher_repo.create(publisher_names=publisher_names)
    await self.publisher_repo.commit()

  async def delete(self, publisher_ids: list[int]):
    await self.publisher_repo.delete(publisher_ids=publisher_ids)
    await self.publisher_repo.commit()

  async def get_all(self, names: list[str] = [], **kwargs):
    if len(names) == 0:
      return await self.publisher_repo.get_all(**kwargs)
    return await self.publisher_repo.get_by_names(names=names, **kwargs)
