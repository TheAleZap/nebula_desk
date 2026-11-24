from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import metrics
from app.db import get_session
from app.models import Conversation, Message

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def support_metrics(session: Session = Depends(get_session)):
    rows = session.execute(
        select(
            Conversation.status,
            Conversation.priority,
            Conversation.created_at,
            Conversation.first_response_at,
        )
    ).all()
    agent_messages = session.scalar(select(func.count(Message.id)).where(Message.sender == "agent"))
    accepted = session.scalar(
        select(func.count(Message.id)).where(Message.sender == "agent", Message.from_suggestion)
    )
    return {
        "total_conversations": len(rows),
        "by_status": metrics.count_by([r.status for r in rows], ["open", "pending", "resolved"]),
        "by_priority": metrics.count_by([r.priority for r in rows], ["high", "normal", "low"]),
        "avg_first_response_minutes": metrics.average_first_response_minutes(
            [(r.created_at, r.first_response_at) for r in rows]
        ),
        "agent_replies": agent_messages,
        "replies_from_ai_suggestion": accepted,
        "ai_suggestion_acceptance_rate": metrics.acceptance_rate(agent_messages, accepted),
    }
