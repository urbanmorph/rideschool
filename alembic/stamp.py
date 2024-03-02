import os
from pathlib import Path
import json
import click
from alembic import command
from alembic.config import Config

PACKAGE_PATH = Path(os.path.abspath(__file__)).parent.parent


@click.command()
@click.argument('rev_id')
def stamp_revision(rev_id):
    # Load configuration from JSON file
    with open('instance/config.json', "r") as config_file:
        config_data = json.load(config_file)

    # Set the database URL from config
    sqlalchemy_url = (
        f"postgresql://{config_data['DB_USER']}:{config_data['DB_PASSWORD']}@"
        f"{config_data['DB_HOST']}:{config_data['DB_PORT']}/{config_data['DB_NAME']}"
    )
    config = Config(PACKAGE_PATH / 'alembic.ini')
    config.set_main_option('sqlalchemy.url', sqlalchemy_url)
    command.stamp(config, rev_id)


if __name__ == '__main__':
    stamp_revision()