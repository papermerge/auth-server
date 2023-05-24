import logging
from datetime import timedelta
from typing import Annotated
from starlette.datastructures import URL

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .auth import authenticate_user, create_access_token
from . import models, get_settings, schemas
from .database import SessionLocal, engine
from .models import User
from .backends.google import GoogleAuth
from .crud import get_or_create_user_by_email

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.post("/token")
async def token_login(
    creds: schemas.UserCredentials,
    response: Response,
    db: Session = Depends(get_db)
) -> schemas.Token:
    """username/password based authentication"""
    user = authenticate_user(db, creds.username, creds.password)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    access_token = create_token(user)

    response.set_cookie('access_token', access_token)
    response.set_cookie('remote_user', str(user.id))
    response.headers['Authorization'] = f"Bearer {access_token}"
    response.headers['REMOTE_USER'] = str(user.id)

    return schemas.Token(access_token=access_token)


@app.post("/auth")
async def form_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> RedirectResponse:
    """username/password based authentication"""
    user = authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        redirect_url = URL("/").include_query_params(msg="Invalid credentials")
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_303_SEE_OTHER
        )

    access_token = create_token(user)

    response = RedirectResponse(
        url=settings.papermerge__auth__redirect_url,
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie('access_token', access_token)
    response.set_cookie('remote_user', str(user.id))
    response.headers['Authorization'] = f"Bearer {access_token}"
    response.headers['REMOTE_USER'] = str(user.id)

    return response


@app.post("/social/token")
async def social_token(
    client_id: str,
    code: str,
    redirect_uri: str,
    response: Response,
    db: Session = Depends(get_db)
) -> schemas.Token:
    logger.info("Auth with google provider")
    if settings.papermerge__auth__google_client_secret is None:
        raise HTTPException(
            status_code=400,
            detail="Google client secret is empty"
        )

    client = GoogleAuth(
        client_secret=settings.papermerge__auth__google_client_secret,
        client_id=client_id,
        code=code,
        redirect_uri=redirect_uri
    )
    logger.info("Auth:goolgle: sign in")
    try:
        await client.signin()
    except Exception as ex:
        logger.warning(f"Auth:google: sign in failed with {ex}")
        raise HTTPException(
            status_code=401,
            detail=f"401 Unauthorized. Auth provider error: {ex}."
        )

    email = await client.user_email()

    user = get_or_create_user_by_email(db, email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail=f"401 Unauthorized. Failed to fetch user model."
        )
    access_token = create_token(user)

    response.set_cookie('access_token', access_token)
    response.set_cookie('remote_user', str(user.id))
    response.headers['Authorization'] = f"Bearer {access_token}"
    response.headers['REMOTE_USER'] = str(user.id)

    return schemas.Token(access_token=access_token)
