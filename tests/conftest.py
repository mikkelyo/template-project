"""Test configuration and fixtures."""

import pytest

from template_project.core.config import AppConfig
from template_project.infrastructure.client import APIClient


@pytest.fixture
def app_config():
    """Fixture for application configuration."""
    return AppConfig(api_url="https://api.example.com", api_timeout=30, debug=True)


@pytest.fixture
def api_client(app_config):
    """Fixture for API client."""
    return APIClient(app_config)
