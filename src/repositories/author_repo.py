from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError

from schemas import Author

from .base import BaseRepository
from .errors import NotFound, AlreadyExists
from .modifiers import modify_stmt_for_rate_limit


class AuthorRepository(BaseRepository):
  async def get_all(self, **kwargs):
    """Return list of authors.

    **kwargs (dict): statement modifier

    Returns:
      Sequence[BookCategory]: list of authors
    """
    stmt = modify_stmt_for_rate_limit(select(Author), **kwargs)
    print(stmt)
    return (await self.session.scalars(stmt)).all()

  async def get_by_names(self, author_names: list[str], strict: bool = False, **kwargs):
    """Return list of book authors matches to the given author names.

    Args:
      category_names (list[str]): list of author names
      strict (bool = `False`): whether to check if all author names exists
        in the database, and raises error if not exists.
      **kwargs (dict): statement modifier

    Returns:
      Sequence[Author]: list of book authors

    Raises:
      NotFound: if strict is set, and if any author_names is not in the database
    """
    stmt = modify_stmt_for_rate_limit(
      select(Author).where(Author.name.in_(author_names)), **kwargs
    )
    authors = (await self.session.scalars(stmt)).all()
    if strict:
      if uncommons := set(author_names).difference(a.name for a in authors):
        raise NotFound("authors not found: `%s`" % ", ".join(uncommons))
      print(f"{uncommons = }")

    return authors

  async def create(self, author_names: list[str]):
    """Insert book author records using bulk insert for efficiency.

    Args:
      author_names (list[str]): author names to insert
    """
    if len(author_names) > 0:
      # Bulk insert
      stmt = insert(Author).values([{"name": name} for name in author_names])
      try:
        await self.session.execute(stmt)
      except IntegrityError as e:
        await self.session.flush()
        raise AlreadyExists from e

  async def delete(self, author_ids: list[int]):
    """Delete author record(s) by `author_ids`.

    Args:
      author_ids (list[int]): lists author records ids
    """
    if len(author_ids) > 0:
      # Bulk delete
      stmt = delete(Author).where(Author.id.in_(author_ids)).returning(Author.id)
      deleted_ids = (await self.session.scalars(stmt)).all()
      if len(deleted_ids) != len(author_ids):
        uncommons = set(author_ids).difference(deleted_ids)
        raise NotFound(
          "one or more authors not found: %s" % ", ".join(map(repr, uncommons))
        )
