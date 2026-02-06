from sqlalchemy import select

from src.schemas import Publisher

from .base import BaseRepository
from .errors import NotFound
from .modifiers import modify_stmt_for_rate_limit


class PublisherRepository(BaseRepository):
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
    stmt = select(Publisher).where(Publisher.name == publisher_name)
    return await self.session.scalar(stmt)
