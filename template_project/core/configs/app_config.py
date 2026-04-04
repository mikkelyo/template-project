"""Application configuration."""

from pydantic import BaseModel


class AppConfig(BaseModel):
    api_url: str = "https://api.example.com"
    api_timeout: int = 30
