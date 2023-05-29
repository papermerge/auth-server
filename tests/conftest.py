import logging
import pytest

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from auth_server.database import Base

logger = logging.getLogger(__name__)


@pytest.fixture()
def db_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    yield engine


@pytest.fixture(autouse=True)
def setup_db_schema(db_engine: Engine):
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)


@pytest.fixture()
def db_connection(db_engine: Engine):
    with db_engine.begin() as conn:
        yield conn


@pytest.fixture()
def db_session(db_engine: Engine):
    with Session(db_engine) as session:
        yield session
