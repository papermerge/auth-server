import click
import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from auth_server.database.engine import engine
from auth_server.crud import create_user, get_user_by_username


logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--username', envvar='PAPERMERGE__AUTH__USERNAME')
@click.option('--email', envvar='PAPERMERGE__AUTH__EMAIL')
@click.option('--password', envvar='PAPERMERGE__AUTH__PASSWORD')
def cli(username: str, email: str | None, password: str):
    if not email:
        email = f'{username}@example.com'

    user = None
    SessionLocal = sessionmaker(engine)
    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
        logger.warning(f"User '{username}' already exists.")
    except NoResultFound:
        pass

    if user is None:
        create_user(
            db,
            username=username,
            password=password,
            email=email
        )
        logger.info(f"User '{username}' created.")






if __name__ == '__main__':
    cli()
