from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


def create_app() -> FastAPI:
    app = FastAPI(title="Niyam")

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    return app