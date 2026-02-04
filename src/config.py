from dataclasses import dataclass, fields, MISSING
from os import environ

from dotenv import load_dotenv

load_dotenv()

env_modes = ("development", "production")

ACCESS_JWT_TIMEOUT = 60 # in seconds


@dataclass(frozen=True, slots=True)
class Config:
  JWT_SECRET: str

  DB_URL: str
  DB_URL_ASYNC: str

  ENV_MODE: str
  LOG_LEVEL: str = "INFO"

  def __post_init__(self):
    if len(self.JWT_SECRET) < 32:
      raise ValueError("JWT_SECRET must be at least 32 characters")
    if self.ENV_MODE not in env_modes:
      raise ValueError(f"ENV_MODE must be either of {env_modes}")

  def is_dev(self):
    return self.ENV_MODE == "development"


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
      val = _get_env(
        field.name, field.default if field.default is not MISSING else None
      )

      # Basic type coercion
      if field.type is int:
        try:
          val = int(val)
        except ValueError:
          raise ValueError(f"Invalid value for {field.name!r}: expected int, got str")

      values[field.name] = val

    _CONFIG = Config(**values)

  return _CONFIG
