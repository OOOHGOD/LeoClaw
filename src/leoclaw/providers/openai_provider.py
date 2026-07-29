"""OpenAI chat-model factory."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def create_openai_model(model_name: str | None = None) -> ChatOpenAI:
    """Create a ChatOpenAI model after loading configuration from ``.env``."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing; add it to .env or the environment")

    return ChatOpenAI(
        model=model_name or os.getenv("OPENAI_MODEL", "gpt-5.6-sol"),
    )


# Backwards-compatible entry point for code that imports this provider directly.
create_model = create_openai_model
