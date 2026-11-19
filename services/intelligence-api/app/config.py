"""Configuration, read only from environment variables (nothing hard-coded)."""

import os


def _list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
CORS_ORIGINS = _list(os.getenv("CORS_ORIGINS", "http://localhost:5173"))
APP_VERSION = os.getenv("APP_VERSION", "dev")
RUN_MIGRATIONS = os.getenv("RUN_MIGRATIONS", "1") == "1"
DB_WAIT_S = int(os.getenv("DB_WAIT_S", "180"))

# Optional LLM for suggested replies (OpenAI-compatible chat completions API).
# Off unless LLM_API_KEY is set; the key is a GitHub secret passed as a Container Apps secret.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT_S = float(os.getenv("LLM_TIMEOUT_S", "4"))
LLM_MAX_CALLS_PER_MINUTE = int(os.getenv("LLM_MAX_CALLS_PER_MINUTE", "10"))
