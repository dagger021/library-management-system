from sqlalchemy import exc, select

from constants import UserRole
from core.security import PasswordHasher
from schemas import User

from .base import BaseRepository
from .errors import AlreadyExists


class UserRepository(BaseRepository):
  async def get_by_email(self, email: str):
    user = await self.session.scalar(select(User).where(User.email == email))
    return user

  async def create(self, email: str, password: str, role: UserRole = UserRole.MEMBER):
    password = PasswordHasher.hash(password)
    self.session.add(user := User(email=email, password=password, role=role))
    try:
      await self.session.flush()
      return user.id
    except exc.IntegrityError as e:
      await self.session.rollback()
      raise AlreadyExists from e    
