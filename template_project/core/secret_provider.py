"""Secret provider — loads secrets from dynaconf config."""

from template_project.core.configs.llm_config import LLMConfig


class SecretProvider:
    """Reads secrets from the application config."""

    def __init__(self, llm_config: LLMConfig):
        self._llm_config = llm_config

    def anthropic_api_key(self) -> str:
        return self._llm_config.api_key
