from sqlalchemy import create_engine

from auth_server.config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.papermerge__database__url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
