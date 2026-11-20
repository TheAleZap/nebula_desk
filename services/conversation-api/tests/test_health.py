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


def test_migrations_seed_agents_once(client):
    agents = client.get("/agents").json()
    assert [a["name"] for a in agents][:1] == ["Demo Agent"]
    assert len(agents) == 3


def test_request_is_logged(client, caplog):
    caplog.set_level("INFO", logger="request")
    client.get("/health")
    line = [r.getMessage() for r in caplog.records if r.name == "request"][-1]
    assert '"method": "GET"' in line and '"path": "/health"' in line and "duration_ms" in line
