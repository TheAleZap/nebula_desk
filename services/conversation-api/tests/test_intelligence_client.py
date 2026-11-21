"""Cross-seam contract test: the Intelligence API is replaced by a stub over HTTP."""

import httpx
import pytest

from app import intelligence_client


def test_client_posts_message_and_returns_json(monkeypatch):
    seen = {}

    def fake_post(url, json, timeout):
        seen.update(url=url, json=json, timeout=timeout)
        return httpx.Response(200, json={"intent": "shipping"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    assert intelligence_client.analyze(7, "where is my parcel")["intent"] == "shipping"
    assert seen["url"].endswith("/analyze")
    assert seen["json"] == {"message_id": 7, "text": "where is my parcel"}
    assert seen["timeout"] > 0


def test_client_raises_on_timeout(monkeypatch):
    def timeout(url, json, timeout):
        raise httpx.ConnectTimeout("too slow")

    monkeypatch.setattr(httpx, "post", timeout)
    with pytest.raises(intelligence_client.IntelligenceUnavailable):
        intelligence_client.analyze(1, "hello")


def test_client_raises_on_server_error(monkeypatch):
    def error(url, json, timeout):
        return httpx.Response(500, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", error)
    with pytest.raises(intelligence_client.IntelligenceUnavailable):
        intelligence_client.analyze(1, "hello")
