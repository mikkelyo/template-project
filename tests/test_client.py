"""Tests for infrastructure/client."""

from template_project.infrastructure.client import APIClient


def test_client_init(api_client):
    """Test that client initializes properly."""
    assert api_client.session is not None
