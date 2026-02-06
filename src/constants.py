from enum import Enum


class UserRole(str, Enum):
    """Enumeration for user roles."""

    ADMIN = "admin"
    MEMBER = "member"


class BookStatus(str, Enum):
    """Enumeration for book's status."""

    LOST = "lost"
    DAMAGED = "damaged"
    BORROWED = "borrowed"
    AVAILABLE = "available"
