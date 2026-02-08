from sqlalchemy import delete, insert, select
from sqlalchemy.exc import IntegrityError

from schemas import Category

from .base import BaseRepository
from .errors import AlreadyExists, NotFound
from .modifiers import modify_stmt_for_rate_limit


class BookCategoryRepository(BaseRepository):
  async def get_all(self, **kwargs):
    """Return list of book categories.

    **kwargs (dict): statement modifier

    Returns:
      Sequence[BookCategory]: list of book categories
    """
    stmt = modify_stmt_for_rate_limit(select(Category), **kwargs)
    return (await self.session.scalars(stmt)).all()

  async def get_by_names(
    self, category_names: list[str], strict: bool = False, **kwargs
  ):
    """Return list of book categories matches to the given category names.

    Args:
      category_names (list[str]): list of category names
      strict (bool = `False`): whether to check if all category names exists
        in the database, and raises error if not exists.
      **kwargs (dict): statement modifier

    Returns:
      Sequence[BookCategory]: list of book categories

    Raises:
      NotFound: if strict is set, and if any category_names is not in the database
    """
    stmt = modify_stmt_for_rate_limit(
      select(Category).where(Category.name.in_(category_names))
    )
    categories = (await self.session.scalars(stmt)).all()
    if strict and len(category_names) != len(categories):
      uncommons = set(category_names).difference(c.name for c in categories)
      raise NotFound("categories not found: `%s`" % ", ".join(uncommons))

    return categories

  async def create(self, category_names: list[str]):
    """Insert book category records using bulk insert for efficiency.

    Args:
      category_names (list[str]): category names to insert
    """
    if len(category_names) > 0:
      # Bulk insert
      stmt = insert(Category).values([{"name": name} for name in category_names])
      try:
        await self.session.execute(stmt)
      except IntegrityError as e:
        await self.session.flush()
        raise AlreadyExists from e

  async def delete(self, category_ids: list[int]):
    """Delete book category records by book category ids.

    Args:
      category_ids (list[int]): record ids of the book categories
    """
    if len(category_ids) > 0:
      # Bulk delete
      stmt = delete(Category).where(Category.id.in_(category_ids))
      deleted_ids = (await self.session.execute(stmt)).all()
      if len(deleted_ids) != len(category_ids):
        raise NotFound(
          "one or more categories not found: %s"
          % ", ".join(map(repr, set(category_ids)))
        )
