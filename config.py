"""Root configuration — loads settings.json + .secrets.json via dynaconf."""

from dynaconf import Dynaconf

from template_project.core.configs.app_config import AppConfig
from template_project.core.configs.llm_config import LLMConfig

_raw = Dynaconf(settings_files=["settings.json", ".secrets.json"])

app_config = AppConfig(**_raw.app)
llm_config = LLMConfig(**_raw.llm)
