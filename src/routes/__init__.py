from .auth import auth_router
from .book import book_router
from .author import author_router
from .book_category import book_category_router
from .publisher import publisher_router
from fastapi import APIRouter

ROUTERS: tuple[APIRouter, ...] = (
  auth_router,
  book_router,
  author_router,
  book_category_router,
  publisher_router,
)
