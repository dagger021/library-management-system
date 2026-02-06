from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import UserRole
from src.core.db import Base

from .mixins import CreatedAtMixin, UuidPkMixin

if TYPE_CHECKING:
  from .member import BookBorrow, MemberDetail


class User(Base, UuidPkMixin, CreatedAtMixin):
  __tablename__ = "users"

  email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
  password: Mapped[str] = mapped_column(String(100))

  role: Mapped[UserRole] = mapped_column(
    Enum(UserRole, name="user_role_enum", native_enum=True), default=UserRole.MEMBER
  )

  is_verified: Mapped[bool] = mapped_column(default=False)
  is_active: Mapped[bool] = mapped_column(default=True)

  # Relationships
  member_detail: Mapped["MemberDetail"] = relationship(
    back_populates="user", cascade="all, delete-orphan", lazy="selectin"
  )
  borrows: Mapped[list["BookBorrow"]] = relationship(back_populates="member")
