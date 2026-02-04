from uuid import UUID
from sqlalchemy import ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.constants import UserRole

from src.core.db import Base

from .mixins import UuidPkMixin, CreatedAtMixin, UpdatedAtMixin


class User(Base, UuidPkMixin, CreatedAtMixin):
  __tablename__ = "users"

  email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
  password: Mapped[str] = mapped_column(String(100))

  role: Mapped[UserRole] = mapped_column(
    Enum(UserRole, name="user_role_enum", native_enum=True), default=UserRole.STUDENT
  )

  is_verified: Mapped[bool] = mapped_column(default=False)
  is_active: Mapped[bool] = mapped_column(default=True)

  # Relationships
  student_detail: Mapped["StudentDetail"] = relationship(
    "StudentDetail",
    uselist=False,
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="selectin",
  )


class StudentDetail(Base, UuidPkMixin, CreatedAtMixin, UpdatedAtMixin):
  __tablename__ = "student_details"

  user_id: Mapped[UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
  )
  user: Mapped[User] = relationship("User", back_populates="student_detail")

  first_name: Mapped[str] = mapped_column(String(50))
  last_name: Mapped[str] = mapped_column(String(50))
  age: Mapped[int]
  institute_name: Mapped[str] = mapped_column(String(100))
