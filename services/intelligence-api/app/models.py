"""Tables owned by the Intelligence API. They must match the migrations."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Plain ID of a message in the Conversation API: no foreign key across the seam.
    message_id: Mapped[int] = mapped_column(Integer)
    text_hash: Mapped[str] = mapped_column(String(64), index=True)
    intent: Mapped[str] = mapped_column(String(30))
    sentiment: Mapped[str] = mapped_column(String(20))
    priority: Mapped[str] = mapped_column(String(20))
    suggested_reply: Mapped[str] = mapped_column(Unicode(2000))
    source: Mapped[str] = mapped_column(String(10))  # "rules" or "llm"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
