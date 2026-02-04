import logging

from src.config import get_config

# basic logger configuration
logging.basicConfig(
  level=get_config().LOG_LEVEL,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  handlers=[logging.StreamHandler()],
)


def get_logger():
  return logging.getLogger(__name__)
