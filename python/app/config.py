from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/what_eat"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # App
    APP_NAME: str = "What-Eat API"
    APP_HOST: str = "0.0.0.0"  # 允许外部访问
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Draw
    DAILY_FREE_TIMES: int = 3


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
