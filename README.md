# Vaeren — Compliance-Autopilot

> Schema-per-Tenant SaaS. Stand Sprint 5: HinSchG-Hinweisgeberportal mit per-Tenant-Encryption (Fernet), anonymem Submission-Form + Bearbeiter-Dashboard + automatischem Frist-Tracking (HinSchG §17).
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
uv run pytest -v                     # alle (153)
uv run pytest -m tenant_isolation -v # nur kritischer CI-Gate
uv run ruff check . && uv run ruff format --check .
```

### Frontend-Setup (Sprint 3+)

```bash
# 1. bun installieren (falls nicht da)
curl -fsSL https://bun.sh/install | bash

# 2. Deps + Dev-Server
cd frontend
bun install
bun run dev     # http://localhost:5173
bun test        # 16 smoke tests
bun run typecheck
bun run build   # Production-Build

# 3. OpenAPI-Type-Sync (nach jedem Backend-Schema-Change)
./backend/scripts/export-openapi.sh
./frontend/scripts/sync-openapi.sh
git diff --exit-code -- frontend/src/lib/api/   # CI-Gate
```

**Vite-Proxy-Routing für Dev:**
Der Dev-Server proxied `/api/*` und `/accounts/*` zum Django-Backend
(`localhost:8000`) mit `Host: acme.app.localhost`-Header, damit
`django-tenants` korrekt routet. `/etc/hosts` braucht den Eintrag
`127.0.0.1 acme.app.localhost` und einen Test-Tenant mit dieser Domain.

## Architektur-Quickref

- **Backend:** Django 5 + DRF + drf-spectacular, Schema-per-Tenant via `django-tenants`
- **Auth:** `django-allauth` + `dj-rest-auth` + `allauth.mfa` (Session-Cookie, TOTP-MFA, 2-stage-Login mit ephemeralem Token)
- **DB:** Postgres 16, Redis 7
- **Frontend:** Vite + React 18 + TypeScript + Tailwind + shadcn/ui, TanStack Query, Zustand, React Router 7, React Hook Form + Zod
- **Type-Safety End-to-End:** drf-spectacular → openapi-typescript → `frontend/src/lib/api/types.gen.ts`. CI-Gate gegen Drift.
- **Code-Layout:** `backend/tenants/` (public-Schema + Demo-Lead-Capture), `backend/core/` (tenant-Schema-Baseline mit User), `frontend/src/{routes,components,lib/api,lib/stores}/`
- **Datenmodell (Sprint 2):** Mitarbeiter, ComplianceTask (polymorph via django-polymorphic), Evidence (immutable, SHA-256), Notification, AuditLog (immutable, GenericFK target). Sprint 3: DemoRequest (public-Schema).
- **Permissions:** `django-rules`-Predicates (siehe `backend/core/rules.py`). DRF-Adapter in `permissions.py`.
- **AuditLog-Auto-Population:** Signals (catch-all für ORM-Saves) + DRF-Mixin (Request-Kontext: User, IP).

Tiefer: `CLAUDE.md` (Kurz-Referenz) und `docs/superpowers/specs/` (Specs).

## Sprint-Stand

| Sprint | Status |
|---|---|
| 1 | ✅ Foundation (Repo, Django, Multi-Tenancy, Auth, Test-Tenant) |
| 2 | ✅ Shared Core (Mitarbeiter, ComplianceTask, Evidence, Notification, AuditLog) + Mitarbeiter/ComplianceTask-API + django-rules-Permissions + AuditLog-Auto-Population |
| 3 | ✅ Frontend-Foundation: Vite + React + TS + Tailwind + shadcn/ui, Login + MFA-Setup/Challenge + Mitarbeiter-CRUD + Demo-Form, openapi-typescript-Pipeline, 16 bun-Tests, CI 3-Job (backend/frontend/openapi-sync) |
| 4 | ✅ Pflichtunterweisung: Kurs/Modul/Frage/Welle-Models, Schulungs-Wizard (4-Step) + Token-basierte Public-Quiz-Routen, LLM-Personalisierung mit RDG-Layer-2-Validator + Static-Fallback, Mailjet mit Console-Backend-Fallback, WeasyPrint-Zertifikate (HTML-Fallback), 35 neue Backend-Tests |
| 5 | ✅ HinSchG-Hinweisgeberportal: Per-Tenant-Fernet-Encryption (`core.fields.EncryptedTextField`), Meldung/Bearbeitungsschritt-Models mit verschlüsselten Inhalten, automatische 7d/3m-Pflicht-Tasks (§17), Public-Form `/hinweise` (anonyme Submission) + Status-Page `/hinweise/status/<token>`, Bearbeiter-Dashboard `/meldungen`, sanitized Status-API (keine Bearbeiter-Identität nach außen), 30 neue Backend-Tests inkl. Cross-Tenant-Decrypt-Isolation |
| 6+ | siehe Spec §12 |
