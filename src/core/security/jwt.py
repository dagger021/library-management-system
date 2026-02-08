from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel

from config import get_config, ACCESS_JWT_TIMEOUT
from constants import UserRole

_JWT_SECRET = get_config().JWT_SECRET
_JWT_ALGO = "HS256"


class InvalidJWTError(Exception): ...


class ExpiredJWTError(Exception): ...


class JWTPayload(BaseModel):
  exp: datetime | None = None


class AuthPayload(JWTPayload):
  sub: str  # user's id -- email
  role: UserRole


class AuthJWT:
  @staticmethod
  def sign(payload: AuthPayload):
    """Sign the payload into a JWT token (`str`).

    Args:
      payload (AuthPayload): auth payload

    Returns:
      str: the jwt token
    """
    payload.exp = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_JWT_TIMEOUT)
    return jwt.encode(payload.model_dump(), key=_JWT_SECRET, algorithm=_JWT_ALGO)

  @staticmethod
  def validate(token: str):
    """Validate a jwt token.

    Args:
      token (str): JWT Token to validate

    Returns:
      `AuthPayload`

    Raises:
      InvalidJWTError: if the token signature is invalid.
      ExpiredJWTError: if the token is expired.
    """
    try:
      payload = AuthPayload(
        **jwt.decode(token, key=_JWT_SECRET, algorithms=[_JWT_ALGO])
      )
    except jwt.InvalidSignatureError:
      raise InvalidJWTError

    if payload.exp is None:
      raise InvalidJWTError
    if payload.exp < datetime.now(timezone.utc):
      raise ExpiredJWTError

    return payload
