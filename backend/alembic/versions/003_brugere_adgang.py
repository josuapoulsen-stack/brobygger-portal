"""003 — Brugere, roller og audit-log

Revision ID: 003
Revises: 002
Create Date: 2025-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE bruger_rolle AS ENUM ('brobygger','raadgiver','admin','superadmin');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)

    op.create_table('brugere',
        sa.Column('id',            postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('azure_oid',     sa.Text(), unique=True),
        sa.Column('email',         sa.Text(), unique=True, nullable=False),
        sa.Column('navn',          sa.Text(), nullable=False),
        sa.Column('rolle',         sa.Enum('brobygger','raadgiver','admin','superadmin',
                                           name='bruger_rolle'), nullable=False),
        sa.Column('hq',            sa.Text()),
        sa.Column('aktiv',         sa.Boolean(), server_default='true'),
        sa.Column('sidst_logget_ind', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.execute("""
        CREATE TRIGGER brugere_updated_at BEFORE UPDATE ON brugere
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)

    # Audit-log
    op.create_table('audit_log',
        sa.Column('id',           postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('tabel',        sa.Text(), nullable=False),
        sa.Column('raekke_id',    sa.Text(), nullable=False),
        sa.Column('handling',     sa.Text(), nullable=False),  # INSERT|UPDATE|DELETE
        sa.Column('bruger_id',    postgresql.UUID(as_uuid=True)),
        sa.Column('gamle_data',   postgresql.JSONB()),
        sa.Column('nye_data',     postgresql.JSONB()),
        sa.Column('created_at',   sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_audit_tabel',   'audit_log', ['tabel', 'raekke_id'])
    op.create_index('ix_audit_dato',    'audit_log', ['created_at'])

    # Audit trigger funktion
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_changes()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
        BEGIN
            INSERT INTO audit_log (tabel, raekke_id, handling, gamle_data, nye_data)
            VALUES (
                TG_TABLE_NAME,
                COALESCE(NEW.id::text, OLD.id::text),
                TG_OP,
                CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) END,
                CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) END
            );
            RETURN COALESCE(NEW, OLD);
        END $$;
    """)

    # Audit på mennesker og aftaler
    for tabel in ('mennesker', 'aftaler'):
        op.execute(f"""
            CREATE TRIGGER {tabel}_audit
            AFTER INSERT OR UPDATE OR DELETE ON {tabel}
            FOR EACH ROW EXECUTE FUNCTION audit_changes();
        """)


def downgrade() -> None:
    for tabel in ('mennesker', 'aftaler'):
        op.execute(f"DROP TRIGGER IF EXISTS {tabel}_audit ON {tabel}")
    op.execute("DROP FUNCTION IF EXISTS audit_changes CASCADE")
    op.drop_table('audit_log')
    op.drop_table('brugere')
    op.execute("DROP TYPE IF EXISTS bruger_rolle")
