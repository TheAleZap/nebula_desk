"""Tests run against a throw-away SQLite file with the real migrations applied.

CI also starts the full stack on SQL Server (docker compose) to catch dialect issues.
"""

import os
import tempfile

import pytest

_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file}"
os.environ["RUN_MIGRATIONS"] = "1"
os.environ["INTELLIGENCE_URL"] = "http://intelligence.test"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:  # "with" runs start-up: migrations
        yield test_client
