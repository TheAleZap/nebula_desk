"""Optional LLM rewrite of the suggested reply, with a rate limit and a timeout.

Cost control: (1) off unless LLM_API_KEY is set, (2) results are cached in the
database by text hash (see routes), (3) at most LLM_MAX_CALLS_PER_MINUTE calls.
Any failure returns None and the rule-based reply is used instead.
"""

import threading
import time

import httpx

from app import config


class RateLimiter:
    def __init__(self, max_calls: int, per_seconds: float = 60.0):
        self.max_calls, self.per_seconds = max_calls, per_seconds
        self._calls: list[float] = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self._lock:
            self._calls = [t for t in self._calls if now - t < self.per_seconds]
            if len(self._calls) >= self.max_calls:
                return False
            self._calls.append(now)
            return True


limiter = RateLimiter(config.LLM_MAX_CALLS_PER_MINUTE)


def is_enabled() -> bool:
    return bool(config.LLM_API_KEY)


def rewrite_reply(customer_text: str, intent: str, draft: str) -> str | None:
    if not is_enabled() or not limiter.allow():
        return None
    prompt = (
        "You are a friendly customer-support agent. Rewrite the draft reply so it answers "
        f"the customer's message. Intent: {intent}. Keep it under 60 words.\n\n"
        f"Customer: {customer_text}\nDraft: {draft}"
    )
    try:
        response = httpx.post(
            f"{config.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
            json={
                "model": config.LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120,
                "temperature": 0.3,
            },
            timeout=config.LLM_TIMEOUT_S,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return None
