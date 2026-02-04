from enum import Enum


class UserRole(str, Enum):
  """Enumeration for user roles."""
  ADMIN = "admin"
  STUDENT = "student"
