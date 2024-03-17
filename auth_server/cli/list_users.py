import click
import logging

from sqlalchemy.orm import sessionmaker
from auth_server.db.engine import engine
from auth_server import db


logger = logging.getLogger(__name__)


@click.command()
def cli():
    SessionLocal = sessionmaker(engine)
    session = SessionLocal()

    users = db.get_users(session)

    for user in users:
        print(f"id={user.id} username={user.username} email={user.email}")

    session.close()


if __name__ == '__main__':
    cli()
