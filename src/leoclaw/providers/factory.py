"""Provider-aware chat-model factory."""

import os
from typing import Any

from dotenv import load_dotenv


def create_model(
    model_name: str | None = None,
    *,
    provider: str | None = None,
) -> Any:
    """Create the configured provider model.

    ``MODEL_PROVIDER`` accepts ``deepseek`` or ``openai``. The explicit
    ``provider`` argument takes precedence, which is useful for embedding
    LeoClaw in another Python application.
    """
    load_dotenv()
    selected_provider = (
        provider or os.getenv("MODEL_PROVIDER", "deepseek")
    ).strip().lower()

    if selected_provider == "deepseek":
        from leoclaw.providers.deepseek_provider import create_deepseek_model

        return create_deepseek_model(model_name)

    if selected_provider == "openai":
        from leoclaw.providers.openai_provider import create_openai_model

        return create_openai_model(model_name)

    raise RuntimeError(
        "Unsupported MODEL_PROVIDER "
        f"{selected_provider!r}; expected 'deepseek' or 'openai'"
    )
