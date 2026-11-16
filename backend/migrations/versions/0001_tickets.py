"""Create ticket and audit event tables.

Revision ID: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('tickets',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(180), nullable=False), sa.Column('description', sa.Text(), nullable=False),
        sa.Column('customer_name', sa.String(100), nullable=False), sa.Column('customer_email', sa.String(254), nullable=False),
        sa.Column('status', sa.String(20), nullable=False), sa.Column('category', sa.String(20)),
        sa.Column('priority', sa.String(20)), sa.Column('sentiment', sa.String(20)),
        sa.Column('analysis', sa.JSON()), sa.Column('suggested_reply', sa.Text()), sa.Column('reply_model', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False), sa.Column('resolved_at', sa.DateTime(timezone=True)))
    for field in ['status', 'category', 'priority', 'created_at']:
        op.create_index(f'ix_tickets_{field}', 'tickets', [field])
    op.create_index('ix_ticket_queue', 'tickets', ['status', 'priority', 'created_at'])
    op.create_table('ticket_events', sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ticket_id', sa.Integer(), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(80), nullable=False), sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_ticket_events_ticket_id', 'ticket_events', ['ticket_id'])


def downgrade() -> None:
    op.drop_table('ticket_events')
    op.drop_table('tickets')
