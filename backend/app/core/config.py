from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project 08 Deep Agents"
    environment: str = "dev"

    # --- LLM Provider (generic, works for NVIDIA/OpenAI/OpenRouter) ---
    llm_model: str = Field(default="mistralai/mixtral-8x7b-instruct", alias="LLM_MODEL")
    llm_base_url: str = Field(default="https://integrate.api.nvidia.com/v1", alias="LLM_BASE_URL")
    llm_timeout_seconds: int = Field(default=30, alias="LLM_TIMEOUT_SECONDS")
    llm_max_retries: int = Field(default=3, alias="LLM_MAX_RETRIES")

    # --- API Keys (priority: NVIDIA → OpenRouter → OpenAI) ---
    nvidia_api_key: str | None = Field(default=None, alias="NVIDIA_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    # Legacy alias kept for backward compat
    openai_model: str = Field(default="mistralai/mixtral-8x7b-instruct", alias="LLM_MODEL")

    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="project8-deep-agents", alias="LANGSMITH_PROJECT")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langsmith_tracing_enabled: bool = Field(default=True, alias="LANGSMITH_TRACING")

    @property
    def resolved_api_key(self) -> str | None:
        """Returns the first available API key: NVIDIA → OpenRouter → OpenAI."""
        return self.nvidia_api_key or self.openrouter_api_key or self.openai_api_key

    # Async SQLAlchemy URL (Alembic converts +asyncpg → +psycopg for sync migrations).
    database_url: str = Field(
        default="postgresql+asyncpg://project8:project8@127.0.0.1:5432/HelpingHireRecruiter",
        alias="DATABASE_URL",
    )

    # Auth Security
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES") # 24 hours

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
