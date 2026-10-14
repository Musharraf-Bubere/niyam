from pathlib import Path

import pytest
from pydantic import ValidationError

from niyam.core.config import Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for name in ("NIYAM_APP_NAME", "NIYAM_ENVIRONMENT", "NIYAM_LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


def test_defaults() -> None:
    settings = Settings()
    assert settings.app_name == "niyam"
    assert settings.environment == "local"
    assert settings.log_level == "INFO"


def test_env_var_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NIYAM_LOG_LEVEL", "DEBUG")
    assert Settings().log_level == "DEBUG"


def test_invalid_log_level_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NIYAM_LOG_LEVEL", "LOUD")
    with pytest.raises(ValidationError):
        Settings()
