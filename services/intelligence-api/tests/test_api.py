from app import llm


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_health_503_when_db_down(client, monkeypatch):
    monkeypatch.setattr("app.main.db_is_healthy", lambda: False)
    assert client.get("/health").status_code == 503


def test_analyze_and_cache(client):
    first = client.post("/analyze", json={"message_id": 1, "text": "Where is my package?"})
    assert first.status_code == 200
    assert first.json()["intent"] == "shipping"
    assert first.json()["cached"] is False
    assert first.json()["source"] == "rules"

    again = client.post("/analyze", json={"message_id": 2, "text": "  where is my PACKAGE?"})
    assert again.json()["cached"] is True
    assert again.json()["message_id"] == 2


def test_analyze_validation(client):
    assert client.post("/analyze", json={"message_id": 1, "text": ""}).status_code == 422


def test_llm_reply_is_used_when_available(client, monkeypatch):
    monkeypatch.setattr(llm, "rewrite_reply", lambda text, intent, draft: "LLM reply")
    response = client.post("/analyze", json={"message_id": 3, "text": "App error on login"})
    assert response.json()["suggested_reply"] == "LLM reply"
    assert response.json()["source"] == "llm"


def test_recent_and_stats(client):
    client.post("/analyze", json={"message_id": 4, "text": "Thank you so much"})
    assert len(client.get("/analyses", params={"limit": 2}).json()) == 2
    stats = client.get("/stats").json()
    assert stats["total_analyses"] >= 1
    assert "feedback" in stats["by_intent"]
    assert stats["llm_enabled"] is False
