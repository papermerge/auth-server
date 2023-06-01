import logging
import uuid

from passlib.hash import pbkdf2_sha256
from sqlalchemy import Connection, insert, update, select
from sqlalchemy.orm import Session

from . import models


logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(
        models.User
    ).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(
        select(models.User).where(models.User.email == email)
    )


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user_from_email(db_connection: Connection, email: str) -> None:
    """
    Creates user with its home and inbox folders

    As username first part of the email address will be used i.e.
    the part before '@'.

    Password field will be set a random UUID4 string as it is
    not supposed to be used in this case.
    When user is created from its email, this means that user
    is created via oauth2 provider and thus, authentication
    will be performed via oauth2 provider.
    """
    logger.debug(f"Inserting user with email {email}...")
    username = email.split('@')[0]

    create_user(
        db_connection,
        username=username,
        email=email,
        password=uuid.uuid4().hex,
        is_superuser=False,
        is_active=True
    )


def create_user(
    db_connection: Connection,
    username: str,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    is_superuser: bool = False,
    is_active: bool = False
):
    """Creates a user"""
    kwargs = {
        "username": username,
        "email": email,
        "password": pbkdf2_sha256.hash(password),
        "is_superuser": is_superuser,
        "is_active": is_active
    }
    if first_name:
        kwargs[first_name] = first_name

    if last_name:
        kwargs[last_name] = last_name

    user_id = uuid.uuid4().hex
    home_id = uuid.uuid4().hex
    inbox_id = uuid.uuid4().hex
    kwargs["id"] = user_id

    # insert user model (without home_folder_id and inbox_folder_id)
    db_connection.execute(insert(models.User), kwargs)

    # create .home and .inbox nodes
    db_connection.execute(
        insert(models.Node),
        [
            {
                "id": home_id,
                "title": models.HOME_TITLE,
                "user_id": user_id
            },
            {
                "id": inbox_id,
                "title": models.INBOX_TITLE,
                "user_id": user_id
            }
        ]
    )

    # .home and .inbox nodes are folder instances
    db_connection.execute(
        insert(models.Folder),
        [
            {
                "basetreenode_ptr_id": home_id,
            },
            {
                "basetreenode_ptr_id": inbox_id,
            }
        ]
    )
    # update user's home_folder_id and inbox_folder_id
    db_connection.execute(
        update(models.User)
        .where(models.User.username == username)
        .values(home_folder_id=home_id, inbox_folder_id=inbox_id)
    )
    db_connection.commit()


def get_or_create_user_by_email(
    db_session: Session, email: str
):
    logger.debug(f"get or create user with email: {email}")

    user = get_user_by_email(db_session, email)
    if user is None:
        logger.info(f"User with email {email} is None")
        create_user_from_email(db_session.connection(), email)
        return db_session.scalar(
            select(models.User)
            .where(models.User.email == email)
        )

    logger.debug(f"User with email {email} was found in database")
    return user
