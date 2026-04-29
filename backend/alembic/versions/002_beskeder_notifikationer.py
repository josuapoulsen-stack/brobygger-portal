"""002 — Beskeder, notifikationer, push-subscriptions

Revision ID: 002
Revises: 001
Create Date: 2025-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # besked_traade
    op.create_table('besked_traade',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('titel',       sa.Text()),
        sa.Column('hq',          sa.Text()),
        sa.Column('oprettet_af', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )

    # besked_deltagere
    op.create_table('besked_deltagere',
        sa.Column('traad_id',    postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('besked_traade.id', ondelete='CASCADE')),
        sa.Column('bruger_id',   postgresql.UUID(as_uuid=True)),
        sa.Column('rolle',       sa.Text()),  # 'brobygger' | 'raadgiver' | 'admin'
        sa.Column('joined_at',   sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )

    # beskeder
    op.create_table('beskeder',
        sa.Column('id',               postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('traad_id',         postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('besked_traade.id', ondelete='CASCADE'), nullable=False),
        sa.Column('afsender_id',      postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('indhold',          sa.Text(), nullable=False),
        sa.Column('signalr_sequence', sa.BigInteger()),
        sa.Column('created_at',       sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_beskeder_traad', 'beskeder', ['traad_id', 'created_at'])

    # notifikationer
    op.create_table('notifikationer',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('bruger_id',   postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type',        sa.Text(), nullable=False),  # 'match'|'reminder'|'message'
        sa.Column('titel',       sa.Text(), nullable=False),
        sa.Column('indhold',     sa.Text()),
        sa.Column('url',         sa.Text()),
        sa.Column('laest',       sa.Boolean(), server_default='false'),
        sa.Column('push_sendt',  sa.Boolean(), server_default='false'),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_notif_bruger', 'notifikationer', ['bruger_id', 'laest'])

    # push_subscriptions
    op.create_table('push_subscriptions',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('bruger_id',   postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('endpoint',    sa.Text(), nullable=False, unique=True),
        sa.Column('p256dh',      sa.Text()),
        sa.Column('auth',        sa.Text()),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_push_bruger', 'push_subscriptions', ['bruger_id'])


def downgrade() -> None:
    op.drop_table('push_subscriptions')
    op.drop_table('notifikationer')
    op.drop_table('beskeder')
    op.drop_table('besked_deltagere')
    op.drop_table('besked_traade')
