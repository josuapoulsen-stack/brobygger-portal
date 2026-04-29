# Makefile — SoS Brobygger Portal
# Krav: Docker Desktop + make (Windows: via Git Bash / WSL / Chocolatey)
#
# Hurtigstart:
#   make setup    — første gang: start DB, kør migrationer, seed
#   make dev      — start hele stacken

.PHONY: help setup dev stop reset migrate seed test lint logs api-shell db-shell

# ── Standard ──────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  SoS Brobygger Portal"
	@echo ""
	@echo "  make setup      Første gang: DB + migrationer + demo-data"
	@echo "  make dev        Start hele stacken (DB + API + Frontend)"
	@echo "  make stop       Stop alle containere"
	@echo "  make reset      Nulstil DB fuldstændigt (tab alle data)"
	@echo ""
	@echo "  make migrate    Kør Alembic-migrationer (upgrade head)"
	@echo "  make seed       Indlæs demo-data"
	@echo "  make test       Kør pytest i API-containeren"
	@echo "  make lint       Kør ruff (Python) + ESLint (JS)"
	@echo ""
	@echo "  make logs       Vis logs fra alle containere"
	@echo "  make api-shell  Åbn shell i API-containeren"
	@echo "  make db-shell   Åbn psql i DB-containeren"
	@echo ""

# ── Opsætning ──────────────────────────────────────────────────────────────────
setup:
	@echo "→ Starter database..."
	docker compose up -d db
	@echo "→ Venter på at DB er klar..."
	docker compose run --rm migrate
	@echo "→ Indlæser demo-data..."
	docker compose run --rm seed
	@echo "✓ Klar. Kør 'make dev' for at starte stacken."

# ── Udvikling ──────────────────────────────────────────────────────────────────
dev:
	docker compose up

stop:
	docker compose down

# ── Database ───────────────────────────────────────────────────────────────────
reset:
	@echo "⚠  Dette sletter AL data i databasen."
	@read -p "Fortsæt? [y/N] " ans && [ "$$ans" = "y" ]
	docker compose down -v
	docker compose up -d db
	docker compose run --rm migrate
	docker compose run --rm seed
	@echo "✓ Database nulstillet med demo-data."

migrate:
	docker compose run --rm migrate

seed:
	docker compose run --rm seed

# ── Test ───────────────────────────────────────────────────────────────────────
test:
	docker compose run --rm api pytest backend/tests/ -v --tb=short

test-matching:
	docker compose run --rm api pytest backend/tests/test_matching.py -v

# ── Kode-kvalitet ──────────────────────────────────────────────────────────────
lint:
	docker compose run --rm api ruff check backend/ || true
	npm run lint 2>/dev/null || echo "(ESLint ikke konfigureret endnu)"

# ── Logs og shells ─────────────────────────────────────────────────────────────
logs:
	docker compose logs -f --tail=50

api-shell:
	docker compose exec api bash

db-shell:
	docker compose exec db psql -U bbadmin -d brobygger
