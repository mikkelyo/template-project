"""Application configuration."""

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration settings."""

    api_url: str = "https://api.example.com"
    api_timeout: int = 30
    debug: bool = False

    class Config:
        env_file = ".env"
