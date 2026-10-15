from dataclasses import dataclass
from typing import Any

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from pydantic import SecretStr

from niyam.core.config import Settings
from niyam.llm.factory import ModelNotConfiguredError, build_chat_model


@dataclass
class InitSpy:
    """Records how the factory called LangChain, and hands back a fake model."""

    model: FakeListChatModel
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]]


@pytest.fixture
def init_spy(monkeypatch: pytest.MonkeyPatch) -> InitSpy:
    spy = InitSpy(model=FakeListChatModel(responses=["hi"]), calls=[])

    def fake_init_chat_model(*args: Any, **kwargs: Any) -> FakeListChatModel:
        spy.calls.append((args, kwargs))
        return spy.model

    monkeypatch.setattr("niyam.llm.factory.init_chat_model", fake_init_chat_model)
    return spy


def test_missing_model_name_raises_clear_error() -> None:
    settings = Settings(llm_model=None)

    with pytest.raises(ModelNotConfiguredError, match="NIYAM_LLM_MODEL"):
        build_chat_model(settings)


def test_factory_passes_model_provider_and_key_to_langchain(init_spy: InitSpy) -> None:
    settings = Settings(
        llm_model="test-model",
        llm_provider="google_genai",
        google_api_key=SecretStr("secret-value"),
    )

    result = build_chat_model(settings)

    assert result is init_spy.model
    assert init_spy.calls == [
        (("test-model",), {"model_provider": "google_genai", "api_key": "secret-value"})
    ]


def test_factory_omits_api_key_when_none_is_configured(init_spy: InitSpy) -> None:
    settings = Settings(llm_model="test-model", google_api_key=None)

    build_chat_model(settings)

    assert "api_key" not in init_spy.calls[0][1]
