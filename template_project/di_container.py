"""Dependency Injection Container for the application."""

from dependency_injector import containers, providers

from config import app_config, llm_config
from template_project.infrastructure.api_client import APIClient
from template_project.infrastructure.llm_client import LLMClient


class InfrastructureContainer(containers.DeclarativeContainer):
    """Configs, secrets, and clients."""

    config = providers.Object(app_config)
    llm_cfg = providers.Object(llm_config)

    api_client = providers.Singleton(APIClient, config=config)
    llm_client = providers.Singleton(
        LLMClient,
        api_key=llm_cfg.provided.api_key,
        llm_config=llm_cfg,
    )


class ServicesContainer(containers.DeclarativeContainer):
    """Application services."""

    infrastructure = providers.DependenciesContainer()
