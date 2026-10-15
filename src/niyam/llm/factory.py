from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from niyam.core.config import Settings


class ModelNotConfiguredError(RuntimeError):
    """Raised when a model is requested but no model name is configured"""


def build_chat_model(settings: Settings) -> BaseChatModel:
    if not settings.llm_model:
        raise ModelNotConfiguredError(
            "NIYAM_LLM_MODEL is not set. Add a model name to your .env file."
        )

    options: dict[str, Any] = {}
    api_key = settings.google_api_key
    if api_key is not None:
        options["api_key"] = api_key.get_secret_value()

    model: BaseChatModel = init_chat_model(
        settings.llm_model,
        model_provider=settings.llm_provider,
        **options,
    )
    return model
