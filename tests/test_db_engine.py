import pytest

from niyam.core.config import Settings
from niyam.db.engine import DatabasePasswordMissingError, build_database_url


def test_url_contains_all_connection_parts(
    monkeypatch: pytest.MonkeyPatch, no_env_file: None
) -> None:
    monkeypatch.setenv("NIYAM_DB_PASSWORD", "secret")
    monkeypatch.setenv("NIYAM_DB_PORT", "5433")

    url = build_database_url(Settings())

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "localhost"
    assert url.port == 5433
    assert url.username == "niyam"
    assert url.database == "niyam"
    assert url.password == "secret"


def test_special_characters_in_password_are_escaped(
    monkeypatch: pytest.MonkeyPatch, no_env_file: None
) -> None:
    monkeypatch.setenv("NIYAM_DB_PASSWORD", "p@ss/word")

    url = build_database_url(Settings())

    assert url.password == "p@ss/word"
    assert "p%40ss%2Fword" in url.render_as_string(hide_password=False)


def test_printing_the_url_hides_the_password(
    monkeypatch: pytest.MonkeyPatch, no_env_file: None
) -> None:
    monkeypatch.setenv("NIYAM_DB_PASSWORD", "secret")

    url = build_database_url(Settings())

    assert "secret" not in str(url)


def test_missing_password_raises_clear_error(no_env_file: None) -> None:
    with pytest.raises(DatabasePasswordMissingError):
        build_database_url(Settings())
