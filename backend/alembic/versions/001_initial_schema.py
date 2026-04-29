"""001 — Initialt skema: brobyggere, mennesker, aftaler

Revision ID: 001
Revises:
Create Date: 2025-06-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ENUMs
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE brobygger_status AS ENUM ('ny','aktiv','pause','inaktiv','afventer');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE brobygning_type AS ENUM ('sundhed','forening','social');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE aftale_status AS ENUM ('foreslaaet','bekraeftet','gennemfoert','aflyst','afventer');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE kon AS ENUM ('mand','kvinde','andet','uoplyst');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
    """)

    # set_updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END $$;
    """)

    # brobyggere
    op.create_table('brobyggere',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('azure_oid',   sa.Text(), unique=True),
        sa.Column('navn',        sa.Text(), nullable=False),
        sa.Column('email',       sa.Text(), unique=True),
        sa.Column('mobil',       sa.Text()),
        sa.Column('hq',          sa.Text(), nullable=False),
        sa.Column('typer',       postgresql.ARRAY(sa.Text())),
        sa.Column('sprog',       postgresql.ARRAY(sa.Text())),
        sa.Column('open_shifts', sa.Integer(), server_default='0'),
        sa.Column('status',      sa.Enum('ny','aktiv','pause','inaktiv','afventer',
                                         name='brobygger_status'), server_default='ny'),
        sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.execute("""
        CREATE TRIGGER brobyggere_updated_at BEFORE UPDATE ON brobyggere
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)

    # mennesker
    op.create_table('mennesker',
        sa.Column('id',                postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('fornavn',           sa.Text(), nullable=False),
        sa.Column('efternavn',         sa.Text()),
        sa.Column('cpr_hash',          sa.Text()),
        sa.Column('kon',               sa.Enum('mand','kvinde','andet','uoplyst', name='kon')),
        sa.Column('foedselsdato',      sa.Date()),
        sa.Column('telefon',           sa.Text()),
        sa.Column('email',             sa.Text()),
        sa.Column('adresse',           sa.Text()),
        sa.Column('postnummer',        sa.Text()),
        sa.Column('by',                sa.Text()),
        sa.Column('hq',                sa.Text(), nullable=False),
        sa.Column('type',              sa.Enum('sundhed','forening','social', name='brobygning_type')),
        sa.Column('sprog',             postgresql.ARRAY(sa.Text())),
        sa.Column('noter',             sa.Text()),
        sa.Column('helbredsnoter_enc', postgresql.BYTEA()),
        sa.Column('deleted_at',        sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at',        sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at',        sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.execute("""
        CREATE TRIGGER mennesker_updated_at BEFORE UPDATE ON mennesker
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)

    # aftaler
    op.create_table('aftaler',
        sa.Column('id',           postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('brobygger_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('brobyggere.id', ondelete='SET NULL')),
        sa.Column('menneske_id',  postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('mennesker.id',  ondelete='CASCADE'), nullable=False),
        sa.Column('dato',         sa.Date(), nullable=False),
        sa.Column('start_tid',    sa.Text()),
        sa.Column('slut_tid',     sa.Text()),
        sa.Column('aktivitet',    sa.Text()),
        sa.Column('sted',         sa.Text()),
        sa.Column('status',       sa.Enum('foreslaaet','bekraeftet','gennemfoert','aflyst','afventer',
                                          name='aftale_status'), server_default='foreslaaet'),
        sa.Column('noter',        sa.Text()),
        sa.Column('created_at',   sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at',   sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.execute("""
        CREATE TRIGGER aftaler_updated_at BEFORE UPDATE ON aftaler
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)
    op.create_index('ix_aftaler_dato', 'aftaler', ['dato'])
    op.create_index('ix_aftaler_brobygger', 'aftaler', ['brobygger_id'])
    op.create_index('ix_aftaler_menneske',  'aftaler', ['menneske_id'])


def downgrade() -> None:
    op.drop_table('aftaler')
    op.drop_table('mennesker')
    op.drop_table('brobyggere')
    op.execute("DROP FUNCTION IF EXISTS set_updated_at CASCADE")
    op.execute("DROP TYPE IF EXISTS aftale_status")
    op.execute("DROP TYPE IF EXISTS brobygning_type")
    op.execute("DROP TYPE IF EXISTS brobygger_status")
    op.execute("DROP TYPE IF EXISTS kon")
