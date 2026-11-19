"""Initial schema: agents (seeded), contacts, conversations, messages.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    agents = op.create_table(
        "agents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
    )
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contact_id", sa.Integer, sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("subject", sa.Unicode(200), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("assigned_agent_id", sa.Integer, sa.ForeignKey("agents.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("first_response_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender", sa.String(20), nullable=False),
        sa.Column("body", sa.Unicode(4000), nullable=False),
        sa.Column("from_suggestion", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    # Seed data travels with its table and runs exactly once (demo agents, no auth).
    op.bulk_insert(
        agents,
        [
            {"name": "Demo Agent", "email": "demo.agent@nebula.test"},
            {"name": "Alex Support", "email": "alex.support@nebula.test"},
            {"name": "Sam Support", "email": "sam.support@nebula.test"},
        ],
    )
