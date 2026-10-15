from typing import Any

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from pydantic import SecretStr

from niyam.core.config import Settings
from niyam.llm.factory import ModelNotConfiguredError, build_chat_model


def test_missing_model_name_raises_clear_error() -> None:
    settings = Settings(llm_model=None)

    with pytest.raises(ModelNotConfiguredError, match="NIYAM_LLM_MODEL"):
        build_chat_model(settings)


def test_factory_passes_model_provider_and_key_to_langchain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    fake_model = FakeListChatModel(responses=["hi"])

    def fake_init_chat_model(*args: Any, **kwargs: Any) -> FakeListChatModel:
        calls.append((args, kwargs))
        return fake_model

    monkeypatch.setattr("niyam.llm.factory.init_chat_model", fake_init_chat_model)
    settings = Settings(
        llm_model="test-model",
        llm_provider="google_genai",
        google_api_key=SecretStr("secret-value"),
    )

    result = build_chat_model(settings)

    assert result is fake_model
    assert calls == [
        (("test-model",), {"model_provider": "google_genai", "api_key": "secret-value"})
    ]


def test_factory_omits_api_key_when_none_is_configured(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_init_chat_model(*args: Any, **kwargs: Any) -> FakeListChatModel:
        calls.append((args, kwargs))
        return FakeListChatModel(responses=["hi"])

    monkeypatch.setattr("niyam.llm.factory.init_chat_model", fake_init_chat_model)
    settings = Settings(llm_model="test-model", google_api_key=None)

    build_chat_model(settings)

    assert "api_key" not in calls[0][1]