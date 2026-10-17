from logging.config import fileConfig

from alembic import context

from niyam.core.config import Settings
from niyam.db.engine import build_database_url, create_db_engine
from niyam.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Table definitions will be connected here when the models exist (step 2.3c).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL text without connecting (used by 'alembic upgrade --sql)."""
    url = build_database_url(settings=()).render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the real database and apply migrations."""
    engine = create_db_engine(Settings())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
