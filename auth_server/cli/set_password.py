import click
import logging

from sqlalchemy.orm import sessionmaker
from auth_server.db.engine import engine
from auth_server import db
from passlib.hash import pbkdf2_sha256


logger = logging.getLogger(__name__)


@click.command()
@click.option('--username', prompt='username')
@click.option(
    '--password',
    prompt='password',
    hide_input=True,
    confirmation_prompt=True
)
def cli(username: str, password: str):
    SessionLocal = sessionmaker(engine)
    session = SessionLocal()

    user = db.get_user_by_username(session, username)
    if not user:
        print("User not found")
        return

    session.add(user)
    user.password = pbkdf2_sha256.hash(password)
    session.commit()

    session.close()


if __name__ == '__main__':
    cli()
