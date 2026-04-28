"""
backend/alembic/env.py

Kør migrationer:
    alembic upgrade head          # anvend alle afventende
    alembic downgrade -1          # rul én tilbage
    alembic revision --autogenerate -m "tilføj tabel xyz"  # auto-generer ny
"""

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Hent DATABASE_URL fra miljø (sæt i .env eller Azure App Settings)
database_url = os.environ.get("DATABASE_URL", "postgresql://bbadmin:password@localhost:5432/brobygger")
config.set_main_option("sqlalchemy.url", database_url)

# ── Metadata til autogenerate ─────────────────────────────────────────────────
# Importér Base-metadata fra ORM-modeller (tilføjes i Fase 2):
# from backend.database import Base
# target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Kør migrationer uden database-forbindelse (generer SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Kør migrationer med live database-forbindelse."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
