"""Dependency Injection Container for the application."""

from dependency_injector import containers, providers

from config import settings
from template_project.core.secret_provider import SecretProvider
from template_project.infrastructure.api_client import APIClient
from template_project.infrastructure.llm_client import LLMClient


class InfrastructureContainer(containers.DeclarativeContainer):
    """Configs, secrets, and clients."""

    secrets = providers.Singleton(SecretProvider, llm_config=settings.llm)

    api_client = providers.Singleton(APIClient, config=settings.app)

    llm_client = providers.Singleton(
        LLMClient,
        api_key=secrets.provided.anthropic_api_key.call(),
        llm_config=settings.llm,
    )


class ServicesContainer(containers.DeclarativeContainer):
    """Application services."""

    infrastructure = providers.DependenciesContainer()
