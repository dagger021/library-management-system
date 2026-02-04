from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def save(self, *args):
    """Saves/syncs the state into the database."""
    await self.session.flush(*args)
