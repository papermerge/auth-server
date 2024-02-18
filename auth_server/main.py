import logging

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer

from .auth import authenticate, create_token
from . import schemas
from .config import get_settings
from auth_server.database import get_db

app = FastAPI()


settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


@app.post("/token")
async def retrieve_token(
    response: Response,
    provider: schemas.AuthProvider | None = None,
    client_id: str | None = None,
    code: str | None = None,
    redirect_uri: str | None = None,
    creds: schemas.UserCredentials | None = None,
    db: Session = Depends(get_db)
) -> schemas.Token:
    """
    Retrieve JWT access token
    """
    kwargs = dict(
        code=code,
        redirect_uri=redirect_uri,
        client_id=client_id,
        provider=provider
    )
    if creds:
        kwargs['username'] = creds.username
        kwargs['password'] = creds.password
        kwargs['provider'] = creds.provider.value
    try:
        user = await authenticate(db, **kwargs)
    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        ) from ex

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    access_token = create_token(user)

    response.set_cookie('access_token', access_token)
    response.set_cookie('remote_user', str(user.id))
    response.headers['Authorization'] = f"Bearer {access_token}"
    response.headers['REMOTE_USER'] = str(user.id)

    return schemas.Token(access_token=access_token)
