import uuid

from auth_server.models import User


def test_create_user(session):
    user = User(
        id=str(uuid.uuid4()),
        username="one",
        email="one@mail.com",
    )
    session.add(user)
    session.commit()
