from sqlalchemy.engine import URL

from niyam.core.config import Settings


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
