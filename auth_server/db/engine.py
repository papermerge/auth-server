import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from auth_server.config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.papermerge__database__url
engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)

Session = sessionmaker(engine, expire_on_commit=False)


def get_engine() -> Engine:
    return engine
