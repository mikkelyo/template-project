"""HTTP clients for downstream systems."""

from template_project.infrastructure.clients.example_client import (
    ExampleClient,
    create_example_client,
)

__all__ = ["ExampleClient", "create_example_client"]
