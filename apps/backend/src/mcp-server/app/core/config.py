import os
from dataclasses import dataclass


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


ENVIRONMENT = os.getenv("ENV", "dev").strip() or "dev"


def _get_str(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value or default


def _get_required(name: str, dev_default: str) -> str:
    value = _get_str(name)
    if value is not None:
        return value
    if ENVIRONMENT != "production":
        return dev_default
    raise RuntimeError(f"Environment variable {name} must be set in production")


@dataclass(frozen=True)
class Settings:
    ENV: str = ENVIRONMENT
    APP_NAME: str = os.getenv("APP_NAME", "PetCare MCP API")
    POSTGRES_URL: str = _get_required(
        "POSTGRES_URL",
        "postgresql+asyncpg://petcare-admin:supersecret@postgres:5432/petcare",
    )
    MINIO_ENDPOINT: str = _get_required("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = _get_required("MINIO_ACCESS_KEY", "petcare")
    MINIO_SECRET_KEY: str = _get_required("MINIO_SECRET_KEY", "petcare123")
    MINIO_BUCKET_PRIVATE: str = _get_required("MINIO_BUCKET_PRIVATE", "petcare-private")
    MINIO_USE_SSL: bool = _get_bool("MINIO_USE_SSL", _get_bool("MINIO_SECURE", False))
    JWT_SECRET_KEY: str = _get_required(
        "JWT_SECRET_KEY",
        "petcare-mcp-local-jwt-secret-change-me",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_EXPIRE_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    )
    AUTH_DEMO_PASSWORD: str = _get_required("AUTH_DEMO_PASSWORD", "petcare-demo-password")
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))
    DEFAULT_LLM: str = os.getenv("DEFAULT_LLM", "gemma")
    GEMMA_ENDPOINT: str | None = os.getenv("GEMMA_ENDPOINT")
    GEMMA_API_KEY: str | None = os.getenv("GEMMA_API_KEY")
    GEMMA_TIMEOUT_SECONDS: int = int(os.getenv("GEMMA_TIMEOUT_SECONDS", "5"))
    OPENROUTER_API_KEY: str | None = _get_str("OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str | None = _get_str("OPENROUTER_MODEL")
    OPENROUTER_BASE_URL: str = _get_str(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1/chat/completions",
    )
    SYSTEM_PROMPT_PATH: str = _get_str(
        "SYSTEM_PROMPT_PATH",
        "app/prompts/emergency_assistant.md",
    )
    OPENROUTER_TIMEOUT_SECONDS: int = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "60"))
    OPENROUTER_MAX_REQUEST_ATTEMPTS: int = int(
        os.getenv("OPENROUTER_MAX_REQUEST_ATTEMPTS", "3")
    )
    OPENROUTER_RETRY_DELAY_SECONDS: float = float(
        os.getenv("OPENROUTER_RETRY_DELAY_SECONDS", "1")
    )


settings = Settings()
