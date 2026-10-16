from fastapi.testclient import TestClient

from niyam.api.app import create_app


def test_ready_returns_200_when_database_is_up() -> None:
    client = TestClient(create_app(database_check=lambda: True))

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "up"}


def test_ready_returns_503_when_database_is_down() -> None:
    client = TestClient(create_app(database_check=lambda: False))

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "database": "down"}


def test_health_stays_ok_when_database_is_down() -> None:
    client = TestClient(create_app(database_check=lambda: False))

    assert client.get("/health").status_code == 200
