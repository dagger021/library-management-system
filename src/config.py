from dataclasses import dataclass, fields, MISSING
from os import environ
from typing import Any

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Config:
  JWT_SECRET: str

  POSTGRES_DB: str
  POSTGRES_PORT: int
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str

  LOG_LEVEL: str = "info"

  def __post_init__(self):
    if len(self.JWT_SECRET) < 32:
      raise ValueError("JWT_SECRET must be at least 32 characters")
    if 0 > self.POSTGRES_PORT > (1 << 16):
      raise ValueError("POSTGRES_PORT must be between 0-65535")


# using singleton pattern
_CONFIG: Config | None = None


def _get_env(key: str, default) -> str:
  if (val := environ.get(key, default)) is None and type(val) is not str:
    raise RuntimeError(
      f"Missing required env variable: {key!r}."
      "Check `.env` file or runtime environment."
    )
  return val


def get_config():
  """Return the global application configuration.

  The configuration is loaded once (lazy singleton) and then reused.
  This function is safe to call from anywhere in the application.

  Raises:
    RuntimeError: if any required environment variable is missing.
    ValueError: if an environment variable cannot be parsed.
  """
  global _CONFIG

  if _CONFIG is None:
    values = {}
    for field in fields(Config):
      val = _get_env(field.name, field.default if field.default is MISSING else None)

      # Basic type coercion
      if field.type is int:
        try:
          val = int(val)
        except ValueError:
          raise ValueError(f"Invalid value for {field.name!r}: expected int, got str")

      values[field.name] = val

    _CONFIG = Config(**values)

  return _CONFIG
