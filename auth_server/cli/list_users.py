import click
import logging

from sqlalchemy.orm import sessionmaker
from auth_server.database.engine import engine
from auth_server.crud import get_users


logger = logging.getLogger(__name__)


@click.command()
def cli():
    SessionLocal = sessionmaker(engine)
    db = SessionLocal()

    users = get_users(db)

    for user in users:
        print(f"id={user.id} username={user.username} email={user.email}")

    db.close()


if __name__ == '__main__':
    cli()
