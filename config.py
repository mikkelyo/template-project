"""Root configuration.

Pydantic models define the shape and defaults; dynaconf layers
settings.json and .secrets.json on top; the merged result is
re-validated through Pydantic so the rest of the app gets typed
config objects.
"""

from dynaconf import Dynaconf
from pydantic import BaseModel

from template_project.core.configs.app_config import AppConfig
from template_project.core.configs.llm_config import LLMConfig


class Settings(BaseModel):
    app: AppConfig
    llm: LLMConfig


_raw = Dynaconf(settings_files=["settings.json", ".secrets.json"])

settings = Settings.model_validate(
    {key.lower(): _raw[key] for key in _raw if key.isupper()}
)
