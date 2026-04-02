"""Tests for configuration."""

from template_project.core.config import AppConfig


def test_config_defaults():
    """Test default configuration values."""
    config = AppConfig()
    assert config.api_url == "https://api.example.com"
    assert config.api_timeout == 30
