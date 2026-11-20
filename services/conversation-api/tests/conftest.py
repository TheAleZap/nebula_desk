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


@pytest.fixture
def contact(client):
    response = client.post("/contacts", json={"name": "Ana Test", "email": "ana@example.com"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def conversation(client, contact):
    response = client.post(
        "/conversations",
        json={
            "contact_id": contact["id"],
            "subject": "Refund please",
            "channel": "email",
            "first_message": "My order arrived broken, I want a refund",
        },
    )
    assert response.status_code == 201
    return response.json()
