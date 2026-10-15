import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from niyam.core.config import Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("NIYAM_")]:
        monkeypatch.delenv(name)


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


def test_model_settings_are_empty_by_default() -> None:
    settings = Settings()
    assert settings.llm_provider == "google_genai"
    assert settings.llm_model is None
    assert settings.embedding_model is None
    assert settings.google_api_key is None
    

def test_model_can_be_changed_by_environment_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NIYAM_LLM_MODEL", "any-model-name")
    assert Settings().llm_model == "any-model-name"


def test_api_key_is_hidden_when_printed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NIYAM_GOOGLE_API_KEY", "super-secret-value")
    settings = Settings()
    assert "super-secret-value" not in repr(settings)
    assert "super-secret-value" not in str(settings)
    assert settings.google_api_key is not None
    assert settings.google_api_key.get_secret_value() == "super-secret-value"
