"""Application configuration using pydantic-settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI
    azure_openai_api_key: str | None = None  # Optional: falls back to DefaultAzureCredential
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2025-03-01-preview"
    
    # Deployments
    azure_openai_deployment_name: str = "gpt-4o"  # Primary chat model
    azure_openai_gpt5_deployment_name: str = "gpt-4o-mini"  # Secondary model
    azure_openai_codex_deployment_name: str = "gpt-4o-mini"  # Code tasks fallback when codex access is unavailable
    azure_openai_textembedding_deployment_name: str = "text-embedding-3-small"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/oneshot.db"

    # Application
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Agent settings
    agentflow_max_steps: int = 10
    agentflow_max_time: int = 300
    agentflow_verbose: bool = True

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allowed_origin_regex: str | None = None

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        """Accept comma-separated origins from environment variables."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
