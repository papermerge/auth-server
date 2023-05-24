from sqlalchemy import select

from auth_server.models import User
from auth_server.crud import create_user_from_email


def test_create_user_from_email(db_session):

    created_user = create_user_from_email(db_session, 'one@mail.com')

    statement = select(User).where(User.username == "one")
    rows = db_session.execute(statement).all()
    user = rows[0][0]

    assert len(rows) == 1
    assert user.username == 'one'
    assert user.inbox_folder.title == '.inbox'
    assert user.home_folder.title == '.home'
    assert created_user.id == user.id

