import click

from rich.console import Console
from sqlalchemy.orm import sessionmaker
from auth_server.db.engine import engine
from auth_server.auth import db_auth


console = Console()

@click.command()
@click.option(
    '--username',
    prompt='Username',
)
@click.option(
    '--password',
    prompt='Password',
    hide_input=True
)
def cli(username: str, password: str):
    SessionLocal = sessionmaker(engine)
    session = SessionLocal()
    user = db_auth(session, username, password)

    if user:
        console.print("Credentials are [bold]correct[/bold]", style="green")
    else:
        console.print("Credentials are [bold]wrong[/bold]", style="red")

    session.close()


if __name__ == '__main__':
    cli()
