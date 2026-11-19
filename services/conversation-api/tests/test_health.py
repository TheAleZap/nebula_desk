def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["db"] == "ok"


def test_health_reports_503_when_db_down(client, monkeypatch):
    monkeypatch.setattr("app.main.db_is_healthy", lambda: False)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["db"] == "down"


def test_request_is_logged(client, caplog):
    caplog.set_level("INFO", logger="request")
    client.get("/health")
    line = [r.getMessage() for r in caplog.records if r.name == "request"][-1]
    assert '"method": "GET"' in line and '"path": "/health"' in line and "duration_ms" in line


def test_migrations_created_tables_and_seeded_agents(client):
    from sqlalchemy import inspect, text

    from app.db import engine

    tables = set(inspect(engine).get_table_names())
    assert {"agents", "contacts", "conversations", "messages", "schema_migrations"} <= tables
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM agents")).scalar() == 3
