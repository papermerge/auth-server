import click


@click.command()
@click.option(
    '--username',
    prompt='Username',
    help='Username of the user instance to be created.'
)
def create_user(username: str):
    print(f"creating user... {username}")


if __name__ == '__main__':
    create_user()
