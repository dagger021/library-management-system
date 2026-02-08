from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

from .mixins import CreatedAtMixin, IntPkMixin, UpdatedAtMixin

if TYPE_CHECKING:
  from .book import BookCopy
  from .user import User


class MemberDetail(Base, IntPkMixin, CreatedAtMixin, UpdatedAtMixin):
  __tablename__ = "member_details"

  user_id: Mapped[UUID] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
  )

  first_name: Mapped[str] = mapped_column(String(50))
  last_name: Mapped[str] = mapped_column(String(50))
  age: Mapped[int]
  institute_name: Mapped[str] = mapped_column(String(100))

  # Relationships
  user: Mapped["User"] = relationship(back_populates="member_detail")


class BookBorrow(Base, IntPkMixin, CreatedAtMixin):
  __tablename__ = "book_borrows"

  copy_id: Mapped[int] = mapped_column(ForeignKey("book_copies.id", ondelete="CASCADE"))
  member_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

  due_date: Mapped[date]
  returned_at: Mapped[datetime | None]

  # Relationships
  copy: Mapped["BookCopy"] = relationship(back_populates="borrows")
  member: Mapped["User"] = relationship(back_populates="borrows")
  fine: Mapped["Fine"] = relationship(back_populates="borrow")


class Fine(Base, IntPkMixin):
  __tablename__ = "fines"

  borrow_id: Mapped[int] = mapped_column(
    ForeignKey("book_borrows.id", ondelete="CASCADE")
  )
  amount: Mapped[float] = mapped_column(Float(2, True))
  paid: Mapped[bool] = mapped_column(default=False)

  # Relationship
  borrow: Mapped[BookBorrow] = relationship(back_populates="fine")
