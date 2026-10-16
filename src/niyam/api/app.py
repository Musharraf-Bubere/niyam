from collections.abc import Callable
from functools import lru_cache

import structlog
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from sqlalchemy import Engine

from niyam.core.config import Settings
from niyam.db.engine import DatabasePasswordMissingError, check_database, create_db_engine

logger = structlog.get_logger()


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@lru_cache(maxsize=1)
def _get_engine() -> Engine:
    return create_db_engine(Settings())


def _default_database_check() -> bool:
    try:
        return check_database(_get_engine())
    except DatabasePasswordMissingError as error:
        logger.warning("database_not_configured", error=str(error))
        return False


def create_app(database_check: Callable[[], bool] | None = None) -> FastAPI:
    app = FastAPI(title="Niyam")
    is_database_up = database_check or _default_database_check

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/ready")
    def ready(response: Response) -> ReadinessResponse:
        if is_database_up():
            return ReadinessResponse(status="ready", database="up")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status="not_ready", database="down")

    return app
