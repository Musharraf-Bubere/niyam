from fastapi.testclient import TestClient

from niyam.api.app import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_path_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/does-not-exist")

    assert response.status_code == 404
