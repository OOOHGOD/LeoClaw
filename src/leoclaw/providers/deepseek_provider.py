"""DeepSeek chat-model factory."""

import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek


def create_deepseek_model(model_name: str | None = None) -> ChatDeepSeek:
    """Create a ChatDeepSeek model after loading configuration from ``.env``."""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is missing; add it to .env or the environment"
        )

    return ChatDeepSeek(
        model=model_name or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        api_key=api_key,
    )
