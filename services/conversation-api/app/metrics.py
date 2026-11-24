"""Support metrics for the dashboard page. Pure functions, easy to unit test."""

from collections import Counter


def average_first_response_minutes(pairs: list[tuple]) -> float | None:
    """pairs = [(created_at, first_response_at), ...]; ignores unanswered ones."""
    durations = [
        (answered - created).total_seconds() / 60 for created, answered in pairs if answered
    ]
    if not durations:
        return None
    return round(sum(durations) / len(durations), 1)


def acceptance_rate(agent_messages: int, from_suggestion: int) -> float | None:
    if agent_messages == 0:
        return None
    return round(from_suggestion / agent_messages, 3)


def count_by(values: list[str], keys: list[str]) -> dict[str, int]:
    counts = Counter(values)
    return {key: counts.get(key, 0) for key in keys} | {
        k: v for k, v in counts.items() if k not in keys
    }
