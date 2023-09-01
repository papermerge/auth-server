import click
import logging

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
    SessionLocal = sessionmaker(engine)
    db = SessionLocal()

    if not email:
        email = f'{username}@example.com'

    user = get_user_by_username(db, username)
    if user:
        logger.warning(f"User '{username}' already exists.")
    else:
        create_user(
            db,
            username=username,
            password=password,
            email=email
        )
        logger.info(f"User '{username}' created.")

    db.close()


if __name__ == '__main__':
    cli()
