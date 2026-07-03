"""add outbox outbox messages table

Revision ID: 8e8c90f1e17e
Revises: 05af1698644d
Create Date: 2026-07-03 08:53:10.409282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8e8c90f1e17e'
down_revision: Union[str, Sequence[str], None] = '05af1698644d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('outbox_messages',
    sa.Column('idempotency_key', sa.String(), nullable=False),
    sa.Column('queue', sa.String(length=255), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('handled_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outbox_messages'))
    )
    op.create_index(op.f('ix_outbox_messages_idempotency_key'), 'outbox_messages', ['idempotency_key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_outbox_messages_idempotency_key'), table_name='outbox_messages')
    op.drop_table('outbox_messages')
