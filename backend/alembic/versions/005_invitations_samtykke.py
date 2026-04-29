"""005 — Invitationer og samtykker

Revision ID: 005
Revises: 004
Create Date: 2025-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Invitationer (magic link til brobyggere)
    op.create_table('invitationer',
        sa.Column('id',             postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('email',          sa.Text(), nullable=False),
        sa.Column('navn',           sa.Text()),
        sa.Column('hq',             sa.Text()),
        sa.Column('token_hash',     sa.Text(), nullable=False, unique=True),  # aldrig raw token
        sa.Column('expires_at',     sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('brugt',          sa.Boolean(), server_default='false'),
        sa.Column('brugt_at',       sa.TIMESTAMP(timezone=True)),
        sa.Column('oprettet_af',    postgresql.UUID(as_uuid=True)),
        sa.Column('created_at',     sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_inv_token',   'invitationer', ['token_hash'])
    op.create_index('ix_inv_email',   'invitationer', ['email'])
    op.create_index('ix_inv_expires', 'invitationer', ['expires_at'])

    # Samtykker (Art. 6 + Art. 9 GDPR)
    op.create_table('samtykker',
        sa.Column('id',              postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('bruger_id',       postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version',         sa.Text(), nullable=False),   # f.eks. "2025-v1"
        sa.Column('helbredsdata',    sa.Boolean(), server_default='false'),
        sa.Column('trukket_tilbage', sa.Boolean(), server_default='false'),
        sa.Column('trukket_at',      sa.TIMESTAMP(timezone=True)),
        sa.Column('ip_adresse',      sa.Text()),
        sa.Column('created_at',      sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_samtykke_bruger', 'samtykker', ['bruger_id', 'version'])

    # Audit trigger på samtykker
    op.execute("""
        CREATE TRIGGER samtykker_audit
        AFTER INSERT OR UPDATE OR DELETE ON samtykker
        FOR EACH ROW EXECUTE FUNCTION audit_changes();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS samtykker_audit ON samtykker")
    op.drop_table('samtykker')
    op.drop_table('invitationer')
