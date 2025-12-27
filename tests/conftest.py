import logging

import httpx
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text, select

from auth_server.db.base import Base
from auth_server.main import app
from auth_server.db.engine import engine, Session
from auth_server.db import orm
from auth_server import const


logger = logging.getLogger(__name__)


@pytest.fixture()
def system_user(db_session) -> orm.User:
    """
    Retrieve or create the system user with special ID.
    System user owns resources created by background tasks
    and initialization scripts.
    """
    stmt = select(orm.User).where(orm.User.id == const.SYSTEM_USER_ID)
    result = db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = orm.User(
            id=const.SYSTEM_USER_ID,
            username="system",
            email="system@local",
            password="-",
            is_superuser=True,
            is_active=False,
            is_staff=False,
            created_by=const.SYSTEM_USER_ID,
            updated_by=const.SYSTEM_USER_ID,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(engine, checkfirst=False)
    with Session() as session:
        try:
            yield session
        finally:
            session.rollback()  # Ensure any uncommitted changes are rolled back

    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()


@pytest.fixture()
def client() -> httpx.Client:
    return TestClient(app)


@pytest.fixture()
def db_engine() -> Engine:
    return engine
