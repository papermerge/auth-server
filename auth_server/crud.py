import logging
import uuid

from passlib.hash import pbkdf2_sha256
from sqlalchemy import Connection, select, Engine, text
from sqlalchemy.orm import Session


from auth_server.database import models as db_models2
from auth_server import constants
from auth_server import schemas
from . import models  # TODO: consolidate with db_models2


logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(engine: Engine, username: str) -> schemas.User | None:
    with Session(engine) as session:
        stmt = select(db_models2.User).where(
            db_models2.User.username == username
        )
        db_user = session.scalars(stmt).one()
        model_user = schemas.User.model_validate(db_user)

    return model_user


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
    engine: Engine,
    username: str,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    is_superuser: bool = True,
    is_active: bool = True
):
    """Creates a user"""

    user_id = uuid.uuid4()
    home_id = uuid.uuid4()
    inbox_id = uuid.uuid4()

    with Session(engine) as session:
        db_user = db_models2.User(
            id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_active=is_active,
            password=pbkdf2_sha256.hash(password),
        )
        db_inbox = db_models2.Folder(
            id=inbox_id,
            title=constants.INBOX_TITLE,
            ctype=constants.CTYPE_FOLDER,
            user_id=user_id,
            lang='xxx'  # not used
        )
        db_home = db_models2.Folder(
            id=home_id,
            title=constants.HOME_TITLE,
            ctype=constants.CTYPE_FOLDER,
            user_id=user_id,
            lang='xxx'  # not used
        )
        session.add(db_inbox)
        session.add(db_home)
        session.add(db_user)
        session.commit()
        db_user.home_folder_id = db_home.id
        db_user.inbox_folder_id = db_inbox.id
        session.commit()


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
