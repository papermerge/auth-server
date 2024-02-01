import logging

import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from auth_server.database.models import User, Node, Folder, HOME_TITLE, INBOX_TITLE
from auth_server.crud import (
    create_user,
    create_user_from_email,
    get_user_by_email,
    get_or_create_user_by_email,
    get_user_by_username
)


logger = logging.getLogger(__name__)


def test_create_user_from_email(db_session):
    create_user_from_email(db_session, "john@mail.com")

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

    home_id = db_session.execute(stmt_home).all()[0][1]
    inbox_id = db_session.execute(stmt_inbox).all()[0][1]

    user = db_session.execute(
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


def test_get_user_by_username(db_session):
    create_user(
        db_session,
        username='eugen',
        password='1234',
        email='eugen@mail.com'
    )

    user = get_user_by_username(db_session, 'eugen')

    assert user.username == 'eugen'


def test_get_user_by_username_raises_correct_exception(db_session):
    with pytest.raises(NoResultFound):
        get_user_by_username(db_session, 'no_such_user')


def test_get_user_by_email(db_session):
    create_user_from_email(db_session, "john2@mail.com")
    user = get_user_by_email(db_session, "john2@mail.com")

    assert user.username == "john2"
