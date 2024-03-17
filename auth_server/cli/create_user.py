import click
import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from auth_server.db.engine import engine
from auth_server import db


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
    session = SessionLocal()
    try:
        user = db.get_user_by_username(session, username)
        logger.warning(f"User '{username}' already exists.")
    except NoResultFound:
        pass

    if user is None:
        db.create_user(
            session,
            username=username,
            password=password,
            email=email
        )
        logger.info(f"User '{username}' created.")


if __name__ == '__main__':
    cli()
