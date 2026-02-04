from sqlalchemy import select, exc

from src.core.security import PasswordHasher
from src.schemas import User
from .base import BaseRepository
from .errors import AlreadyExists
from src.constants import UserRole


class UserRepository(BaseRepository):
  async def get_by_email(self, email: str):
    user = await self.session.scalar(select(User).where(User.email == email))
    return user

  async def create(self, email: str, password: str, role: UserRole = UserRole.STUDENT):
    password = PasswordHasher.hash(password)
    self.session.add(user := User(email=email, password=password, role=role))
    try:
      await self.session.commit()
      return user.id
    except exc.IntegrityError as e:
      await self.session.rollback()
      raise AlreadyExists from e
