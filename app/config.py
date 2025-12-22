from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):

    APP_NAME: str = "Model Select Tool"
    OPENAI_API_KEY: str = "read-from-env"
    RATE_LIMIT: str = "10/minute" # "number/unit"
    RESPONSE_MAX_TOKENS: int = 1000
    MAX_PROMPT_LENGTH: int = 1000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:8000"]

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()


