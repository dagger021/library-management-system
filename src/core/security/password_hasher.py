from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash


class PasswordHasher:
  _hasher = Argon2PasswordHasher()

  @staticmethod
  def hash(password: str):
    return PasswordHasher._hasher.hash(password)

  @staticmethod
  def verify(hashed: str, password: str) -> tuple[bool, bool]:
    try:
      is_valid = PasswordHasher._hasher.verify(hashed, password)
      needs_rehash = is_valid and PasswordHasher._hasher.check_needs_rehash(hashed)
      return is_valid, needs_rehash
    except VerifyMismatchError:
      return False, False
    except InvalidHash:
      return False, False
