import logging
from uuid import UUID

from sqlalchemy.exc import OperationalError, NoResultFound
from fastapi import FastAPI, HTTPException, Response, Request, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from auth_server.auth import authenticate, create_token
from auth_server.backends.oidc import introspect_token
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
    provider: schema.AuthProvider | None = None,
    client_id: str | None = None,
    code: str | None = None,
    redirect_url: str | None = None,
    creds: schema.UserCredentials | None = None,
) -> schema.Token:
    """
    Retrieve JWT access token
    """
    kwargs = dict(
        code=code, redirect_url=redirect_url, client_id=client_id, provider=provider
    )
    if creds:
        kwargs["username"] = creds.username
        kwargs["password"] = creds.password
        kwargs["provider"] = creds.provider.value
    try:
        with Session() as db_session:
            user_or_token: None | str | schema.User = await authenticate(
                db_session, **kwargs
            )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex

    if user_or_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if isinstance(user_or_token, schema.User):
        # user was returned e.g. when using DB auth
        access_token = create_token(user_or_token)
    else:
        # token string was returned e.g. when using OIDC provider
        access_token = user_or_token

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

    if settings.papermerge__auth__oidc_introspect_url:
        logger.debug("Found OIDC introspect endpoint")
        # OIDC introspection point is provided ->
        # ask OIDC provider if token is active
        # # https://datatracker.ietf.org/doc/html/rfc7662
        # here we verify (=instrospect) token issued by OIDC provider
        valid_token = await introspect_token(
            settings.papermerge__auth__oidc_introspect_url,
            token=token,
            client_secret=settings.papermerge__auth__oidc_client_secret,
            client_id=settings.papermerge__auth__oidc_client_id,
        )
        if valid_token:
            logger.debug("Introspect: token valid")
            return Response(status_code=status.HTTP_200_OK)
        else:
            logger.debug("Introspect: token NOT valid!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Introspection says: token is not active",
            )
    # non OIDC flow
    # here we verify token which was issued by papermerge auth server
    logger.debug("non OIDC flow")
    try:
        decoded_token = jwt.decode(
            token,
            settings.papermerge__security__secret_key,
            algorithms=[settings.papermerge__security__token_algorithm],
        )
    except JWTError:
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
