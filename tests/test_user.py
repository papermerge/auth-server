import logging

from sqlalchemy import select

from auth_server.models import User, Node, Folder, HOME_TITLE, INBOX_TITLE
from auth_server.crud import (
    create_user_from_email,
    get_or_create_user_by_email
)


logger = logging.getLogger(__name__)


def test_create_user_from_email(db_connection):
    create_user_from_email(db_connection, "john@mail.com")

    stmt_home = select(Folder).join(
        Node,
        Node.id == Folder.basetreenode_ptr_id
    ).join(
        User,
        User.id == Node.user_id
    ).where(
        Node.parent_id == None,
        Node.title == HOME_TITLE,
        User.username == "john"
    )

    stmt_inbox = select(Folder).join(
        Node,
        Node.id == Folder.basetreenode_ptr_id
    ).join(
        User,
        User.id == Node.user_id
    ).where(
        Node.parent_id == None,
        Node.title == INBOX_TITLE,
        User.username == "john"
    )

    home_id = db_connection.execute(stmt_home).all()[0][1]
    inbox_id = db_connection.execute(stmt_inbox).all()[0][1]

    user = db_connection.execute(
        select(
            User.id,
            User.username,
            User.home_folder_id,
            User.inbox_folder_id
        ).where(User.username == "john")
    ).all()[0]

    # make sure that user's home_folder_id and inbox_folder_id are correct
    assert user.home_folder_id == home_id
    assert user.inbox_folder_id == inbox_id


def test_get_or_create_user_by_email(db_session):
    user = get_or_create_user_by_email(db_session, "mila@lol.com")

    assert user.username == "mila"
    assert user.home_folder_id
    assert user.inbox_folder_id
