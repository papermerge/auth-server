import logging
import uuid

from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.orm import Session


from auth_server.database import models
from auth_server import constants, schemas, scopes


logger = logging.getLogger(__name__)


def get_user_by_username(
    session: Session,
    username: str
) -> schemas.User | None:
    stmt = select(models.User).where(
        models.User.username == username
    )
    db_user = session.scalars(stmt).one()
    model_user = schemas.User.model_validate(db_user)
    if model_user.is_superuser:
        # superuser has all permissions (permission = scope)
        model_user.scopes = scopes.SCOPES.keys()
    else:
        # user inherits his/her scopes
        # from the direct permissions associated
        # and from groups he/she belongs to
        user_scopes = set()
        user_scopes.update(
            [p.codename for p in db_user.permissions]
        )
        for group in db_user.groups:
            user_scopes.update(
                [p.codename for p in group.permissions]
            )
        model_user.scopes = list(user_scopes)

    return model_user


def get_user_by_email(session: Session, email: str) -> schemas.User | None:

    stmt = select(models.User).where(models.User.email == email)
    db_user = session.scalar(stmt)

    if db_user is None:
        return db_user

    model_user = schemas.User.model_validate(db_user)

    return model_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user_from_email(
    session: Session,
    email: str
) -> schemas.User:
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

    return create_user(
        session,
        username=username,
        email=email,
        password=uuid.uuid4().hex,
        is_superuser=False,
        is_active=True
    )


def create_user(
    session: Session,
    username: str,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    is_superuser: bool = True,
    is_active: bool = True,
    group_names: list[str] = [],
    scopes: list[str] = []
) -> schemas.User:
    """Creates a user"""

    user_id = uuid.uuid4()
    home_id = uuid.uuid4()
    inbox_id = uuid.uuid4()

    db_user = models.User(
        id=user_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
        is_active=is_active,
        password=pbkdf2_sha256.hash(password),
    )
    db_inbox = models.Folder(
        id=inbox_id,
        title=constants.INBOX_TITLE,
        ctype=constants.CTYPE_FOLDER,
        user_id=user_id,
        lang='xxx'  # not used
    )
    db_home = models.Folder(
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
    stmt = select(models.Permission).where(
        models.Permission.codename.in_(scopes)
    )
    perms = session.execute(stmt).scalars().all()

    stmt = select(models.Group).where(
        models.Group.name.in_(group_names)
    )
    groups = session.execute(stmt).scalars().all()
    db_user.groups = groups
    db_user.permissions = perms
    session.commit()

    return schemas.User.model_validate(db_user)


def get_or_create_user_by_email(
    session: Session, email: str
) -> schemas.User:
    logger.debug(f"get or create user with email: {email}")

    user = get_user_by_email(session, email)
    if user is None:
        logger.info(f"User with email {email} is None")
        try:
            create_user_from_email(session, email)
        except Exception:
            logger.exception(
                f"Exception while creating user from email={email}"
            )

        stmt = select(models.User).where(
            models.User.email == email
        )
        user = session.scalar(stmt)

    logger.debug(f"User with email {email} was found in database")

    return user


def create_group(
    session: Session,
    name: str,
    scopes: list[str],
) -> schemas.Group:

    stmt = select(models.Permission).where(
        models.Permission.codename.in_(scopes)
    )
    perms = session.execute(stmt).scalars().all()
    group = models.Group(
        name=name,
        permissions=perms
    )
    session.add(group)
    session.commit()
    result = schemas.Group.model_validate(group)

    return result
