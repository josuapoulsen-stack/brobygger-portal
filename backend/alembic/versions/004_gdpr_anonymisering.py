"""004 — GDPR: anonymisering, audit-cleanup og Row-Level Security

Revision ID: 004
Revises: 003
Create Date: 2025-06-01
"""

from alembic import op

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Anonymisér slettede mennesker efter 30 dage
    op.execute("""
        CREATE OR REPLACE FUNCTION anonymiser_slettede_mennesker()
        RETURNS INT LANGUAGE plpgsql AS $$
        DECLARE aff INT;
        BEGIN
            UPDATE mennesker SET
                fornavn           = 'Anonymiseret',
                efternavn         = NULL,
                cpr_hash          = NULL,
                telefon           = NULL,
                email             = NULL,
                adresse           = NULL,
                postnummer        = NULL,
                by                = NULL,
                noter             = NULL,
                helbredsnoter_enc = NULL
            WHERE deleted_at IS NOT NULL
              AND deleted_at < NOW() - INTERVAL '30 days'
              AND fornavn != 'Anonymiseret';
            GET DIAGNOSTICS aff = ROW_COUNT;
            RETURN aff;
        END $$;
    """)

    # Ryd audit-log ældre end 5 år
    op.execute("""
        CREATE OR REPLACE FUNCTION ryd_gammel_audit()
        RETURNS INT LANGUAGE plpgsql AS $$
        DECLARE aff INT;
        BEGIN
            DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '5 years';
            GET DIAGNOSTICS aff = ROW_COUNT;
            RETURN aff;
        END $$;
    """)

    # Row-Level Security
    op.execute("ALTER TABLE aftaler   ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE mennesker ENABLE ROW LEVEL SECURITY")

    # Superbruger-policy (bypass for service-account)
    op.execute("""
        CREATE POLICY aftaler_service ON aftaler
        USING (current_user = 'bbadmin');
    """)
    op.execute("""
        CREATE POLICY mennesker_service ON mennesker
        USING (current_user = 'bbadmin');
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS aftaler_service   ON aftaler")
    op.execute("DROP POLICY IF EXISTS mennesker_service ON mennesker")
    op.execute("ALTER TABLE aftaler   DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE mennesker DISABLE ROW LEVEL SECURITY")
    op.execute("DROP FUNCTION IF EXISTS ryd_gammel_audit")
    op.execute("DROP FUNCTION IF EXISTS anonymiser_slettede_mennesker")
