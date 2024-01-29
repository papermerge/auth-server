import click
import logging

from sqlalchemy.exc import NoResultFound
from auth_server.database.engine import engine
from auth_server.auth import create_token, get_user_by_username


logger = logging.getLogger(__name__)


@click.command()
@click.argument('username')
def cli(username: str):
    """Creates token for given user"""
    user = None
    try:
        user = get_user_by_username(engine, username)
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
