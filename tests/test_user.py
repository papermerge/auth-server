import uuid
from sqlalchemy import select

from auth_server.models import User


def test_create_user(db_session):
    user = User(
        id=uuid.uuid4().hex,
        username="one",
        email="one@mail.com",
    )
    db_session.add(user)
    db_session.commit()

    rows = db_session.execute(
        select(User).where(User.username == "one")
    ).all()

    assert len(rows) == 1
