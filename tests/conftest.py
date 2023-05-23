import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from auth_server import get_settings


@pytest.fixture(scope='session')
def db_engine():
    """yields a SQLAlchemy engine which is suppressed after the test session"""
    settings = get_settings()
    db_url = settings.papermerge__database__url
    engine = create_engine(db_url, echo=True)

    yield engine

    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """yields a SQLAlchemy connection which is rollbacked after the test"""
    connection = db_engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    yield session

    transaction.rollback()
    session.rollback()
    session.close()
