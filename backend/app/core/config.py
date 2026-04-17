from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Project 08 Deep Agents"
    environment: str = "dev"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="project8-deep-agents", alias="LANGSMITH_PROJECT")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langsmith_tracing_enabled: bool = Field(default=False, alias="LANGSMITH_TRACING")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
