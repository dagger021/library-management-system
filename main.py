from uvicorn import run
from src.api.main import app  # noqa
from config import get_config

IS_DEV = get_config().is_dev()

if __name__ == "__main__":
  if IS_DEV:
    run("main:app", reload=True, reload_includes="src/**")
  else:
    run("main:app")
