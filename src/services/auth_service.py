from src.constants import UserRole
from src.core.security import PasswordHasher
from src.core.security.jwt import AuthJWT, AuthPayload
from src.repositories.user_repo import UserRepository

from .base import BaseService
from .errors import InvalidCreds, UserNotFound


class AuthService(BaseService):
  def __init__(self, user_repo: UserRepository, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.user_repo = user_repo

  async def register(
    self, email: str, password: str, role: UserRole = UserRole.STUDENT
  ):
    """
    Register creates a user record in the database.

    :param email: user's email
    :type email: str
    :param password: user's password
    :type password: str
    :param role: user's role [see src.constants.UserRole]
    :type role: UserRole

    Raises:
      repositories.AlreadyExists: if email is already registered
    """
    user_id = await self.user_repo.create(email, password, role)
    return user_id

  async def login(self, email: str, password: str) -> str:
    """
    Docstring for login

    Args:
      email (str): user's email
      password (str): user's password

    Returns:
      str: the jwt token.

    Raises:
      UserNotFound: if the user with email does not exist.
    """
    if (user := await self.user_repo.get_by_email(email)) is None:
      raise UserNotFound

    try:
      is_valid, needs_rehash = PasswordHasher.verify(user.password, password)
      if is_valid and needs_rehash:
        user.password = PasswordHasher.hash(user.password)
        await self.user_repo.save(user)

    except Exception as e:
      raise e

    if not is_valid:
      raise InvalidCreds
    return AuthJWT.sign(AuthPayload(sub=user.email, role=user.role))
