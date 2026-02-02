from uuid import UUID
from sqlalchemy import ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.constants import UserRole

from src.db import Base

from .mixins import UuidPkMixin, CreatedAtMixin, UpdatedAtMixin


class User(Base, UuidPkMixin, CreatedAtMixin):
  __tablename__ = "users"

  email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
  password: Mapped[str] = mapped_column(String(100))

  role: Mapped[UserRole] = mapped_column(
    Enum(UserRole, name="user_role_enum"), default=UserRole.STUDENT
  )

  is_verified: Mapped[bool] = mapped_column(default=False)
  is_active: Mapped[bool] = mapped_column(default=True)

  # Relationships
  student_details: Mapped["StudentDetails"] = relationship(
    "StudentDetails", uselist=False
  )


class StudentDetails(Base, UuidPkMixin, CreatedAtMixin, UpdatedAtMixin):
  __tablename__ = "student_details"

  user_id: Mapped[UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), index=True
  )

  first_name: Mapped[str] = mapped_column(String(50))
  last_name: Mapped[str] = mapped_column(String(50))
  age: Mapped[int]
  institute_name: Mapped[str] = mapped_column(String(100))
