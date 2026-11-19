"""Configuration, read only from environment variables (nothing hard-coded)."""

import os


def _list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
INTELLIGENCE_URL = os.getenv("INTELLIGENCE_URL", "http://localhost:8002").rstrip("/")
INTELLIGENCE_TIMEOUT_S = float(os.getenv("INTELLIGENCE_TIMEOUT_S", "3"))
CORS_ORIGINS = _list(os.getenv("CORS_ORIGINS", "http://localhost:5173"))
APP_VERSION = os.getenv("APP_VERSION", "dev")
RUN_MIGRATIONS = os.getenv("RUN_MIGRATIONS", "1") == "1"
DB_WAIT_S = int(os.getenv("DB_WAIT_S", "180"))
