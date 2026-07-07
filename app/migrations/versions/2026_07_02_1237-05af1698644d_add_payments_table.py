"""
add payments table

Revision ID: 05af1698644d
Revises:
Create Date: 2026-07-02 12:37:35.910673

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "05af1698644d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("payments",
    sa.Column("idempotency_key", sa.String(), nullable=False),
    sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column("currency", sa.Enum("RUB", "USD", "EUR", name="currencyenum"), nullable=False),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column("metadata_", sa.JSON(), nullable=True),
    sa.Column("webhook_url", sa.String(), nullable=False),
    sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("status", sa.Enum("PENDING", "SUCCEEDED", "FAILED", name="paymentstatusenum"), nullable=False),
    sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
    )
    op.create_index(op.f("ix_payments_idempotency_key"), "payments", ["idempotency_key"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_payments_idempotency_key"), table_name="payments")
    op.drop_table("payments")
