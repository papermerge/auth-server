from enum import Enum
from pydantic import BaseSettings


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
    papermerge__database__url: str = "sqlite+pysqlite:///:memory:"
    papermerge__auth__redirect_url: str = '/app'
    papermerge__auth__google_client_secret: str | None
