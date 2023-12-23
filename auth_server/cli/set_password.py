import click
import logging

from sqlalchemy.orm import sessionmaker
from auth_server.database.engine import engine
from auth_server.crud import get_user_by_username


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
    db = SessionLocal()

    user = get_user_by_username(db, username)
    if not user:
        print("User not found")
        return

    db.add(user)
    user.password = pbkdf2_sha256.hash(password)
    db.commit()

    db.close()


if __name__ == '__main__':
    cli()
