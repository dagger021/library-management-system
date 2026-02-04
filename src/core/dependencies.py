from datetime import datetime

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service import AuthService
from src.constants import UserRole
from src.core.db import get_async_session
from src.core.security import jwt
from src.logger import get_logger
from src.repositories.user_repo import UserRepository

_INVALID_AUTH_TOKEN = HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid auth token")
_EXPIRED_AUTH_TOKEN = HTTPException(status.HTTP_401_UNAUTHORIZED, "expired auth token")

logger = get_logger()


def get_user_repo(session: AsyncSession = Depends(get_async_session)):
  return UserRepository(session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repo)):
  return AuthService(user_repo=user_repo)


AuthServiceDeps: AuthService = Depends(get_user_service)


class SafeUser(BaseModel):
  email: str
  role: UserRole
  is_verified: bool
  created_at: datetime


class AuthToken(BaseModel):
  token: str


async def get_current_user(token: AuthToken, auth_svc=AuthServiceDeps):
  parts = token.token.split(" ")
  if len(parts) != 2 or parts[0] != "Bearer":
    raise _INVALID_AUTH_TOKEN

  try:
    payload = jwt.AuthJWT.validate(parts[1])

  except jwt.InvalidJWTError:
    raise _INVALID_AUTH_TOKEN
  except jwt.ExpiredJWTError:
    raise _EXPIRED_AUTH_TOKEN

  if (user := await auth_svc.user_repo.get_by_email(payload.sub)) is None:
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
  if not user.is_active:
    raise HTTPException(status.HTTP_404_NOT_FOUND, "user not active")

  return SafeUser(
    email=user.email,
    role=user.role,
    is_verified=user.is_verified,
    created_at=user.created_at,
  )


CurrentUserDeps: SafeUser = Depends(get_current_user)
"""CurrentUserDeps parses auth token, fetches user data
   from database, and returns it iff the user is active."""
