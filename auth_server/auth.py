import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from datetime import datetime, timedelta, UTC
import jwt
from passlib.hash import pbkdf2_sha256

from fastapi import HTTPException

from auth_server.db import api as dbapi
from auth_server.db.orm import User
from auth_server import schema
from auth_server.config import Settings
from auth_server.utils import raise_on_empty


logger = logging.getLogger(__name__)
settings = Settings()


def authenticate(
    session: Session,
    username: str,
    password: str,
) -> schema.User | str | None:
    return db_auth(session, username, password)


def verify_password(password: str, hashed_password: str) -> bool:
    logger.debug("checking credentials...")
    return pbkdf2_sha256.verify(password, hashed_password)


def create_access_token(
    data: schema.TokenData,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta | None = None,
) -> str:
    logger.debug(f"create access token for data={data}")

    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    except Exception as exc:
        logger.error(exc)
        raise

    return encoded_jwt


def db_auth(session: Session, username: str, password: str) -> schema.User | None:
    """Authenticates user based on username and password

    User data is read from database.
    """
    logger.info(f"Database based authentication for '{username}'")

    try:
        user: schema.User | None = dbapi.get_user_by_username(session, username)
    except NoResultFound:
        user = None

    if not user:
        logger.warning(f"User {username} not found in database")
        return None

    if not verify_password(password, user.password):
        logger.warning(f"Authentication failed for '{username}'")
        return None

    logger.info(f"Authentication succeded for '{username}'")
    return user


def create_token(user: schema.User) -> str:
    access_token_expires = timedelta(
        minutes=settings.papermerge__security__token_expire_minutes
    )
    data = schema.TokenData(
        sub=str(user.id),
        preferred_username=user.username,
        email=user.email,
        scopes=user.scopes,
    )

    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires,
        secret_key=settings.papermerge__security__secret_key,
        algorithm=settings.papermerge__security__token_algorithm,
    )

    return access_token
