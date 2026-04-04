"""Tests for configuration."""

from config import app_config


def test_config_defaults():
    """Test default configuration values."""
    assert app_config.api_url == "https://api.example.com"
    assert app_config.api_timeout == 30
