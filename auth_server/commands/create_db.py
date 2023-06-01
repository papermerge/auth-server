import click

from auth_server.database.base import Base
from auth_server.database.engine import engine
# loads user model into Base.metadata so that engine can create it
from auth_server.models import User  # noqa


@click.command()
def create_db():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_db()
