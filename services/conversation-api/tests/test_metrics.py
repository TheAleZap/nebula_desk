from datetime import datetime, timedelta

from app import metrics


def test_average_first_response_minutes():
    t0 = datetime(2026, 11, 20, 10, 0)
    pairs = [(t0, t0 + timedelta(minutes=10)), (t0, t0 + timedelta(minutes=20)), (t0, None)]
    assert metrics.average_first_response_minutes(pairs) == 15.0
    assert metrics.average_first_response_minutes([(t0, None)]) is None


def test_acceptance_rate():
    assert metrics.acceptance_rate(0, 0) is None
    assert metrics.acceptance_rate(4, 1) == 0.25


def test_count_by_keeps_known_keys():
    assert metrics.count_by(["open", "open", "x"], ["open", "resolved"]) == {
        "open": 2,
        "resolved": 0,
        "x": 1,
    }


def test_metrics_endpoint(client, conversation):
    client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"sender": "agent", "body": "On it", "from_suggestion": True},
    )
    data = client.get("/metrics").json()
    assert data["total_conversations"] >= 1
    assert data["by_status"]["open"] >= 1
    assert data["replies_from_ai_suggestion"] >= 1
    assert 0 < data["ai_suggestion_acceptance_rate"] <= 1
