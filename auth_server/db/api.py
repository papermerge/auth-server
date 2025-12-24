import uuid
import logging

from typing import Tuple, Dict
from passlib.hash import pbkdf2_sha256
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy import delete

from auth_server import schema, constants, scopes, types
from auth_server.db import orm
from auth_server.db.orm import OwnerType, FolderType, SpecialFolder

logger = logging.getLogger(__name__)


def create_special_folders_for_user(
    session: Session,
    user_id: uuid.UUID,
) -> dict[str, uuid.UUID]:
    """
    Create home and inbox folders for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Dictionary with 'home' and 'inbox' keys mapping to folder IDs
    """
    home_id = uuid.uuid4()
    inbox_id = uuid.uuid4()

    # Create the actual folder nodes WITHOUT user_id
    home_folder = orm.Folder(
        id=home_id,
        title=constants.HOME_TITLE,
        ctype=constants.CTYPE_FOLDER,
        lang="xxx",
    )
    inbox_folder = orm.Folder(
        id=inbox_id,
        title=constants.INBOX_TITLE,
        ctype=constants.CTYPE_FOLDER,
        lang="xxx",
    )

    session.add(home_folder)
    session.add(inbox_folder)
    session.flush()

    # Create special folder entries
    home_special = orm.SpecialFolder(
        owner_type=OwnerType.USER,
        owner_id=user_id,
        folder_type=FolderType.HOME,
        folder_id=home_id,
    )
    inbox_special = orm.SpecialFolder(
        owner_type=OwnerType.USER,
        owner_id=user_id,
        folder_type=FolderType.INBOX,
        folder_id=inbox_id,
    )

    session.add_all([home_special, inbox_special])
    session.flush()

    return {"home": home_id, "inbox": inbox_id}


def create_role(
    db_session: Session, name: str, scopes: list[str], exists_ok: bool = False
) -> Tuple[schema.Role | None, str | None]:
    """Creates a role with given scopes"""
    stmt_total_permissions = select(func.count(orm.Permission.id))
    perms_count = db_session.execute(stmt_total_permissions).scalar()
    if perms_count == 0:
        error = (
            "There are no permissions in the system."
            " Did you forget to run `paper-cli perms sync`?"
        )
        return None, error

    if exists_ok:
        stmt = select(orm.Role).where(orm.Role.name == name)
        result = db_session.execute(stmt).scalars().all()
        if len(result) >= 1:
            logger.info(f"Role {name} already exists")
            return schema.Role.model_validate(result[0]), None

    stmt = select(orm.Permission).where(orm.Permission.codename.in_(scopes))
    perms = db_session.execute(stmt).scalars().all()

    if len(perms) != len(scopes):
        error = f"Some of the permissions did not match scopes. {perms=} {scopes=}"
        return None, error

    role = orm.Role(name=name, permissions=perms)
    db_session.add(role)
    try:
        db_session.commit()
    except Exception as e:
        error_msg = str(e)
        if "UNIQUE constraint failed" in error_msg:
            return None, "Role already exists"

    result = schema.Role.model_validate(role)

    return result, None


def create_group(
    session: Session,
    name: str,
    scopes: list[str],
) -> schema.Group:

    group = orm.Group(name=name)
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
        for role in db_user.roles:
            user_scopes.update([p.codename for p in role.permissions])

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
        for role in db_user.roles:
            user_scopes.update([p.codename for p in role.permissions])

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
    role_names: list[str] | None = None,
) -> schema.User:
    """Creates a user with its home and inbox folders via special_folders table"""

    if role_names is None:
        role_names = []

    user_id = uuid.uuid4()
    create_special_folders_for_user(session, user_id)

    # Step 1: Create user first
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

    session.add(db_user)
    session.flush()

    # Step 3: Add roles if specified
    stmt = select(orm.Role).where(orm.Role.name.in_(role_names))
    roles = session.execute(stmt).scalars().all()
    db_user.roles = roles

    session.commit()

    # Refresh user to get special_folders loaded
    session.refresh(db_user)

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


def set_user_password(db_session: Session, username: str, password: str) -> orm.User:
    stmt = select(orm.User).where(orm.User.username == username)
    db_user = db_session.scalars(stmt).one()

    db_session.add(db_user)
    db_user.password = pbkdf2_sha256.hash(password)
    db_session.commit()

    return db_user
