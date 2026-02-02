from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


class UuidPkMixin:
  """Adds `id` column of **UUID** type, with *primary key* constraint set and
  defaults to `gen_random_uuid()` from PostgreSQL."""

  id: Mapped[UUID] = mapped_column(
    PG_UUID(True), primary_key=True, server_default="gen_random_uuid()"
  )


class CreatedAtMixin:
  """CreatedAtMixin add `created_at` column of **TIMESTAMP** type,
  with default set to `CURRENT_TIMESTAMP`."""

  created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UpdatedAtMixin:
  """UpdatedAtMixin adds `updated_at` column of **TIMESTAMP** type."""

  updated_at: Mapped[datetime] = mapped_column(nullable=True)

  def set_as_updated(self):
    """Sets `updated_at` to current time."""
    self.updated_at = datetime.now(timezone.utc)

  @property
  def is_updated(self):
    """Check if the record is ever updated"""
    return self.updated_at is not None
