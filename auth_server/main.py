from datetime import timedelta
from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .auth import authenticate_user, create_access_token
from . import models, get_settings, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: Session = Depends(get_db)
) -> schemas.Token:
    """
    username/password based authentication.

    Returns JWT access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )

    access_token_expires = timedelta(
        minutes=settings.papermerge__security__token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
        secret_key=settings.papermerge__security__secret_key,
        algorithm=settings.papermerge__security__token_algorithm
    )

    response.set_cookie('access_token', access_token)
    response.headers['Authorization'] = f"Bearer {access_token}"

    return schemas.Token(access_token=access_token, token_type="bearer")
