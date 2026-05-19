from pathlib import Path

from app.core.config import settings


BASE_DIR = Path(__file__).resolve().parents[2]


# @lru_cache(maxsize=1)
def load_system_prompt() -> str | None:
    path = Path(settings.SYSTEM_PROMPT_PATH)
    if not path.is_absolute():
        path = BASE_DIR / path

    content = path.read_text(encoding="utf-8").strip()
    return content or None
