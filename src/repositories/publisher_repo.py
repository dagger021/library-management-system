from psycopg2 import IntegrityError
from sqlalchemy import delete, insert, select

from schemas import Publisher

from .base import BaseRepository
from .errors import AlreadyExists, NotFound
from .modifiers import modify_stmt_for_rate_limit


class PublisherRepository(BaseRepository):
  async def get_all(self, **kwargs):
    """Return list of publishers.

    **kwargs (dict): statement modifier

    Returns:
      Sequence[Publisher]: list of publishers
    """
    stmt = modify_stmt_for_rate_limit(select(Publisher), **kwargs)
    print(stmt)
    return (await self.session.scalars(stmt)).all()

  async def get_by_names(
    self, publisher_names: list[str], strict: bool = False, **kwargs
  ):
    """Return list of publishers matches to the given publisher names.

    Args:
      publisher_names (list[str]): list of publisher names
      strict (bool = `False`): whether to check if all publisher names exists
        in the database, and raises error if not exists.
      **kwargs (dict): statement modifier

    Returns:
      Sequence[BookPublisher]: list of book publishers

    Raises:
      NotFound: if strict is set, and any publisher_names is not in the database
    """
    stmt = modify_stmt_for_rate_limit(
      select(Publisher).where(Publisher.name.in_(publisher_names)), **kwargs
    )
    publishers = (await self.session.scalars(stmt)).all()

    if strict and len(publishers) != len(publisher_names):
      uncommons = set(publisher_names).difference({"name": n} for n in publisher_names)
      raise NotFound("publishers not found: `%s`" % ", ".join(uncommons))

    return publishers

  async def get_by_name(self, publisher_name: str):
    """Return one publisher matches to the given publisher name.

    Args:
      publisher_name (str): publisher name

    Returns:
      Publisher|None: `Publisher` if exists, otherwise `None`.
    """
    stmt = select(Publisher).where(Publisher.name == publisher_name)
    return await self.session.scalar(stmt)

  async def create(self, publisher_names: list[str]):
    """Insert publisher using bulk insert for efficiency.

    Args:
      publisher_names (list[str]): publisher names to insert
    """
    if len(publisher_names) > 0:
      # Bulk insert
      stmt = insert(Publisher).values([{"name": name} for name in publisher_names])
      try:
        await self.session.execute(stmt)
      except IntegrityError as e:
        await self.session.flush()
        raise AlreadyExists from e

  async def delete(self, publisher_ids: list[int]):
    """Delete publisher records by `publisher_ids`.

    Args:
      publisher_ids (list[int]): record ids of the publishers
    """
    if len(publisher_ids) > 0:
      # Bulk delete
      stmt = (
        delete(Publisher).where(Publisher.id.in_(publisher_ids)).returning(Publisher.id)
      )
      deleted_ids = (await self.session.scalars(stmt)).all()
      if len(deleted_ids) != len(publisher_ids):
        uncommons = set(publisher_ids).difference(deleted_ids)
        raise NotFound(
          "one or more publisher not found: %s" % ", ".join(map(repr, uncommons))
        )
