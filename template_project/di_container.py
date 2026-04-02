"""Dependency Injection Container for the application."""

from dependency_injector import containers, providers

from template_project.core.config import AppConfig
from template_project.infrastructure.client import APIClient


class Container(containers.DeclarativeContainer):
    """Application dependency injection container."""

    config = providers.Singleton(AppConfig)
    api_client = providers.Singleton(APIClient, config=config)
