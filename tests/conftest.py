import logging

import httpx
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from auth_server.database.base import Base
from auth_server.main import app
from auth_server.database.engine import engine


logger = logging.getLogger(__name__)


@pytest.fixture()
def db_connection():
    with engine.connect() as conn:
        yield conn


@pytest.fixture(scope="module", autouse=True)
def db_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture()
def db_session():
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client() -> httpx.Client:
    return TestClient(app)
