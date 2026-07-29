import pytest

import leoclaw.providers.factory as factory_module


def test_create_model_selects_deepseek(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(factory_module, "load_dotenv", lambda: None)
    monkeypatch.setenv("MODEL_PROVIDER", "deepseek")

    import leoclaw.providers.deepseek_provider as provider_module

    monkeypatch.setattr(
        provider_module,
        "create_deepseek_model",
        lambda model_name=None: (sentinel, model_name),
    )

    assert factory_module.create_model("deepseek-v4-pro") == (
        sentinel,
        "deepseek-v4-pro",
    )


def test_create_model_selects_openai(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(factory_module, "load_dotenv", lambda: None)
    monkeypatch.setenv("MODEL_PROVIDER", "openai")

    import leoclaw.providers.openai_provider as provider_module

    monkeypatch.setattr(
        provider_module,
        "create_openai_model",
        lambda model_name=None: (sentinel, model_name),
    )

    assert factory_module.create_model("gpt-5.6-sol") == (
        sentinel,
        "gpt-5.6-sol",
    )


def test_explicit_provider_overrides_environment(monkeypatch):
    monkeypatch.setattr(factory_module, "load_dotenv", lambda: None)
    monkeypatch.setenv("MODEL_PROVIDER", "openai")

    import leoclaw.providers.deepseek_provider as provider_module

    monkeypatch.setattr(
        provider_module,
        "create_deepseek_model",
        lambda model_name=None: "deepseek",
    )

    assert factory_module.create_model(provider="deepseek") == "deepseek"


def test_create_model_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(factory_module, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="Unsupported MODEL_PROVIDER"):
        factory_module.create_model(provider="unknown")
