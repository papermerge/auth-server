import logging
from functools import lru_cache

from .config import Settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_settings():
    logger.info("=========================Getting settings instance===")
    return Settings()
