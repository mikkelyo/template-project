"""Tests for configuration."""

from config import settings


def test_settings_file_overrides_pydantic_defaults():
    """settings.json values should override the Pydantic defaults."""
    assert settings.app.api_url == "https://api.example.com"
    assert settings.app.api_timeout == 30
    assert settings.llm.model == "claude-sonnet-4-6"
    assert settings.llm.max_tokens == 4096
    assert settings.llm.temperature == 0.7
