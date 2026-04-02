"""HTTP client for API requests."""

import requests

from template_project.core.config import AppConfig


class APIClient:
    """Simple HTTP client for making API requests."""

    def __init__(self, config: AppConfig):
        """
        Initialize the API client.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.session = requests.Session()

    def get(self, endpoint: str, **kwargs):
        """
        Make a GET request.

        Args:
            endpoint: The API endpoint to call.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            The response object.
        """
        url = f"{self.config.api_url}{endpoint}"
        return self.session.get(url, timeout=self.config.api_timeout, **kwargs)

    def post(self, endpoint: str, **kwargs):
        """
        Make a POST request.

        Args:
            endpoint: The API endpoint to call.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            The response object.
        """
        url = f"{self.config.api_url}{endpoint}"
        return self.session.post(url, timeout=self.config.api_timeout, **kwargs)
