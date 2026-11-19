"""Initial schema: analyses (results of classification + suggested reply).

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("message_id", sa.Integer, nullable=False),
        sa.Column("text_hash", sa.String(64), nullable=False),
        sa.Column("intent", sa.String(30), nullable=False),
        sa.Column("sentiment", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("suggested_reply", sa.Unicode(2000), nullable=False),
        sa.Column("source", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_analyses_text_hash", "analyses", ["text_hash"])
