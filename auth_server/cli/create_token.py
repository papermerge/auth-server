import click
import logging

from sqlalchemy.orm import sessionmaker
from auth_server.database.engine import engine
from auth_server.auth import create_token, get_user_by_username


logger = logging.getLogger(__name__)


@click.command()
@click.argument('username')
def cli(username: str):
    SessionLocal = sessionmaker(engine)
    db = SessionLocal()

    user = get_user_by_username(db, username)
    token = create_token(user)

    print(token)
    logger.info(token)

    db.close()


if __name__ == '__main__':
    cli()
