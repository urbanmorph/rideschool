from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

import os
import json


from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config



# Calculate the path to the config file relative to the alembic folder
#config_file_path = os.path.join(os.path.dirname(__file__), "instance", "config.json")

# Load configuration from JSON file
with open('instance/config.json', "r") as config_file:
    config_data = json.load(config_file)

# Set the database URL from config
sqlalchemy_url = (
    f"postgresql://{config_data['DB_USER']}:{config_data['DB_PASSWORD']}@"
    f"{config_data['DB_HOST']}:{config_data['DB_PORT']}/{config_data['DB_NAME']}"
)

# Set the dynamic sqlalchemy.url
config.set_main_option("sqlalchemy.url", sqlalchemy_url)




# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
