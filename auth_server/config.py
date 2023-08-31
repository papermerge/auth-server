import logging

from functools import lru_cache
from enum import Enum

from pydantic import BaseSettings


logger = logging.getLogger(__name__)


class Algs(str, Enum):
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"


class Settings(BaseSettings):
    papermerge__security__secret_key: str
    papermerge__security__token_algorithm: Algs = Algs.HS256
    papermerge__security__token_expire_minutes: int = 360

    # database where to read user table from
    papermerge__database__url: str = "sqlite:////db/db.sqlite3"
    papermerge__auth__google_client_secret: str | None
    papermerge__auth__github_client_secret: str | None


@lru_cache()
def get_settings():
    return Settings()
