import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from niyam.core.config import Settings
from niyam.db.engine import build_database_url, check_database, create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def admin_engine() -> Iterator[Engine]:
    """Connection that can create and drop databases. Skips or fails if Postgre is down"""
    engine = create_engine(
        build_database_url(Settings()),
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 2},
    )
    if not check_database(engine):
        engine.dispose()
        message = "PostgreSQL is not reachable. Start it with: docker compose up -d"
        if os.environ.get("CI"):
            pytest.fail(message)
        pytest.skip(message)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def migrated_engine(admin_engine: Engine) -> Iterator[Engine]:
    """A brand-new database built by the real migrations, deleted afterwards."""
    database_name = f"niyam_test_{uuid.uuid4().hex[:8]}"
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE"{database_name}"'))

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("NIYAM_DB_NAME", database_name)
        command.upgrade(config, "head")
        engine = create_db_engine(Settings())

    yield engine

    engine.dispose()
    with admin_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))


@pytest.fixture
def session(migrated_engine: Engine) -> Iterator[Session]:
    """A session inside a transaction that is rolled back after each test."""
    connection = migrated_engine.connect()
    transaction = connection.begin()
    db_session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield db_session
    db_session.close()
    transaction.rollback()
    connection.close()
