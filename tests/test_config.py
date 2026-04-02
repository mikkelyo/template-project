"""Tests for the configuration module."""

from template_project.core.config import AppConfig


def test_app_config_defaults():
    """Test that AppConfig loads with default values."""
    config = AppConfig()
    assert config.api_url == "https://api.example.com"
    assert config.api_timeout == 30
    assert config.debug is False


def test_app_config_custom():
    """Test that AppConfig accepts custom values."""
    config = AppConfig(api_url="https://custom.api.com", api_timeout=60, debug=True)
    assert config.api_url == "https://custom.api.com"
    assert config.api_timeout == 60
    assert config.debug is True
