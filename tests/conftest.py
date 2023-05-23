import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from auth_server import get_settings


@pytest.fixture(scope='session')
def db_engine():
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    settings = get_settings()
    db_url = settings.papermerge__database__url
    _engine = create_engine(db_url, echo=True)

    yield _engine

    _engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    _session = scoped_session(sessionmaker(bind=db_engine))

    yield _session

    _session.rollback()
    _session.close()
