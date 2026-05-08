# Vaeren — Compliance-Autopilot

> Schema-per-Tenant SaaS. Stand Sprint 1: Foundation komplett (Django 5 + Multi-Tenancy + Auth-Stack).
> Architektur-Spec: `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md`.

## Lokales Dev-Setup

### Prerequisites

- Docker + Docker Compose
- `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `/etc/hosts` Eintrag (einmalig): `127.0.0.1 dev.app.vaeren.local`

### Setup

```bash
# 1. Env-File anlegen
cp .env.example .env

# 2. Postgres + Redis starten
docker compose -f docker-compose.dev.yml --env-file .env up -d

# 3. Backend-Deps installieren + Migrations
cd backend
uv sync
uv run python manage.py migrate_schemas --shared

# 4. Test-Tenant anlegen
uv run python manage.py create_tenant \
    --schema dev --firma "Dev GmbH" --domain "dev.app.vaeren.local" --pilot

# 5. Dev-Server starten
uv run python manage.py runserver 0.0.0.0:8000

# 6. Health-Check
curl http://dev.app.vaeren.local:8000/api/health/
# {"status":"ok","schema":"dev"}
```

### Tests laufen

```bash
cd backend
uv run pytest -v                     # alle
uv run pytest -m tenant_isolation -v # nur kritischer CI-Gate
uv run ruff check . && uv run ruff format --check .
```

## Architektur-Quickref

- **Backend:** Django 5 + DRF + drf-spectacular, Schema-per-Tenant via `django-tenants`
- **Auth:** `django-allauth` + `dj-rest-auth` + `django-otp` (Session-Cookie, TOTP-MFA)
- **DB:** Postgres 16, Redis 7
- **Code-Layout:** `backend/tenants/` (public-Schema), `backend/core/` (tenant-Schema-Baseline mit User)

Tiefer: `CLAUDE.md` (Kurz-Referenz) und `docs/superpowers/specs/` (Specs).

## Sprint-Stand

| Sprint | Status |
|---|---|
| 1 | ✅ Foundation (Repo, Django, Multi-Tenancy, Auth, Test-Tenant) |
| 2 | ⬜ Shared Core Models + DRF API + AuditLog |
| 3+ | siehe Spec §12 |
