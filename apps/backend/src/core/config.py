from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    INVITE_BASE_URL: str | None = None
    BACKEND_CORS_ORIGINS: str | None = None
    ENABLE_ADMIN_IMPORTS: bool = False
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_BOT_INTERNAL_TOKEN: str | None = None
    MINIO_ENDPOINT: str | None = None
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_BUCKET_PRIVATE: str | None = None
    MINIO_SECURE: bool = False
    MINIO_REGION: str | None = None
    MINIO_PRESIGNED_UPLOAD_TTL_SEC: int = 900
    MINIO_PRESIGNED_DOWNLOAD_TTL_SEC: int = 300
    YANDEX_GEOCODER_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_SYSTEM_PROMPT_PATH: Path = "src/third_party/llm_chat/prompts/emergency_assistant.md"
    ENV: str

settings = Settings()
