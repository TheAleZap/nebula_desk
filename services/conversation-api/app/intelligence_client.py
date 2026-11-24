"""The only call across the seam: Conversation API -> Intelligence API.

Every call has a timeout. If the Intelligence API is down, slow, or answers
with an error, we raise IntelligenceUnavailable and the caller degrades.
"""

import httpx

from app import config


class IntelligenceUnavailable(Exception):
    pass


def analyze(message_id: int, text: str) -> dict:
    try:
        response = httpx.post(
            f"{config.INTELLIGENCE_URL}/analyze",
            json={"message_id": message_id, "text": text},
            timeout=config.INTELLIGENCE_TIMEOUT_S,
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise IntelligenceUnavailable(type(exc).__name__) from exc
