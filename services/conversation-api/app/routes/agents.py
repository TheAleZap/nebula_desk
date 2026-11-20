from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Agent
from app.schemas import AgentOut

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentOut])
def list_agents(session: Session = Depends(get_session)):
    """Agents are seeded by migration 0001 (demo users, no authentication)."""
    return session.scalars(select(Agent).order_by(Agent.id)).all()
