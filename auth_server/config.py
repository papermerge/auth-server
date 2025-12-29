import logging

from functools import lru_cache
from enum import Enum

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    secret_key: str
    db_url: PostgresDsn

    token_algorithm: Algs = Algs.HS256
    token_expire_minutes: int = Field(gt=0, default=1360)
    cookie_name: str = "access_token"

    model_config = SettingsConfigDict(env_prefix='pm_')


@lru_cache()
def get_settings():
    return Settings()
