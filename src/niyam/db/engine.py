import structlog
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

from niyam.core.config import Settings

logger = structlog.get_logger()


class DatabasePasswordMissingError(RuntimeError):
    """Raised when a database connection is requested but no password is configured"""


def build_database_url(settings: Settings) -> URL:
    if settings.db_password is None:
        raise DatabasePasswordMissingError(
            "NIYAM_DB_PASSWORD is not set. Add it to your .env file."
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def create_db_engine(settings: Settings) -> Engine:
    return create_engine(
        build_database_url(settings),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


def check_database(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.warning("database_check_failed", error=str(error))
        return False
    return True
