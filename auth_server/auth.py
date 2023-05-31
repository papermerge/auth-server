import logging

from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import pbkdf2_sha256

from fastapi import HTTPException

from .crud import get_user_by_username, get_or_create_user_by_email
from .models import User
from .config import Settings
from .backends import GoogleAuth


logger = logging.getLogger(__name__)
settings = Settings()


async def authenticate(
    db: Session,
    *,
    username: str | None = None,
    password: str | None = None,
    provider: str | None = None,
    client_id: str | None = None,
    code: str | None = None,
    redirect_uri: str | None = None
) -> User | None:
    if username and password:
        # password based authentication against database
        return db_auth(db, username, password)

    if provider == "google":
        # oauth 2.0, google provider
        return await google_auth(
            db,
            client_id=client_id,
            code=code,
            redirect_uri=redirect_uri
        )

    return None


def verify_password(password: str, hashed_password: str):
    return pbkdf2_sha256.verify(password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm
    )
    return encoded_jwt


def db_auth(db, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)

    if not user:
        return None
    if not verify_password(password, user.password):
        return None

    return user


async def google_auth(
    db: Session,
    client_id: str,
    code: str,
    redirect_uri: str
) -> User | None:
    if settings.papermerge__auth__google_client_secret is None:
        raise HTTPException(
            status_code=400,
            detail = "Google client secret is empty"
        )

    client = GoogleAuth(
        client_secret = settings.papermerge__auth__google_client_secret,
        client_id=client_id,
        code=code,
        redirect_uri = redirect_uri
    )

    logger.debug("Auth:google: sign in")

    try:
        await client.signin()
    except Exception as ex:
        logger.warning(f"Auth:google: sign in failed with {ex}")

        raise HTTPException(
            status_code=401,
            detail = f"401 Unauthorized. Auth provider error: {ex}."
        )

    email = await client.user_email()

    return get_or_create_user_by_email(db, email)


def create_token(user: User) -> str:
    access_token_expires = timedelta(
        minutes=settings.papermerge__security__token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires,
        secret_key=settings.papermerge__security__secret_key,
        algorithm=settings.papermerge__security__token_algorithm
    )

    return access_token
