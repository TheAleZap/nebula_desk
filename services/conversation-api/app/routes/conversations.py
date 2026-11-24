import random

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import intelligence_client
from app.db import get_session
from app.models import Agent, Contact, Conversation, Message, utcnow
from app.samples import SAMPLE_MESSAGES
from app.schemas import (
    AnalysisOut,
    ConversationDetail,
    ConversationIn,
    ConversationOut,
    ConversationUpdate,
    MessageIn,
    MessageOut,
    SimulateOut,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])

UNAVAILABLE = (
    "AI analysis is unavailable right now: the Intelligence API did not answer in time. "
    "The inbox keeps working; try again in a moment."
)


def _get(session: Session, conversation_id: int) -> Conversation:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(404, "Conversation not found")
    return conversation


def _add_message(session: Session, conversation: Conversation, body: MessageIn) -> Message:
    message = Message(conversation_id=conversation.id, **body.model_dump())
    session.add(message)
    if body.sender == "agent" and conversation.first_response_at is None:
        conversation.first_response_at = utcnow()
    conversation.updated_at = utcnow()
    return message


def _analyze(session: Session, conversation: Conversation) -> dict:
    """Send the latest customer message across the seam and keep the labels."""
    customer_messages = [m for m in conversation.messages if m.sender == "customer"]
    if not customer_messages:
        raise HTTPException(400, "Conversation has no customer message to analyze")
    latest = customer_messages[-1]
    result = intelligence_client.analyze(latest.id, latest.body)
    conversation.intent = result["intent"]
    conversation.sentiment = result["sentiment"]
    conversation.priority = result["priority"]
    session.commit()
    return {"conversation_id": conversation.id, **result, "message_id": latest.id}


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    status: str | None = None,
    assigned_agent_id: int | None = None,
    q: str | None = None,
    session: Session = Depends(get_session),
):
    query = select(Conversation).order_by(Conversation.updated_at.desc())
    if status:
        query = query.where(Conversation.status == status)
    if assigned_agent_id is not None:
        query = query.where(Conversation.assigned_agent_id == assigned_agent_id)
    if q:
        query = query.where(Conversation.subject.ilike(f"%{q}%"))
    return session.scalars(query).all()


@router.post("", response_model=ConversationDetail, status_code=201)
def create_conversation(body: ConversationIn, session: Session = Depends(get_session)):
    if session.get(Contact, body.contact_id) is None:
        raise HTTPException(400, "contact_id does not exist")
    conversation = Conversation(
        contact_id=body.contact_id, subject=body.subject, channel=body.channel
    )
    session.add(conversation)
    session.flush()
    if body.first_message:
        _add_message(session, conversation, MessageIn(sender="customer", body=body.first_message))
    session.commit()
    session.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, session: Session = Depends(get_session)):
    return _get(session, conversation_id)


@router.put("/{conversation_id}", response_model=ConversationDetail)
def update_conversation(
    conversation_id: int, body: ConversationUpdate, session: Session = Depends(get_session)
):
    conversation = _get(session, conversation_id)
    if body.subject is not None:
        if not body.subject.strip():
            raise HTTPException(422, "subject must not be blank")
        conversation.subject = body.subject.strip()
    if body.status is not None:
        conversation.status = body.status
    if body.unassign:
        conversation.assigned_agent_id = None
    elif body.assigned_agent_id is not None:
        if session.get(Agent, body.assigned_agent_id) is None:
            raise HTTPException(400, "assigned_agent_id does not exist")
        conversation.assigned_agent_id = body.assigned_agent_id
    conversation.updated_at = utcnow()
    session.commit()
    session.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: int, session: Session = Depends(get_session)):
    session.delete(_get(session, conversation_id))
    session.commit()
    return Response(status_code=204)


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
def add_message(conversation_id: int, body: MessageIn, session: Session = Depends(get_session)):
    conversation = _get(session, conversation_id)
    message = _add_message(session, conversation, body)
    session.commit()
    return message


@router.post(
    "/{conversation_id}/analyze",
    response_model=AnalysisOut,
    responses={503: {"description": "Intelligence API unavailable (designed degradation)"}},
)
def analyze_conversation(conversation_id: int, session: Session = Depends(get_session)):
    conversation = _get(session, conversation_id)
    try:
        return _analyze(session, conversation)
    except intelligence_client.IntelligenceUnavailable:
        raise HTTPException(503, UNAVAILABLE) from None


@router.post("/simulate", response_model=SimulateOut, status_code=201)
def simulate_incoming_message(session: Session = Depends(get_session)):
    """Pretend a customer wrote in on chat, email or WhatsApp."""
    sample = random.choice(SAMPLE_MESSAGES)
    contact = session.scalar(select(Contact).where(Contact.email == sample["email"]))
    if contact is None:
        contact = Contact(name=sample["name"], email=sample["email"])
        session.add(contact)
        session.flush()
    conversation = Conversation(
        contact_id=contact.id, subject=sample["subject"], channel=sample["channel"]
    )
    session.add(conversation)
    session.flush()
    _add_message(session, conversation, MessageIn(sender="customer", body=sample["body"]))
    session.commit()
    session.refresh(conversation)
    try:
        _analyze(session, conversation)
        status = "ok"
    except intelligence_client.IntelligenceUnavailable:
        status = "unavailable"
    session.refresh(conversation)
    return {"conversation": conversation, "analysis_status": status}
