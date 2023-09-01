import click

from sqlalchemy.orm import sessionmaker
from auth_server.database.engine import engine
from auth_server.crud import create_user


@click.command()
@click.option(
    '--username',
    prompt='Username',
)
@click.option(
    '--email',
    prompt='Email',
)
@click.option(
    '--password',
    prompt='Password',
    hide_input=True,
    confirmation_prompt=True
)
def cli(username: str, email: str, password: str):
    SessionLocal = sessionmaker(engine)
    db = SessionLocal()
    create_user(
        db,
        username=username,
        password=password,
        email=email
    )
    db.close()


if __name__ == '__main__':
    cli()
