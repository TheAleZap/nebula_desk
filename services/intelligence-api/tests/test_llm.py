import httpx

from app import config, llm


def test_rate_limiter_blocks_after_max_calls():
    limiter = llm.RateLimiter(max_calls=2, per_seconds=60)
    assert limiter.allow() and limiter.allow()
    assert limiter.allow() is False


def test_disabled_without_key(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", "")
    assert llm.is_enabled() is False
    assert llm.rewrite_reply("hi", "other", "draft") is None


def test_rewrite_reply_success_and_failure(monkeypatch):
    monkeypatch.setattr(config, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(llm, "limiter", llm.RateLimiter(5))

    def ok(url, headers, json, timeout):
        body = {"choices": [{"message": {"content": " Better reply "}}]}
        return httpx.Response(200, json=body, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", ok)
    assert llm.rewrite_reply("hi", "other", "draft") == "Better reply"

    def fail(url, headers, json, timeout):
        raise httpx.ReadTimeout("slow")

    monkeypatch.setattr(httpx, "post", fail)
    assert llm.rewrite_reply("hi", "other", "draft") is None
