from datetime import datetime

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from services import (
  AuthService,
  BookService,
  AuthorService,
  BookCategoryService,
  PublisherService,
)
from constants import UserRole
from core.db import get_async_session
from core.security import jwt
from src.logger import get_logger
from repositories import (
  AuthorRepository,
  BookCategoryRepository,
  BookRepository,
  PublisherRepository,
  UserRepository,
)

_INVALID_AUTH_TOKEN = HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid auth token")

logger = get_logger()


def get_user_repo(session: AsyncSession = Depends(get_async_session)):
  return UserRepository(session)


def get_book_repo(session: AsyncSession = Depends(get_async_session)):
  return BookRepository(session)


def get_author_repo(session: AsyncSession = Depends(get_async_session)):
  return AuthorRepository(session)


def get_book_category_repo(session: AsyncSession = Depends(get_async_session)):
  return BookCategoryRepository(session)


def get_publisher_repo(session: AsyncSession = Depends(get_async_session)):
  return PublisherRepository(session)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)):
  return AuthService(user_repo=user_repo)


def get_author_service(author_repo: AuthorRepository = Depends(get_author_repo)):
  return AuthorService(author_repo=author_repo)


def get_book_category_service(
  book_category_repo: BookCategoryRepository = Depends(get_book_category_repo),
):
  return BookCategoryService(book_category_repo=book_category_repo)


def get_publisher_service(
  publisher_repo: PublisherRepository = Depends(get_publisher_repo),
):
  return PublisherService(publisher_repo=publisher_repo)


def get_book_service(
  book_repo: BookRepository = Depends(get_book_repo),
  author_repo: AuthorRepository = Depends(get_author_repo),
  book_category_repo: BookCategoryRepository = Depends(get_book_category_repo),
  publisher_repo: PublisherRepository = Depends(get_publisher_repo),
):
  return BookService(
    book_repo=book_repo,
    author_repo=author_repo,
    book_category_repo=book_category_repo,
    publisher_repo=publisher_repo,
  )


class SafeUser(BaseModel):
  email: str
  role: UserRole
  is_verified: bool
  created_at: datetime


class AuthToken(BaseModel):
  token: str


async def get_current_user(
  token: AuthToken, auth_svc: AuthService = Depends(get_auth_service)
):
  """get_current_user parses auth token, fetches user data
  from database, and returns it iff the user is active."""
  parts = token.token.split(" ")
  if len(parts) != 2 or parts[0] != "Bearer":
    raise _INVALID_AUTH_TOKEN

  try:
    payload = jwt.AuthJWT.validate(parts[1])

  except jwt.InvalidJWTError:
    raise _INVALID_AUTH_TOKEN
  except jwt.ExpiredJWTError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED, detail="auth token expired"
    )

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
