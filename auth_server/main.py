import logging
from uuid import UUID

from sqlalchemy.exc import OperationalError, NoResultFound
from fastapi import FastAPI, HTTPException, Response, Request, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
import jwt

from auth_server.auth import authenticate, create_token
from auth_server import schema
from auth_server.config import get_settings
from auth_server import utils
from auth_server.db.engine import Session
from auth_server.db import api as dbapi

app = FastAPI()

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


@app.post("/token")
async def token_endpoint(
    response: Response,
    creds: schema.UserCredentials,
) -> schema.Token:
    """
    Retrieve JWT access token
    """
    try:
        with Session() as db_session:
            user: None | schema.User = authenticate(
                db_session, username=creds.username, password=creds.password
            )
    except ValueError as ex:
        logger.debug(f"ValueError: {ex}")
        raise HTTPException(status_code=400, detail=str(ex)) from ex

    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    access_token = create_token(user)

    response.set_cookie("access_token", access_token)
    response.headers["Authorization"] = f"Bearer {access_token}"

    return schema.Token(access_token=access_token)


@app.get("/verify")
async def verify_endpoint(request: Request) -> Response:
    """
    Returns 200 OK response if and only if JWT token is valid

    JWT token is read either from authorization header or from
    cookie header. Token is considered valid if and only if both
    of the following conditions are true:
    - token was signed with PAPERMERGE__SECURITY__SECRET_KEY
    - User with user_id from the token is present in database
    """
    logger.debug("Verify endpoint")
    token = utils.get_token(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        decoded_token = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.token_algorithm],
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if "sub" not in decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"sub key not present in decoded token",
        )

    user_id = decoded_token["sub"]

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"user_id value is None",
        )

    try:
        with Session() as db_session:
            user = dbapi.get_user_uuid(db_session, UUID(user_id))
    except OperationalError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"DB operation error {exc}",
        )
    except NoResultFound:
        user = None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with ID {user_id} not found in DB",
        )

    return Response(status_code=status.HTTP_200_OK)
