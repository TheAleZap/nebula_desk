"""Database engine, sessions, start-up retries and migrations."""

import logging
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app import config

log = logging.getLogger("db")

engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    with SessionLocal() as session:
        yield session


def wait_for_db(max_wait_s: int = config.DB_WAIT_S) -> None:
    """Azure SQL serverless may be paused: retry with backoff until it resumes."""
    delay, waited = 2, 0
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info('{"event": "db_ready", "waited_s": %d}', waited)
            return
        except Exception as exc:  # driver errors differ (40613, 20002...)
            if waited >= max_wait_s:
                raise
            log.warning('{"event": "db_not_ready", "error": "%s"}', type(exc).__name__)
            time.sleep(delay)
            waited += delay
            delay = min(delay * 2, 20)


def run_migrations() -> None:
    """Apply every pending migration in migrations/versions, in order, once."""
    root = Path(__file__).resolve().parent.parent
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", config.DATABASE_URL.replace("%", "%%"))
    command.upgrade(cfg, "head")
    log.info('{"event": "migrations_applied"}')


def db_is_healthy() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
