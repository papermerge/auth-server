import uuid
from sqlalchemy.orm import Session

from . import models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(
        models.User
    ).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user_from_email(db_session: Session, email: str):
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
    username = email.split('@')[0]
    user = models.User(
        id=uuid.uuid4().hex,
        username=username,
        password=uuid.uuid4().hex,
        email=email,
    )
    home = models.Node(
        id=uuid.uuid4().hex,
        title=".home",
        user=user
    )
    home_folder = models.Folder(basetreenode_ptr=home)

    inbox = models.Node(
        id=uuid.uuid4().hex,
        title=".inbox",
        user=user
    )
    inbox_folder = models.Folder(basetreenode_ptr=inbox)

    db_session.add(user)
    db_session.add(home)
    db_session.add(home_folder)
    db_session.commit()

    db_session.add(inbox)
    db_session.add(inbox_folder)
    db_session.commit()

    return user
