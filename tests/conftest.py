import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth_server import get_settings


@pytest.fixture()
def session():
    settings = get_settings()
    url = settings.papermerge__database__url

    engine = create_engine(
        url, connect_args={
            "check_same_thread": False
        }
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
