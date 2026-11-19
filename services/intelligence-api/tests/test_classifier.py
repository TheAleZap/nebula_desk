import pytest

from app import classifier


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("My order arrived broken, I want a refund", "refund"),
        ("I was charged twice on my invoice", "billing"),
        ("Where is my package? No delivery yet", "shipping"),
        ("The app shows an error and crashes", "technical"),
        ("How do I change my password?", "account"),
        ("Thank you, great service!", "feedback"),
        ("Hola, una pregunta", "other"),
    ],
)
def test_intent(text, intent):
    assert classifier.classify_intent(text) == intent


def test_sentiment():
    assert classifier.classify_sentiment("This is unacceptable and terrible") == "negative"
    assert classifier.classify_sentiment("Thanks, perfect!") == "positive"
    assert classifier.classify_sentiment("Where is my parcel") == "neutral"
    assert classifier.classify_sentiment("Thanks but this is terrible") == "neutral"


def test_priority():
    assert classifier.classify_priority("please fix urgently", "billing", "neutral") == "high"
    assert classifier.classify_priority("broken", "refund", "negative") == "high"
    assert classifier.classify_priority("thanks", "feedback", "positive") == "low"
    assert classifier.classify_priority("where is it", "shipping", "neutral") == "normal"


def test_suggest_reply_uses_template():
    assert "refund" in classifier.suggest_reply("refund", "Ana")
    assert classifier.suggest_reply("unknown-intent").startswith("Hi there")


def test_analyze_returns_all_fields():
    result = classifier.analyze("I want my money back, this is unacceptable")
    assert result["intent"] == "refund"
    assert result["priority"] == "high"
    assert result["suggested_reply"]
