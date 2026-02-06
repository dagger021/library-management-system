from sqlalchemy import delete, select, insert

from src.schemas import Author
from .modifiers import modify_stmt_for_rate_limit

from .base import BaseRepository
from .errors import NotFound


class AuthorRepository(BaseRepository):
  async def get_all(self, **kwargs):
    stmt = modify_stmt_for_rate_limit(select(Author), **kwargs)
    print(stmt)
    return (await self.session.scalars(stmt)).all()

  async def get_by_names(self, author_names: list[str], strict: bool = False, **kwargs):
    stmt = modify_stmt_for_rate_limit(
      select(Author).where(Author.name.in_(author_names)), **kwargs
    )
    authors = (await self.session.scalars(stmt)).all()
    if strict and len(authors) != len(author_names):
      uncommons = set(author_names).difference(a.name for a in authors)
      raise NotFound("authors not found: `%s`" % ", ".join(uncommons))

    return authors

  async def create(self, *author_names: str):
    if len(author_names) > 0:
      # Bulk insert
      stmt = insert(Author).values([{"name": name} for name in author_names])
      await self.session.execute(stmt)

  async def delete(self, author_ids: list[int]):
    if len(author_ids) > 0:
      # Bulk delete
      stmt = delete(Author).where(Author.id.in_(author_ids))
      await self.session.execute(stmt)
