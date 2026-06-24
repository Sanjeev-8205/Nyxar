from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    PROMETHEUS_METRICS_USERNAME: str
    PROMETHEUS_METRICS_PASSWORD: str
    PROTECT_API_KEY: str
    USE_MOCK_LLM: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()