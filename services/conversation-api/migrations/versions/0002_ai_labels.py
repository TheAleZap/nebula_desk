"""Add AI labels to conversations, keeping existing rows (defaults backfill them).

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    with op.batch_alter_table("conversations") as batch:
        batch.add_column(
            sa.Column("intent", sa.String(30), nullable=False, server_default="unknown")
        )
        batch.add_column(
            sa.Column("sentiment", sa.String(20), nullable=False, server_default="neutral")
        )
        batch.add_column(
            sa.Column("priority", sa.String(20), nullable=False, server_default="normal")
        )
