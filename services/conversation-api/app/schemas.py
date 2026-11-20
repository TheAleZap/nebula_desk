"""Request and response shapes (they also become the OpenAPI document)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Channel = Literal["chat", "email", "whatsapp"]
Status = Literal["open", "pending", "resolved"]
Sender = Literal["customer", "agent"]


def _not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must not be blank")
    return value


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class ContactIn(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=200, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    _name = field_validator("name")(_not_blank)


class ContactOut(ContactIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class MessageIn(BaseModel):
    sender: Sender
    body: str = Field(max_length=4000)
    from_suggestion: bool = False

    _body = field_validator("body")(_not_blank)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conversation_id: int
    sender: Sender
    body: str
    from_suggestion: bool
    created_at: datetime


class ConversationIn(BaseModel):
    contact_id: int
    subject: str = Field(max_length=200)
    channel: Channel = "chat"
    first_message: str | None = Field(default=None, max_length=4000)

    _subject = field_validator("subject")(_not_blank)


class ConversationUpdate(BaseModel):
    subject: str | None = Field(default=None, max_length=200)
    status: Status | None = None
    assigned_agent_id: int | None = None
    unassign: bool = False


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contact_id: int
    subject: str
    channel: Channel
    status: Status
    assigned_agent_id: int | None
    created_at: datetime
    updated_at: datetime
    first_response_at: datetime | None
    contact: ContactOut
    agent: AgentOut | None = None


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class SimulateOut(BaseModel):
    conversation: ConversationOut
