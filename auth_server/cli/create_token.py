import click
import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from auth_server.db.engine import engine
from auth_server.auth import create_token
from auth_server import db


logger = logging.getLogger(__name__)


@click.command()
@click.argument('username')
def cli(username: str):
    """Creates token for given user"""
    SessionLocal = sessionmaker(engine)
    session = SessionLocal()
    user = None
    try:
        user = db.get_user_by_username(session, username)
    except NoResultFound:
        pass

    if user is None:
        logger.warning(f"User username='{username}' not found")
        return

    token = create_token(user)

    print(token)
    logger.info(token)


if __name__ == '__main__':
    cli()
