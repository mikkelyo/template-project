"""Tests for the API client."""

from template_project.infrastructure.client import APIClient


def test_api_client_init(api_client, app_config):
    """Test that APIClient initializes with config."""
    assert api_client.config == app_config
    assert api_client.session is not None


def test_api_client_has_methods(api_client):
    """Test that APIClient has get and post methods."""
    assert hasattr(api_client, "get")
    assert hasattr(api_client, "post")
    assert callable(api_client.get)
    assert callable(api_client.post)
