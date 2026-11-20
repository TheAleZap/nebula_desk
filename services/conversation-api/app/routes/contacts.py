from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Contact, Conversation
from app.schemas import ContactIn, ContactOut

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _get(session: Session, contact_id: int) -> Contact:
    contact = session.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(404, "Contact not found")
    return contact


@router.get("", response_model=list[ContactOut])
def list_contacts(session: Session = Depends(get_session)):
    return session.scalars(select(Contact).order_by(Contact.name)).all()


@router.post("", response_model=ContactOut, status_code=201)
def create_contact(body: ContactIn, session: Session = Depends(get_session)):
    contact = Contact(**body.model_dump())
    session.add(contact)
    session.commit()
    return contact


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, session: Session = Depends(get_session)):
    return _get(session, contact_id)


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, body: ContactIn, session: Session = Depends(get_session)):
    contact = _get(session, contact_id)
    contact.name, contact.email = body.name, body.email
    session.commit()
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    contact = _get(session, contact_id)
    in_use = session.scalar(select(Conversation.id).where(Conversation.contact_id == contact_id))
    if in_use is not None:
        raise HTTPException(409, "Contact has conversations; delete them first")
    session.delete(contact)
    session.commit()
    return Response(status_code=204)
