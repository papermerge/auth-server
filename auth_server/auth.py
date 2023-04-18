from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import pbkdf2_sha256

from .crud import get_user_by_username


def verify_password(passowrd: str, hashed_password: str):
    pbkdf2_sha256.verify(passowrd, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta | None = None
):
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


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
