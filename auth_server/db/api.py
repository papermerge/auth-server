import uuid
import logging

from passlib.hash import pbkdf2_sha256
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import delete

from auth_server import schema, constants, scopes
from auth_server.db import orm

logger = logging.getLogger(__name__)


def create_group(
    session: Session,
    name: str,
    scopes: list[str],
) -> schema.Group:

    stmt = select(orm.Permission).where(orm.Permission.codename.in_(scopes))
    perms = session.execute(stmt).scalars().all()
    group = orm.Group(name=name, permissions=perms)
    session.add(group)
    session.commit()
    result = schema.Group.model_validate(group)

    return result


def get_perms(db_session: Session) -> list[schema.Permission]:
    with db_session as session:
        db_perms = session.scalars(select(orm.Permission).order_by("codename"))
        model_perms = [
            schema.Permission.model_validate(db_perm) for db_perm in db_perms
        ]

    return model_perms


def sync_perms(db_session: Session):
    """Syncs `core.auth.scopes.SCOPES` with `auth_permissions` table

    In other words makes sure that all scopes defined in
    `core.auth.scopes.SCOPES` are in `auth_permissions` table and other way
    around - any permission found in db table is also in
    `core.auth.scopes.SCOPES`.
    """
    # A. add missing scopes to perms table
    scopes_to_be_added = []
    db_perms = db_session.scalars(select(orm.Permission))
    model_perms = [schema.Permission.model_validate(db_perm) for db_perm in db_perms]
    perms_codenames = [perm.codename for perm in model_perms]

    # collect missing scopes
    for codename, desc in scopes.SCOPES.items():
        if codename not in perms_codenames:
            scopes_to_be_added.append((codename, desc))
    # add missing scopes
    for scope in scopes_to_be_added:
        db_session.add(orm.Permission(codename=scope[0], name=scope[1]))
    db_session.commit()

    # B. removes permissions not present in scopes

    scope_codenames = [scope for scope in scopes.SCOPES.keys()]

    stmt = delete(orm.Permission).where(orm.Permission.codename.notin_(scope_codenames))
    db_session.execute(stmt)
    db_session.commit()


def get_user_uuid(session: Session, user_id: uuid.UUID) -> orm.User:
    stmt = select(orm.User).where(orm.User.id == user_id)

    db_user = session.scalars(stmt).one()

    return db_user


def get_user_by_username(session: Session, username: str) -> schema.User | None:
    stmt = select(orm.User).where(orm.User.username == username)
    db_user = session.scalars(stmt).one()
    model_user = schema.User.model_validate(db_user)
    if model_user.is_superuser:
        # superuser has all permissions (permission = scope)
        model_user.scopes = scopes.SCOPES.keys()
    else:
        # user inherits his/her scopes
        # from the direct permissions associated
        # and from groups he/she belongs to
        user_scopes = set()
        user_scopes.update([p.codename for p in db_user.permissions])
        for group in db_user.groups:
            user_scopes.update([p.codename for p in group.permissions])
        model_user.scopes = list(user_scopes)

    return model_user


def get_user_by_email(session: Session, email: str) -> schema.User | None:

    stmt = select(orm.User).where(orm.User.email == email)
    db_user = session.scalar(stmt)

    if db_user is None:
        return None

    model_user = schema.User.model_validate(db_user)

    if model_user.is_superuser:
        # superuser has all permissions (permission = scope)
        model_user.scopes = scopes.SCOPES.keys()
    else:
        # user inherits his/her scopes
        # from the direct permissions associated
        # and from groups he/she belongs to
        user_scopes = set()
        user_scopes.update([p.codename for p in db_user.permissions])
        for group in db_user.groups:
            user_scopes.update([p.codename for p in group.permissions])
        model_user.scopes = list(user_scopes)

    return model_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.User).offset(skip).limit(limit).all()


def create_user_from_email(session: Session, email: str) -> schema.User:
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
    username = email.split("@")[0]

    return create_user(
        session,
        username=username,
        email=email,
        password=uuid.uuid4().hex,
        is_superuser=False,
        is_active=True,
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
    group_names: list[str] | None = None,
    perm_names: list[str] | None = None,
) -> schema.User:
    """Creates a user"""

    if group_names is None:
        group_names = []
    if perm_names is None:
        perm_names = []

    user_id = uuid.uuid4()
    home_id = uuid.uuid4()
    inbox_id = uuid.uuid4()

    db_user = orm.User(
        id=user_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
        is_active=is_active,
        password=pbkdf2_sha256.hash(password),
    )
    db_inbox = orm.Folder(
        id=inbox_id,
        title=constants.INBOX_TITLE,
        ctype=constants.CTYPE_FOLDER,
        user_id=user_id,
        lang="xxx",  # not used
    )
    db_home = orm.Folder(
        id=home_id,
        title=constants.HOME_TITLE,
        ctype=constants.CTYPE_FOLDER,
        user_id=user_id,
        lang="xxx",  # not used
    )
    session.add(db_inbox)
    session.add(db_home)
    session.add(db_user)
    session.commit()
    db_user.home_folder_id = db_home.id
    db_user.inbox_folder_id = db_inbox.id
    stmt = select(orm.Permission).where(orm.Permission.codename.in_(perm_names))
    perms = session.execute(stmt).scalars().all()

    stmt = select(orm.Group).where(orm.Group.name.in_(group_names))
    groups = session.execute(stmt).scalars().all()
    db_user.groups = groups
    db_user.permissions = perms
    session.commit()

    return schema.User.model_validate(db_user)


def get_or_create_user_by_email(session: Session, email: str) -> schema.User:
    logger.debug(f"get or create user with email: {email}")

    user = get_user_by_email(session, email)
    if user is None:
        logger.info(f"User with email {email} is None")
        try:
            create_user_from_email(session, email)
        except Exception:
            logger.exception(f"Exception while creating user from email={email}")

        stmt = select(orm.User).where(orm.User.email == email)
        user = session.scalar(stmt)

    logger.debug(f"User with email {email} was found in database")

    return user
