from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",  # apps/backend/.env
        extra="ignore"
    )

    DATABASE_URL: str


settings = Settings()