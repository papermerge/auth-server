import logging

import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


from auth_server.db.orm import User, Node, Folder, HOME_TITLE, INBOX_TITLE
from auth_server.db import api as dbapi
from auth_server import scopes


logger = logging.getLogger(__name__)


def test_create_user_from_email(db_session):
    user = dbapi.create_user_from_email(db_session, "john@mail.com")

    stmt_home = (
        select(Folder)
        .join(User, User.id == Node.user_id)
        .where(
            Node.parent_id == None, Node.title == HOME_TITLE, User.username == "john"
        )
    )

    stmt_inbox = (
        select(Folder)
        .join(User, User.id == Node.user_id)
        .where(
            Node.parent_id == None, Node.title == INBOX_TITLE, User.username == "john"
        )
    )

    home = db_session.execute(stmt_home).one()[0]
    inbox = db_session.execute(stmt_inbox).one()[0]

    # make sure that user's home_folder_id and inbox_folder_id are correct
    assert user.id == home.user.id
    assert user.id == inbox.user.id
    assert user.home_folder_id == home.id
    assert user.inbox_folder_id == inbox.id


def test_get_or_create_user_by_email(db_session):
    user = dbapi.get_or_create_user_by_email(db_session, "mila@lol.com")

    assert user.username == "mila"
    assert user.home_folder_id
    assert user.inbox_folder_id


def test_get_user_by_username(db_session):
    dbapi.create_user(
        db_session, username="eugen", password="1234", email="eugen@mail.com"
    )

    user = dbapi.get_user_by_username(db_session, "eugen")

    assert user.username == "eugen"


def test_get_user_by_username_raises_correct_exception(db_session):
    with pytest.raises(NoResultFound):
        dbapi.get_user_by_username(db_session, "no_such_user")


def test_get_user_by_email(db_session):
    dbapi.create_user_from_email(db_session, "john@mail.com")
    user = dbapi.get_user_by_email(db_session, "john@mail.com")

    assert user.username == "john"


def test_user_inherits_from_groups(db_session):
    """
    `get_user_by_username` return user with correct scopes

    User inherits his/her scopes from the group he/she belongs
    """
    # make sure all scope values are in DB
    dbapi.sync_perms(db_session)

    dbapi.create_group(db_session, name="g1", scopes=["node.create", "node.view"])
    dbapi.create_group(db_session, name="g2", scopes=["tag.create", "tag.view"])
    dbapi.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        group_names=["g1", "g2"],  # user inherits scopes from these groups
    )
    user = dbapi.get_user_by_username(db_session, "erasmus")

    assert user.username == "erasmus"
    # check that user inherits all permissions from his/her group
    expected_scopes = {"node.create", "node.view", "tag.create", "tag.view"}
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_user_inherits_scopes_from_perms(db_session):
    """
    `get_user_by_username` return user with correct scopes

    User inherits his/her scopes from his/her direct permissions
    """
    # make sure all scope values are in DB
    dbapi.sync_perms(db_session)

    dbapi.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        perm_names=["page.move", "page.extract"],
    )
    user = dbapi.get_user_by_username(db_session, "erasmus")

    assert user.username == "erasmus"
    # check that user inherits his/her direct permissions
    expected_scopes = {"page.move", "page.extract"}
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_user_inherits_scopes_from_perms_and_groups(db_session):
    """
    `get_user_by_username` return user with correct scopes

    User inherits his/her scopes from his/her direct permissions and groups
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_group(db_session, name="g1", scopes=["node.create", "node.view"])
    db.create_group(db_session, name="g2", scopes=["tag.create", "tag.view"])

    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        perm_names=["page.move", "page.extract"],
        group_names=["g1", "g2"],
    )
    user = db.get_user_by_username(db_session, "erasmus")

    assert user.username == "erasmus"
    # check that user inherits scopes from his/her direct permissions and groups
    expected_scopes = {
        "page.move",
        "page.extract",
        "node.create",
        "node.view",
        "tag.create",
        "tag.view",
    }
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_get_user_by_email_inherits_scopes_from_groups(db_session):
    """
    `get_user_by_email` return user with correct scopes

    User inherits his/her scopes from the group he/she belongs
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_group(db_session, name="g1", scopes=["node.create", "node.view"])
    db.create_group(db_session, name="g2", scopes=["tag.create", "tag.view"])
    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        group_names=["g1", "g2"],  # user inherits scopes from these groups
    )
    user = db.get_user_by_email(db_session, "erasmus@mail.com")

    assert user.username == "erasmus"
    # check that user inherits all permissions from his/her group
    expected_scopes = {"node.create", "node.view", "tag.create", "tag.view"}
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_get_user_by_email_scopes_from_perms(db_session):
    """
    `get_user_by_email` return user with correct scopes

    User inherits his/her scopes from his/her direct permissions
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        perm_names=["page.move", "page.extract"],
    )
    user = db.get_user_by_email(db_session, "erasmus@mail.com")

    assert user.username == "erasmus"
    # check that user inherits his/her direct permissions
    expected_scopes = {"page.move", "page.extract"}
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_get_user_by_email_inherits_scopes_from_perms_and_groups(db_session):
    """
    `get_user_by_email` return user with correct scopes

    User inherits his/her scopes from his/her direct permissions and groups
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_group(db_session, name="g1", scopes=["node.create", "node.view"])
    db.create_group(db_session, name="g2", scopes=["tag.create", "tag.view"])

    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
        perm_names=["page.move", "page.extract"],
        group_names=["g1", "g2"],
    )
    user = db.get_user_by_email(db_session, "erasmus@mail.com")

    assert user.username == "erasmus"
    # check that user inherits scopes from his/her direct permissions and groups
    expected_scopes = {
        "page.move",
        "page.extract",
        "node.create",
        "node.view",
        "tag.create",
        "tag.view",
    }
    actual_scopes = set(user.scopes)
    assert actual_scopes == expected_scopes


def test_get_user_by_email_for_superuser(db_session):
    """
    `get_user_by_email` return user with correct scopes

    User inherits all scopes if he/she is superuser
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=True,
    )
    user = db.get_user_by_email(db_session, "erasmus@mail.com")

    assert user.username == "erasmus"
    assert len(user.scopes) == len(scopes.SCOPES)


def test_get_user_by_email_for_non_superuser(db_session):
    """
    `get_user_by_email` return user with correct scopes

    User inherits all scopes if he/she is superuser.
    In this case user not superuser and does not have any perms
    groups assigned
    """
    # make sure all scope values are in DB
    db.sync_perms(db_session)

    db.create_user(
        db_session,
        username="erasmus",
        email="erasmus@mail.com",
        password="freewill41",
        is_superuser=False,
    )
    user = db.get_user_by_email(db_session, "erasmus@mail.com")

    assert user.username == "erasmus"
    # user is not superuser and does not have any
    # group/perms associated
    assert len(user.scopes) == 0
