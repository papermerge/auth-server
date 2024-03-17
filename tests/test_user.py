import logging

import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


from auth_server.database.models import (
    User,
    Node,
    Folder,
    HOME_TITLE,
    INBOX_TITLE
)
from auth_server import database as db
from auth_server.crud import (
    create_user,
    create_user_from_email,
    get_user_by_email,
    get_or_create_user_by_email,
    get_user_by_username
)


logger = logging.getLogger(__name__)


def test_create_user_from_email(db_session):
    user = create_user_from_email(db_session, "john@mail.com")

    stmt_home = select(Folder).join(
        User,
        User.id == Node.user_id
    ).where(
        Node.parent_id == None,
        Node.title == HOME_TITLE,
        User.username == "john"
    )

    stmt_inbox = select(Folder).join(
        User,
        User.id == Node.user_id
    ).where(
        Node.parent_id == None,
        Node.title == INBOX_TITLE,
        User.username == "john"
    )

    home = db_session.execute(stmt_home).one()[0]
    inbox = db_session.execute(stmt_inbox).one()[0]

    # make sure that user's home_folder_id and inbox_folder_id are correct
    assert user.id == home.user.id
    assert user.id == inbox.user.id
    assert user.home_folder_id == home.id
    assert user.inbox_folder_id == inbox.id


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
    create_user_from_email(db_session, "john@mail.com")
    user = get_user_by_email(db_session, "john@mail.com")

    assert user.username == "john"


def test_get_user_by_username_with_scopes(db_session):
    """
    Assert that returned user contains correct scopes

    User inherits his/her scopes from the group he/she belongs
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_group(
        db_session,
        name="g1",
        scopes=["node.create", "node.view"]
    )
    db.create_group(
        db_session,
        name="g2",
        scopes=["tag.create", "tag.view"]
    )
    create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        group_names=["g1", "g2"]  # user
    )
    user = get_user_by_username(db_session, "erasmus")

    assert user.username == "erasmus"
    # check that user inherits all permissions from his/her group
    expected_scopes = {"node.create", "node.view", "tag.create", "tag.view"}
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes
