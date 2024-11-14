import logging

import httpx
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import Engine

from auth_server.db.engine import Session
from auth_server.db.base import Base
from auth_server.main import app
from auth_server.db.engine import engine


logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(engine, checkfirst=False)
    with Session() as session:
        yield session

    Base.metadata.drop_all(engine, checkfirst=False)


@pytest.fixture()
def client() -> httpx.Client:
    return TestClient(app)


@pytest.fixture()
def db_engine() -> Engine:
    return engine
