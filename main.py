from uvicorn import run
from src.api.main import app  # noqa

if __name__ == "__main__":
  run("main:app", reload=True, reload_includes="src/**")
