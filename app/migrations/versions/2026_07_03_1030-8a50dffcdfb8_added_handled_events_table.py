"""added handled events table

Revision ID: 8a50dffcdfb8
Revises: 8e8c90f1e17e
Create Date: 2026-07-03 10:30:11.128829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8a50dffcdfb8'
down_revision: Union[str, Sequence[str], None] = '8e8c90f1e17e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('handled_events',
    sa.Column('idempotency_key', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_handled_events'))
    )
    op.create_index(op.f('ix_handled_events_idempotency_key'), 'handled_events', ['idempotency_key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_handled_events_idempotency_key'), table_name='handled_events')
    op.drop_table('handled_events')
