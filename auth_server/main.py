from datetime import datetime, timedelta
from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .auth import authenticate_user, create_access_token
from . import crud, models, schemas
from .database import SessionLocal, engine
from .config import Settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

settings = Settings()
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
    db: Session = Depends(get_db)
):
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

    return {"access_token": access_token, "token_type": "bearer"}
