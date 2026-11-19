"""Rule-based classification and reply templates.

This is the core of the non-CRUD feature. It is deterministic (easy to test),
free, and works without any API key. The optional LLM only rewrites the reply.
"""

import re

INTENT_KEYWORDS = {
    "refund": ["refund", "money back", "return", "reembolso", "damaged", "broken"],
    "billing": ["charged", "invoice", "payment", "bill", "credit card", "price"],
    "shipping": ["package", "delivery", "shipping", "parcel", "tracking", "arrive"],
    "technical": [
        "error",
        "crash",
        "bug",
        "not working",
        "does not work",
        "login",
        "app",
    ],
    "account": ["account", "password", "email address", "username", "profile"],
    "feedback": ["thanks", "thank you", "great", "love", "awesome"],
}
# Checked in this order: the first intent with a matching keyword wins.
INTENT_ORDER = ["refund", "billing", "shipping", "technical", "account", "feedback"]

NEGATIVE = [
    "unacceptable",
    "angry",
    "terrible",
    "awful",
    "worst",
    "broken",
    "disappointed",
    "never",
    "annoying",
]
POSITIVE = ["thanks", "thank you", "great", "love", "perfect", "awesome", "happy"]
URGENT = [
    "urgent",
    "urgently",
    "asap",
    "as soon as possible",
    "immediately",
    "right now",
]

REPLIES = {
    "refund": "Hi {name}, I'm sorry your order didn't arrive in good condition. I've started a refund "
    "request for you; you'll receive a confirmation email within 24 hours.",
    "billing": "Hi {name}, thanks for flagging this. I'm checking the charges on your account now "
    "and will correct any duplicate payment right away.",
    "shipping": "Hi {name}, let me check the tracking for your package. I'll send you the latest "
    "delivery status in a moment.",
    "technical": "Hi {name}, sorry for the trouble. Could you tell me your device and app version? "
    "Meanwhile, updating the app and restarting it usually fixes this.",
    "account": "Hi {name}, you can change this under Settings > Account. If you prefer, I can "
    "update it for you; just confirm the new details.",
    "feedback": "Hi {name}, thank you so much for your kind words! I'll share them with the team.",
    "other": "Hi {name}, thanks for reaching out. Could you give me a bit more detail so I can help?",
}


def _contains(text: str, words: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def classify_intent(text: str) -> str:
    lowered = text.lower()
    for intent in INTENT_ORDER:
        if _contains(lowered, INTENT_KEYWORDS[intent]):
            return intent
    return "other"


def classify_sentiment(text: str) -> str:
    lowered = text.lower()
    negative, positive = _contains(lowered, NEGATIVE), _contains(lowered, POSITIVE)
    if negative and not positive:
        return "negative"
    if positive and not negative:
        return "positive"
    return "neutral"


def classify_priority(text: str, intent: str, sentiment: str) -> str:
    lowered = text.lower()
    if _contains(lowered, URGENT) or (sentiment == "negative" and intent in {"refund", "billing"}):
        return "high"
    if intent == "feedback" or sentiment == "positive":
        return "low"
    return "normal"


def suggest_reply(intent: str, name: str = "there") -> str:
    return REPLIES.get(intent, REPLIES["other"]).format(name=name)


def analyze(text: str) -> dict:
    intent = classify_intent(text)
    sentiment = classify_sentiment(text)
    return {
        "intent": intent,
        "sentiment": sentiment,
        "priority": classify_priority(text, intent, sentiment),
        "suggested_reply": suggest_reply(intent),
    }
