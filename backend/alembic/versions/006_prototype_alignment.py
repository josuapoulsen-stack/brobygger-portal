"""006 — Prototype-alignment (henvendelser, UCLA-3, udlæg, opkald, skabeloner, stamdata)

Bringer backend-schemaet på højde med prototypen (se DATAMODEL_GAP.md).
Tilføjer nye tabeller + manglende kolonner på mennesker/aftaler/brobyggere
+ afstemmer aftale_status-ENUM.

Revision ID: 006
Revises: 005
Create Date: 2026-06-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Nye ENUM-typer ────────────────────────────────────────────────────────
    ucla_slags = postgresql.ENUM('baseline', 'opfoelgning', name='ucla_slags')
    ucla_slags.create(op.get_bind(), checkfirst=True)
    opkald_type = postgresql.ENUM('samtale_menneske', 'samtale_brobygger', 'ringeopgave', name='opkald_type')
    opkald_type.create(op.get_bind(), checkfirst=True)

    # ── Afstem aftale_status med prototypens taksonomi (additivt) ─────────────
    for val in ('kladde', 'pending', 'confirmed', 'afslaaet', 'brudt'):
        op.execute(f"ALTER TYPE aftale_status ADD VALUE IF NOT EXISTS '{val}'")

    # ── stamdata (admin-redigerbart reference-data — erstatter SoS_REFS) ───────
    op.create_table('stamdata',
        sa.Column('id',         postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('kategori',   sa.Text(), nullable=False),   # hovedsaeder|afdelinger|aftaletyper|henvendere|modtagere|transportplaner|aflysningsaarsager|aflystAf|finansieringskilder|samarbejdspartnere|brobygningstyper
        sa.Column('navn',       sa.Text(), nullable=False),
        sa.Column('hovedsaede', sa.Text()),                   # hq-specifik (afdelinger, samarbejdspartnere); NULL/'Alle hovedsæder' = landsdækkende
        sa.Column('farve',      sa.Text()),                   # stamdata-farve pr. post
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('aktiv',      sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_stamdata_kategori', 'stamdata', ['kategori'])

    # ── henvendelser (flere pr. menneske; tidligste = førstegangshenvender) ────
    op.create_table('henvendelser',
        sa.Column('id',            postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('menneske_id',   postgresql.UUID(as_uuid=True), sa.ForeignKey('mennesker.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type',          sa.Text(), nullable=False),   # 'Personen selv' | 'Kommune' | 'Pårørende' | ...
        sa.Column('navn',          sa.Text()),
        sa.Column('dato',          sa.Date(), nullable=False),
        sa.Column('note',          sa.Text()),
        sa.Column('oprettet_af_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brugere.id')),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_henvendelser_menneske', 'henvendelser', ['menneske_id', 'dato'])

    # ── ucla_maalinger (UCLA-3 baseline + opfølgninger) ────────────────────────
    op.create_table('ucla_maalinger',
        sa.Column('id',            postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('menneske_id',   postgresql.UUID(as_uuid=True), sa.ForeignKey('mennesker.id', ondelete='CASCADE'), nullable=False),
        sa.Column('slags',         postgresql.ENUM('baseline', 'opfoelgning', name='ucla_slags', create_type=False), nullable=False),
        sa.Column('q1',            sa.SmallInteger()),
        sa.Column('q2',            sa.SmallInteger()),
        sa.Column('q3',            sa.SmallInteger()),
        sa.Column('sum',           sa.SmallInteger(), nullable=False),   # 3–9
        sa.Column('dato',          sa.Date(), nullable=False),
        sa.Column('label',         sa.Text()),
        sa.Column('oprettet_af_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brugere.id')),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_ucla_menneske', 'ucla_maalinger', ['menneske_id', 'dato'])

    # ── udlaeg_konti (bankoplysninger — kontonr KRYPTERET) ─────────────────────
    op.create_table('udlaeg_konti',
        sa.Column('id',           postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('brobygger_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brobyggere.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('navn',         sa.Text(), nullable=False),
        sa.Column('email',        sa.Text()),
        sa.Column('reg_nr',       sa.Text(), nullable=False),
        sa.Column('konto_nr_enc', postgresql.BYTEA(), nullable=False),   # pgp_sym_encrypt — som helbredsnoter
        sa.Column('aar',          sa.SmallInteger(), nullable=False),    # kreditorgruppe = år − 2020
        sa.Column('kreditor_nr',  sa.Text()),                            # tildeles ved eksport
        sa.Column('indsendt_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )

    # ── opkald_log (typed; koblet til menneske ELLER brobygger) ────────────────
    op.create_table('opkald_log',
        sa.Column('id',            postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('type',          postgresql.ENUM('samtale_menneske', 'samtale_brobygger', 'ringeopgave', name='opkald_type', create_type=False), nullable=False),
        sa.Column('under_type',    sa.Text()),   # ringeopgave: bestil_tid|forny_recept|kontakt_forening|andet
        sa.Column('menneske_id',   postgresql.UUID(as_uuid=True), sa.ForeignKey('mennesker.id', ondelete='SET NULL')),
        sa.Column('brobygger_id',  postgresql.UUID(as_uuid=True), sa.ForeignKey('brobyggere.id', ondelete='SET NULL')),
        sa.Column('tlf',           sa.Text()),
        sa.Column('note',          sa.Text(), nullable=False),
        sa.Column('dato',          sa.Date(), nullable=False),
        sa.Column('tid',           sa.Text()),
        sa.Column('oprettet_af_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brugere.id')),
        sa.Column('created_at',    sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.CheckConstraint('menneske_id IS NOT NULL OR brobygger_id IS NOT NULL', name='opkald_skal_kobles'),
    )
    op.create_index('ix_opkald_menneske', 'opkald_log', ['menneske_id'])
    op.create_index('ix_opkald_brobygger', 'opkald_log', ['brobygger_id'])

    # ── besked_skabeloner (pr. rådgiver; flettefelter i tekst) ─────────────────
    op.create_table('besked_skabeloner',
        sa.Column('id',         postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('ejer_id',    postgresql.UUID(as_uuid=True), sa.ForeignKey('brugere.id', ondelete='CASCADE'), nullable=False),
        sa.Column('navn',       sa.Text(), nullable=False),
        sa.Column('indsats',    sa.Text(), server_default='alle'),   # alle|social|forening|sundhed
        sa.Column('tekst',      sa.Text(), nullable=False),
        sa.Column('er_standard', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_skabelon_ejer', 'besked_skabeloner', ['ejer_id'])

    # ── kontaktpersoner (pårørende/instans pr. menneske) ───────────────────────
    op.create_table('kontaktpersoner',
        sa.Column('id',          postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('menneske_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mennesker.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rolle',       sa.Text()),
        sa.Column('navn',        sa.Text()),
        sa.Column('tlf',         sa.Text()),
    )
    op.create_index('ix_kontaktperson_menneske', 'kontaktpersoner', ['menneske_id'])

    # ── mennesker: manglende kolonner ─────────────────────────────────────────
    op.add_column('mennesker', sa.Column('afdeling',           sa.Text()))
    op.add_column('mennesker', sa.Column('kilde',              sa.Text()))
    op.add_column('mennesker', sa.Column('meetpoint',          sa.Text()))
    op.add_column('mennesker', sa.Column('sroi_maalgruppe',    sa.Text()))
    op.add_column('mennesker', sa.Column('helbreds_kategorier', postgresql.ARRAY(sa.Text())))
    op.add_column('mennesker', sa.Column('praeferencer',       postgresql.JSONB()))
    op.add_column('mennesker', sa.Column('afslut_trivsel',     sa.SmallInteger()))
    op.add_column('mennesker', sa.Column('afslut_aarsag',      sa.Text()))
    op.add_column('mennesker', sa.Column('ucla_fravalgt',      sa.Boolean(), server_default='false'))
    op.add_column('mennesker', sa.Column('telefon_norm',       sa.Text()))   # kanonisk (sidste 8 cifre) til genkendelse
    op.create_index('ix_mennesker_telefon_norm', 'mennesker', ['telefon_norm'])

    # ── brobyggere: manglende kolonner ────────────────────────────────────────
    op.add_column('brobyggere', sa.Column('afdeling',     sa.Text()))
    op.add_column('brobyggere', sa.Column('telefon_norm', sa.Text()))
    op.create_index('ix_brobyggere_telefon_norm', 'brobyggere', ['telefon_norm'])

    # ── aftaler: manglende klassificerings- + log-kolonner ────────────────────
    for col in (
        sa.Column('aftaletype',          sa.Text()),
        sa.Column('brobygningstype',     sa.Text()),   # Social|Forening|Sundhed
        sa.Column('henvender',           sa.Text()),
        sa.Column('modtager',            sa.Text()),
        sa.Column('finansiering',        sa.Text()),
        sa.Column('samarbejdspartner',   sa.Text()),
        sa.Column('afdeling',            sa.Text()),
        sa.Column('aflyst_af',           sa.Text()),
        sa.Column('aflysnings_aarsag',   sa.Text()),
        sa.Column('transportplan',       sa.Text()),
        sa.Column('aktivitets_tid',      sa.Text()),
        sa.Column('fremmoede_type',      sa.Text()),
        sa.Column('gentagelse',          sa.Text()),
        sa.Column('aftale_form',         sa.Text()),
        sa.Column('brobygger_note',      sa.Text()),    # briefing til brobygger (gemt på aftalen)
        sa.Column('raadgiver_opfoelgning', sa.Text()),
        # brobyggerLog (udfald af afholdt aftale)
        sa.Column('udfald',              sa.Text()),     # gennemfoert|afbud|ikke-modt
        sa.Column('varighed_min',        sa.Integer()),
        sa.Column('log_note',            sa.Text()),
        sa.Column('logged_at',           sa.TIMESTAMP(timezone=True)),
    ):
        op.add_column('aftaler', col)


def downgrade() -> None:
    # aftaler-kolonner
    for name in ('aftaletype', 'brobygningstype', 'henvender', 'modtager', 'finansiering',
                 'samarbejdspartner', 'afdeling', 'aflyst_af', 'aflysnings_aarsag', 'transportplan',
                 'aktivitets_tid', 'fremmoede_type', 'gentagelse', 'aftale_form', 'brobygger_note',
                 'raadgiver_opfoelgning', 'udfald', 'varighed_min', 'log_note', 'logged_at'):
        op.drop_column('aftaler', name)

    op.drop_index('ix_brobyggere_telefon_norm', table_name='brobyggere')
    op.drop_column('brobyggere', 'telefon_norm')
    op.drop_column('brobyggere', 'afdeling')

    op.drop_index('ix_mennesker_telefon_norm', table_name='mennesker')
    for name in ('telefon_norm', 'ucla_fravalgt', 'afslut_aarsag', 'afslut_trivsel', 'praeferencer',
                 'helbreds_kategorier', 'sroi_maalgruppe', 'meetpoint', 'kilde', 'afdeling'):
        op.drop_column('mennesker', name)

    op.drop_table('kontaktpersoner')
    op.drop_table('besked_skabeloner')
    op.drop_table('opkald_log')
    op.drop_table('udlaeg_konti')
    op.drop_table('ucla_maalinger')
    op.drop_table('henvendelser')
    op.drop_table('stamdata')

    op.execute("DROP TYPE IF EXISTS opkald_type")
    op.execute("DROP TYPE IF EXISTS ucla_slags")
    # Bemærk: tilføjede aftale_status-værdier fjernes ikke (PostgreSQL kan ikke
    # fjerne enum-værdier uden at gen-skabe typen) — det er harmløst at lade dem stå.
