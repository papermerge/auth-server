import uuid
from sqlalchemy import select

from auth_server.models import User, Node, Folder


def test_create_user(db_session):
    user = User(
        id=uuid.uuid4().hex,
        username="one",
        email="one@mail.com",
    )
    node = Node(
        id=uuid.uuid4().hex,
        title=".home",
        user=user
    )
    folder = Folder(basetreenode_ptr=node)

    db_session.add(user)
    db_session.add(node)
    db_session.add(folder)
    db_session.commit()

    statement = select(User).where(User.username == "one")
    rows = db_session.execute(statement).all()

    assert len(rows) == 1
    assert rows[0][0].username == 'one'

