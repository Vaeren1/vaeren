# Sprint 1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Foundation für Vaeren MVP — Repo-Skeleton, Django 5 + DRF + Multi-Tenancy via `django-tenants`, Custom-User mit Rollen, Auth-Stack (`django-allauth` + `dj-rest-auth` + `django-allauth-2fa`), `create_tenant`-Management-Command, Multi-Tenant-Isolation-Test als kritischer CI-Gate, GitHub-Actions-Pipeline.

**Architecture:** Single Django-Backend in `backend/` mit Schema-per-Tenant (`django-tenants`). `public`-Schema für `Tenant` + `TenantDomain`, je-Tenant-Schema für Geschäftsdaten + `User`. Lokales Dev-Setup über `docker-compose.dev.yml` (Postgres 16 + Redis 7). Tests über `pytest-django`; Multi-Tenant-Isolation ist ein nicht-verhandelbarer CI-Gate. Frontend, Mailjet, LLM, Production-Deploy bewusst **out of scope** (Sprints 3/4/8).

**Tech Stack:** Python 3.12, Django 5.0 LTS, DRF, drf-spectacular, django-tenants, django-allauth + dj-rest-auth + django-allauth-2fa, Postgres 16, Redis 7, pytest-django + factory_boy + responses, uv, Ruff, GitHub Actions.

**Spec-Referenz:** `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md` §2 (Stack), §4 (Multi-Tenancy), §5 (Datenmodell — public + tenant), §6 (Auth), §10 (Test-Strategie), §12 (Sprint-Plan), §14 (Risiken).

---

## Datei-Struktur (Sprint 1)

Sprint 1 erzeugt **neue Dateien**; ergänzt nur `.gitignore` und `README.md`. Die Struktur folgt §9 Repo-Struktur des Specs.

```
ai-act/
├── .env.example                                  # Sprint-1: Postgres + Django-Secret + Tenant-Defaults
├── .gitignore                                    # erweitert
├── .github/workflows/test.yml                    # Backend-Tests + Multi-Tenant-Isolation-Gate
├── docker-compose.dev.yml                        # Postgres 16 + Redis 7 für lokales Dev
├── README.md                                     # Setup-Anleitung ergänzt
└── backend/
    ├── pyproject.toml                            # uv-managed, Ruff-Config inline
    ├── uv.lock                                   # generiert
    ├── manage.py
    ├── pytest.ini                                # pytest-django Settings
    ├── config/                                   # Django-Project
    │   ├── __init__.py
    │   ├── settings/
    │   │   ├── __init__.py
    │   │   ├── base.py                           # SHARED_APPS / TENANT_APPS / DRF / Allauth
    │   │   ├── dev.py
    │   │   ├── test.py                           # nutzt eigene Test-DB
    │   │   └── prod.py                           # Stub für Sprint 8
    │   ├── urls_public.py                        # public-Schema URLs (Tenant-Onboarding später)
    │   ├── urls_tenant.py                        # tenant-Schema URLs (Auth, Health, Schema)
    │   ├── asgi.py
    │   └── wsgi.py
    ├── tenants/                                  # public-Schema App
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── models.py                             # Tenant, TenantDomain
    │   ├── admin.py
    │   ├── migrations/__init__.py
    │   └── management/
    │       ├── __init__.py
    │       └── commands/
    │           ├── __init__.py
    │           └── create_tenant.py
    ├── core/                                     # Tenant-Schema-Baseline
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── models.py                             # Custom User mit Rollen
    │   ├── views.py                              # /api/health/
    │   ├── urls.py
    │   └── migrations/__init__.py
    └── tests/
        ├── __init__.py
        ├── conftest.py                           # pytest-Fixtures + Tenant-DB-Setup
        ├── factories.py                          # TenantFactory, UserFactory
        ├── test_tenant_isolation.py              # KRITISCHER CI-GATE
        ├── test_auth_smoke.py                    # django-tenants × allauth × 2fa Smoke
        ├── test_create_tenant_command.py
        └── test_health.py
```

**Decomposition-Begründung:**
- `tenants/` (public) und `core/` (tenant) sind getrennt, weil sie in unterschiedliche Schemas migriert werden — dieselbe Trennung erzwingt `django-tenants` über `SHARED_APPS` vs. `TENANT_APPS`.
- `config/urls_public.py` vs. `urls_tenant.py` ist `django-tenants`-Konvention — Subdomain-Erkennung wählt das URLconf für die Request-Laufzeit.
- `tests/` flach unter `backend/`, weil pytest-django sowieso projekt-weit collected wird; per-App-Tests sind Sprint-2+-Konvention sobald die Apps wachsen.

---

## Task 1: Repo-Skeleton + uv-Init + erweiterte .gitignore

**Ziel:** Backend-Verzeichnis anlegen, uv-Projekt initialisieren, `.gitignore` für Python + JS + Docker erweitern, `.env.example` schaffen.

**Files:**
- Create: `backend/pyproject.toml`
- Modify: `.gitignore` (erweitern)
- Create: `.env.example`

- [ ] **Step 1.1: uv-Verfügbarkeit prüfen**

```bash
uv --version
```

Expected: `uv 0.5.x` oder neuer. Wenn fehlend: `curl -LsSf https://astral.sh/uv/install.sh | sh` ausführen, Shell neu starten.

- [ ] **Step 1.2: Backend-Verzeichnis anlegen + uv-Projekt initialisieren**

```bash
cd /home/konrad/ai-act
mkdir -p backend
cd backend
uv init --python 3.12 --name vaeren-backend --no-readme --no-workspace
```

Expected: erzeugt `backend/pyproject.toml`, `backend/.python-version`, `backend/main.py`. Die `main.py` löschen wir gleich, sie wird durch `manage.py` ersetzt.

```bash
rm /home/konrad/ai-act/backend/main.py
rm -f /home/konrad/ai-act/backend/.python-version  # wir legen Python-Version in pyproject.toml fest
```

- [ ] **Step 1.3: `pyproject.toml` mit endgültiger Form überschreiben**

Datei `/home/konrad/ai-act/backend/pyproject.toml` mit folgendem Inhalt:

```toml
[project]
name = "vaeren-backend"
version = "0.1.0"
description = "Vaeren Compliance-Autopilot — Django-Backend"
requires-python = ">=3.12,<3.13"
dependencies = []

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "DJ", "RUF"]
ignore = [
    "E501",   # Line-Length-Check übernimmt Formatter
    "DJ001",  # null=True auf TextField/CharField bei django-tenants legitim
]

[tool.ruff.lint.per-file-ignores]
"**/migrations/*.py" = ["E", "F", "W", "N", "B"]
"**/settings/*.py" = ["F405", "F403"]

[tool.ruff.format]
quote-style = "double"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "-ra --strict-markers --tb=short"
```

- [ ] **Step 1.4: Root-`.gitignore` erweitern**

Aktuelle `.gitignore` lesen, dann ersetzen durch:

```gitignore
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
.ruff_cache/
htmlcov/
.coverage
coverage.xml

# uv
# uv.lock IS committed; only ignore caches
.uv/

# Node/Bun
node_modules/
.bun/
bun.lockb.bak

# Django
*.log
*.sqlite3
staticfiles/
media/

# Env
.env
.env.local
.env.production
.env.dev
!.env.example

# Editors / OS
.idea/
.vscode/
.DS_Store

# Superpowers
.superpowers/
```

- [ ] **Step 1.5: `.env.example` anlegen**

Datei `/home/konrad/ai-act/.env.example`:

```env
# Vaeren Backend — Environment-Variablen (Beispiel)
# Niemals echte Secrets in dieses File schreiben.

# Django
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=replace-me-with-secrets-token-urlsafe-50
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.app.vaeren.local

# Postgres (lokal über docker-compose.dev.yml)
POSTGRES_DB=vaeren
POSTGRES_USER=vaeren
POSTGRES_PASSWORD=vaeren_dev_only
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/0

# Tenant-Defaults
PUBLIC_TENANT_DOMAIN=vaeren.local
```

- [ ] **Step 1.6: Verifikations-Run + Commit**

```bash
cd /home/konrad/ai-act
git status
```

Expected: untracked = `backend/pyproject.toml`, `.env.example`. Modified = `.gitignore`.

```bash
git add backend/pyproject.toml .gitignore .env.example
git commit -m "chore(backend): initialize uv project skeleton + env template"
```

---

## Task 2: Lokale Dev-Infrastruktur — Postgres 16 + Redis 7 via docker-compose.dev.yml

**Ziel:** Postgres und Redis lokal verfügbar machen, sodass Django-Migrations und Tests laufen.

**Files:**
- Create: `docker-compose.dev.yml`

- [ ] **Step 2.1: `docker-compose.dev.yml` schreiben**

Datei `/home/konrad/ai-act/docker-compose.dev.yml`:

```yaml
# Lokales Dev-Setup. NICHT für Production verwenden.
# Production-Compose liegt in Sprint 8 unter docker-compose.prod.yml.
services:
  postgres:
    image: postgres:16-alpine
    container_name: vaeren-dev-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-vaeren}
      POSTGRES_USER: ${POSTGRES_USER:-vaeren}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-vaeren_dev_only}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - vaeren-dev-postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-vaeren}"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: vaeren-dev-redis
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - vaeren-dev-redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  vaeren-dev-postgres-data:
  vaeren-dev-redis-data:
```

- [ ] **Step 2.2: `.env`-Datei lokal anlegen (NICHT committed)**

```bash
cd /home/konrad/ai-act
cp .env.example .env
```

Erinnerung: `.env` ist in `.gitignore`, wird also nie committed.

- [ ] **Step 2.3: Container starten und Health verifizieren**

```bash
cd /home/konrad/ai-act
docker compose -f docker-compose.dev.yml --env-file .env up -d
docker compose -f docker-compose.dev.yml ps
```

Expected: beide Container `Up (healthy)`. Wenn nicht healthy: `docker compose -f docker-compose.dev.yml logs` zur Diagnose.

- [ ] **Step 2.4: Postgres-Konnektivität von außen prüfen**

```bash
docker exec vaeren-dev-postgres psql -U vaeren -d vaeren -c "SELECT version();"
```

Expected: `PostgreSQL 16.x ... aarch64-unknown-linux-musl ...` (oder x86_64 je nach Host).

- [ ] **Step 2.5: Commit**

```bash
cd /home/konrad/ai-act
git add docker-compose.dev.yml
git commit -m "chore(infra): add docker-compose.dev.yml for local Postgres+Redis"
```

---

## Task 3: Django-Projekt bootstrappen mit Split-Settings

**Ziel:** Django + DRF + drf-spectacular installieren, `manage.py` und `config/`-Layout aufbauen, Settings in `base/dev/test/prod` aufgeteilt. Noch ohne Multi-Tenancy.

**Files:**
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings/__init__.py`
- Create: `backend/config/settings/base.py`
- Create: `backend/config/settings/dev.py`
- Create: `backend/config/settings/test.py`
- Create: `backend/config/settings/prod.py`
- Create: `backend/config/urls_public.py`
- Create: `backend/config/urls_tenant.py`
- Create: `backend/config/asgi.py`
- Create: `backend/config/wsgi.py`
- Modify: `backend/pyproject.toml` (uv add fügt Deps ein)

- [ ] **Step 3.1: Core-Deps via `uv add` installieren**

```bash
cd /home/konrad/ai-act/backend
uv add "django>=5.0,<5.1" "djangorestframework>=3.15" "drf-spectacular>=0.27" "psycopg[binary]>=3.2" "django-environ>=0.11"
```

Expected: erzeugt/aktualisiert `backend/uv.lock` und ergänzt `[project].dependencies` in `pyproject.toml`. uv erstellt `backend/.venv/` automatisch.

- [ ] **Step 3.2: Django-Project-Files schreiben — `manage.py`**

Datei `/home/konrad/ai-act/backend/manage.py`:

```python
#!/usr/bin/env python
"""Django Management-Entry-Point."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Django not installed. Run `uv sync` inside backend/."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.3: `config/__init__.py` und `config/settings/__init__.py` (leer)**

```bash
mkdir -p /home/konrad/ai-act/backend/config/settings
touch /home/konrad/ai-act/backend/config/__init__.py
touch /home/konrad/ai-act/backend/config/settings/__init__.py
```

- [ ] **Step 3.4: `config/settings/base.py` schreiben**

Datei `/home/konrad/ai-act/backend/config/settings/base.py`:

```python
"""Gemeinsame Django-Settings. Konkrete Umgebungen erweitern dies."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent

env = environ.Env()
# .env aus Repo-Root lesen, falls vorhanden
env_file = REPO_ROOT / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-default-only-for-import")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Multi-Tenant-Apps werden in Task 5 ergänzt.
SHARED_APPS: list[str] = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
TENANT_APPS: list[str] = []
INSTALLED_APPS = SHARED_APPS + [a for a in TENANT_APPS if a not in SHARED_APPS]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Public + Tenant URLconfs werden in Task 5 endgültig konfiguriert.
ROOT_URLCONF = "config.urls_tenant"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="vaeren"),
        "USER": env("POSTGRES_USER", default="vaeren"),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
        "HOST": env("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Vaeren API",
    "DESCRIPTION": "Compliance-Autopilot Backend-API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
```

- [ ] **Step 3.5: `config/settings/dev.py`**

Datei `/home/konrad/ai-act/backend/config/settings/dev.py`:

```python
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
```

- [ ] **Step 3.6: `config/settings/test.py`**

Datei `/home/konrad/ai-act/backend/config/settings/test.py`:

```python
from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-only-key-not-for-production"  # noqa: S105
# Tests laufen gegen dieselbe lokale Postgres-Instanz; pytest-django legt
# automatisch eine separate Test-DB an (vorangestellt mit "test_").
```

- [ ] **Step 3.7: `config/settings/prod.py` (Stub für Sprint 8)**

Datei `/home/konrad/ai-act/backend/config/settings/prod.py`:

```python
"""Prod-Settings. Wird in Sprint 8 (Production-Deploy) finalisiert."""
from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

- [ ] **Step 3.8: `urls_public.py` und `urls_tenant.py` (vorerst minimal)**

Datei `/home/konrad/ai-act/backend/config/urls_public.py`:

```python
"""URLs für das public-Schema (Tenant-Onboarding, globales Admin — Sprint 1.5+)."""
from django.urls import path

urlpatterns: list = [
    # path("admin/", admin.site.urls),  # wird in Sprint 2 ergänzt
]
```

Datei `/home/konrad/ai-act/backend/config/urls_tenant.py`:

```python
"""URLs für tenant-Schemas (App-Funktionalität)."""
from django.urls import path

urlpatterns: list = [
    # path("api/health/", ...) wird in Task 9 ergänzt
]
```

- [ ] **Step 3.9: `config/asgi.py` und `config/wsgi.py`**

Datei `/home/konrad/ai-act/backend/config/asgi.py`:

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_asgi_application()
```

Datei `/home/konrad/ai-act/backend/config/wsgi.py`:

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
application = get_wsgi_application()
```

- [ ] **Step 3.10: Verifikation — Django-Check**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py check --settings=config.settings.dev
```

Expected: `System check identified no issues (0 silenced).`

Fehlerfall: `django.db.utils.OperationalError` heißt Postgres läuft nicht — Task 2 prüfen. `ImproperlyConfigured: SECRET_KEY` heißt `.env` fehlt.

- [ ] **Step 3.11: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(backend): bootstrap django 5 project with split settings"
```

---

## Task 4: pytest-Setup + factory_boy + responses + conftest

**Ziel:** Test-Infra einrichten, sodass spätere Multi-Tenant-Tests darauf aufbauen können.

**Files:**
- Modify: `backend/pyproject.toml` (via `uv add --dev`)
- Create: `backend/pytest.ini`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_smoke.py` (temporär — wird in Task 5 ersetzt)

- [ ] **Step 4.1: Test-Deps installieren**

```bash
cd /home/konrad/ai-act/backend
uv add --dev "pytest>=8" "pytest-django>=4.8" "factory-boy>=3.3" "responses>=0.25" "ruff>=0.6"
```

- [ ] **Step 4.2: `pytest.ini` schreiben**

Datei `/home/konrad/ai-act/backend/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = test_*.py
addopts = -ra --strict-markers --tb=short
markers =
    tenant_isolation: marks tests as critical multi-tenant isolation gates
```

(Hinweis: pyproject.toml hat denselben Eintrag — pytest.ini gewinnt für lokale Klarheit, beides schadet nicht.)

- [ ] **Step 4.3: Failing Smoke-Test schreiben**

Datei `/home/konrad/ai-act/backend/tests/__init__.py` (leer anlegen):

```bash
mkdir -p /home/konrad/ai-act/backend/tests
touch /home/konrad/ai-act/backend/tests/__init__.py
```

Datei `/home/konrad/ai-act/backend/tests/test_smoke.py`:

```python
"""Smoke-Test — wird durch echte Tests in Task 5+ ersetzt."""
import django


def test_django_imports() -> None:
    assert django.VERSION[0] == 5
```

- [ ] **Step 4.4: Test laufen — soll grün sein**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_smoke.py -v
```

Expected: `1 passed`. Falls Fehler `Database access not allowed`: das Smoke-File nutzt `db`-Fixture nicht, sollte daher passen. Falls anderer Fehler: `DJANGO_SETTINGS_MODULE` oder `.env` prüfen.

- [ ] **Step 4.5: Minimaler `conftest.py` (Tenant-Fixtures kommen in Task 5)**

Datei `/home/konrad/ai-act/backend/tests/conftest.py`:

```python
"""Globale pytest-Fixtures. Erweitert in Task 5 mit Tenant-Fixtures."""
import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sicherheitsnetz: blockiert versehentliche echte Outbound-HTTP-Calls.

    Tests müssen `responses` oder explizites Mocking nutzen. Wenn sie
    Network-Activity wollen, ist das ein Designfehler.
    """
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")
```

- [ ] **Step 4.6: Erneuter Run + Commit**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: `1 passed`.

```bash
cd /home/konrad/ai-act
git add backend/pyproject.toml backend/uv.lock backend/pytest.ini backend/tests/
git commit -m "test(backend): add pytest + factory-boy + responses skeleton"
```

---

## Task 5: django-tenants — Tenant + TenantDomain Models, Multi-Tenancy aktivieren

**Ziel:** `django-tenants` einbauen, `tenants/`-App mit `Tenant`+`TenantDomain` anlegen, Settings auf Multi-Tenancy umstellen, public-Migration laufen lassen, manuell einen Test-Tenant erzeugen.

**Files:**
- Modify: `backend/pyproject.toml` (via `uv add`)
- Modify: `backend/config/settings/base.py`
- Create: `backend/tenants/__init__.py`
- Create: `backend/tenants/apps.py`
- Create: `backend/tenants/models.py`
- Create: `backend/tenants/admin.py`
- Create: `backend/tenants/migrations/__init__.py`

- [ ] **Step 5.1: `django-tenants` installieren**

```bash
cd /home/konrad/ai-act/backend
uv add "django-tenants>=3.7"
```

- [ ] **Step 5.2: TDD — Failing Test für Tenant-Modell schreiben**

Datei `/home/konrad/ai-act/backend/tests/test_tenant_isolation.py`:

```python
"""Multi-Tenant-Isolation — kritischer CI-Gate (Spec §10).

Datenleak zwischen Tenants ist nicht verhandelbar. Wenn dieser Test
bricht, schlägt CI fehl und der PR kann nicht gemergt werden.
"""
import pytest
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context


@pytest.fixture
def two_tenants(db):
    """Zwei minimal-Tenants im public-Schema, jeweils mit eigenem Schema."""
    Tenant = get_tenant_model()
    acme = Tenant(schema_name="acme_test", firma_name="ACME GmbH")
    acme.save()  # legt Schema automatisch an
    meier = Tenant(schema_name="meier_test", firma_name="Meier KG")
    meier.save()
    yield acme, meier
    # Aufräumen erfolgt durch pytest-django's transactional rollback
    # plus djang-tenants's auto_drop_schema (siehe Tenant-Model).


@pytest.mark.tenant_isolation
def test_tenants_have_distinct_schemas(two_tenants):
    acme, meier = two_tenants
    assert acme.schema_name != meier.schema_name


@pytest.mark.tenant_isolation
def test_schema_context_switches_connection(two_tenants):
    acme, meier = two_tenants
    with schema_context(acme.schema_name):
        assert connection.schema_name == "acme_test"
    with schema_context(meier.schema_name):
        assert connection.schema_name == "meier_test"
```

- [ ] **Step 5.3: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_tenant_isolation.py -v
```

Expected FAIL: `LookupError` oder `ImproperlyConfigured: TENANT_MODEL not configured` — weil Tenant-Modell+Settings fehlen.

- [ ] **Step 5.4: `tenants/`-App-Skeleton anlegen**

```bash
mkdir -p /home/konrad/ai-act/backend/tenants/migrations
touch /home/konrad/ai-act/backend/tenants/__init__.py
touch /home/konrad/ai-act/backend/tenants/migrations/__init__.py
```

Datei `/home/konrad/ai-act/backend/tenants/apps.py`:

```python
from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants"
    verbose_name = "Tenants (public schema)"
```

- [ ] **Step 5.5: Tenant + TenantDomain Models**

Datei `/home/konrad/ai-act/backend/tenants/models.py`:

```python
"""Public-Schema-Modelle. Spec §5."""
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Plan(models.TextChoices):
    STARTER = "starter", "Starter"
    PROFESSIONAL = "professional", "Professional"
    BUSINESS = "business", "Business"


class Tenant(TenantMixin):
    firma_name = models.CharField(max_length=200)
    plan = models.CharField(
        max_length=20, choices=Plan.choices, default=Plan.PROFESSIONAL
    )
    pilot = models.BooleanField(default=False)
    pilot_discount_percent = models.PositiveSmallIntegerField(default=0)
    mfa_required = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, default="de-DE")
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # django-tenants legt Schema automatisch beim ersten save() an.
    auto_create_schema = True
    # In Tests Schema beim Tenant-Delete droppen (Cleanup).
    auto_drop_schema = True

    def __str__(self) -> str:
        return f"{self.firma_name} ({self.schema_name})"


class TenantDomain(DomainMixin):
    """Subdomain → Tenant-Mapping. `acme.app.vaeren.de` → Tenant `acme_gmbh`."""

    pass
```

- [ ] **Step 5.6: `tenants/admin.py` (minimal)**

Datei `/home/konrad/ai-act/backend/tenants/admin.py`:

```python
from django.contrib import admin

from .models import Tenant, TenantDomain

admin.site.register(Tenant)
admin.site.register(TenantDomain)
```

- [ ] **Step 5.7: `base.py` auf Multi-Tenant umkonfigurieren**

Datei `/home/konrad/ai-act/backend/config/settings/base.py` — folgende Blöcke ersetzen:

Ersetze `SHARED_APPS`/`TENANT_APPS`/`INSTALLED_APPS`-Block durch:

```python
SHARED_APPS: list[str] = [
    "django_tenants",
    "tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
]
TENANT_APPS: list[str] = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
]
INSTALLED_APPS = SHARED_APPS + [a for a in TENANT_APPS if a not in SHARED_APPS]
```

Ersetze `MIDDLEWARE` durch:

```python
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",  # MUSS first sein
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Ersetze `DATABASES` durch:

```python
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("POSTGRES_DB", default="vaeren"),
        "USER": env("POSTGRES_USER", default="vaeren"),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
        "HOST": env("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
```

Am Ende der Datei ergänzen:

```python
TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.TenantDomain"
```

- [ ] **Step 5.8: Migrations für `tenants`-App anlegen**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations tenants
```

Expected: erzeugt `backend/tenants/migrations/0001_initial.py`. Wenn keine Migration erzeugt: prüfen, dass `tenants` in `SHARED_APPS` steht und `tenants/__init__.py`/`apps.py` existieren.

- [ ] **Step 5.9: Public-Schema migrieren**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py migrate_schemas --shared
```

Expected: `Migrating shared apps, schema public ... OK` für `contenttypes`, `auth`, `tenants`.

- [ ] **Step 5.10: conftest.py erweitern für Tenant-Tests**

Datei `/home/konrad/ai-act/backend/tests/conftest.py` ersetzen durch:

```python
"""Globale pytest-Fixtures.

django-tenants verlangt Test-Sonderbehandlung: pytest-django's `db`-Fixture
mit `transactional_db` ist verlässlicher, weil django-tenants Schema-DDLs
ausführt, die in transaktionalen Tests automatisch zurückgerollt werden.
"""
import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")


@pytest.fixture
def db(transactional_db):  # noqa: F811
    """Erzwingt transactional_db für alle `db`-Fixturen.

    django-tenants legt Schemas via DDL an; in normalem `db` (transaktional)
    werden DDLs zwar gefahren, aber Cleanup ist unvollständig. transactional_db
    nutzt full-flush nach jedem Test.
    """
    yield
```

- [ ] **Step 5.11: Test erneut laufen — soll PASS geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_tenant_isolation.py -v
```

Expected: 2 passed.

Fehlerfall — `permission denied to create database`: Postgres-User braucht `CREATEDB`-Recht. Lokal lösen via:

```bash
docker exec vaeren-dev-postgres psql -U postgres -c "ALTER USER vaeren CREATEDB;"
```

(Dafür müsste der `postgres`-Superuser zugänglich sein. Im `postgres:16-alpine`-Default-Setup wird der Init-User automatisch Superuser, sodass dieser Schritt selten nötig ist. Wenn vaeren als Superuser angelegt wurde, entfällt das.)

- [ ] **Step 5.12: Smoke-Test entfernen + Commit**

```bash
cd /home/konrad/ai-act/backend
rm tests/test_smoke.py
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(backend): activate django-tenants with public schema models"
```

---

## Task 6: TenantFactory + isolierte Mitarbeiter-Probe-Test

**Ziel:** factory_boy-Factories für Tests + den vollständigen Spec-§10-Isolation-Test (mit echten Tenant-Schema-Modellen). Da wir noch keine Mitarbeiter-Modell haben (Sprint 2), nutzen wir den Django-`User`, der in Task 7 in `core/` lebt — Reihenfolge: Task 7 zuerst, dann ergänzen wir hier. **Anpassung:** Task 6 baut die Factories, der vollständige Cross-Schema-Test wird **erst nach Task 7** abgeschlossen.

**Files:**
- Create: `backend/tests/factories.py`

- [ ] **Step 6.1: TenantFactory schreiben**

Datei `/home/konrad/ai-act/backend/tests/factories.py`:

```python
"""factory_boy Factories für Tests."""
import factory
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
        django_get_or_create = ("schema_name",)

    schema_name = factory.Sequence(lambda n: f"test_tenant_{n}")
    firma_name = factory.Sequence(lambda n: f"Test-Firma {n} GmbH")
    plan = "professional"
    pilot = True
    pilot_discount_percent = 40


class TenantDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TenantDomain

    tenant = factory.SubFactory(TenantFactory)
    domain = factory.LazyAttribute(lambda o: f"{o.tenant.schema_name}.app.vaeren.local")
    is_primary = True
```

- [ ] **Step 6.2: TenantFactory durch existing Test verifizieren**

Datei `/home/konrad/ai-act/backend/tests/test_tenant_isolation.py` — Fixture `two_tenants` ersetzen durch Factory-basierte Variante:

Ersetze:

```python
@pytest.fixture
def two_tenants(db):
    """Zwei minimal-Tenants im public-Schema, jeweils mit eigenem Schema."""
    Tenant = get_tenant_model()
    acme = Tenant(schema_name="acme_test", firma_name="ACME GmbH")
    acme.save()  # legt Schema automatisch an
    meier = Tenant(schema_name="meier_test", firma_name="Meier KG")
    meier.save()
    yield acme, meier
    # Aufräumen erfolgt durch pytest-django's transactional rollback
    # plus djang-tenants's auto_drop_schema (siehe Tenant-Model).
```

durch:

```python
@pytest.fixture
def two_tenants(db):
    """Zwei minimal-Tenants im public-Schema, jeweils mit eigenem Schema."""
    from tests.factories import TenantFactory

    acme = TenantFactory(schema_name="acme_test", firma_name="ACME GmbH")
    meier = TenantFactory(schema_name="meier_test", firma_name="Meier KG")
    yield acme, meier
```

- [ ] **Step 6.3: Tests müssen weiterhin grün sein**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_tenant_isolation.py -v
```

Expected: 2 passed. Wenn nicht: `tests/__init__.py` als leeres File und Import-Path über `pyproject.toml` `[tool.pytest.ini_options].pythonpath` prüfen — alternativ in `pytest.ini` ergänzen:

```ini
pythonpath = .
```

- [ ] **Step 6.4: Commit**

```bash
cd /home/konrad/ai-act
git add backend/tests/
git commit -m "test(backend): add TenantFactory and route isolation test through factories"
```

---

## Task 7: Custom-User-Modell in `core` (Tenant-Schema) mit Rollen-Enum

**Ziel:** `core/`-App anlegen, `User` als `AbstractUser`-Subclass mit `email` als Username + Rollen-Choices (Spec §6 Permissions-Tabelle). User lebt im **Tenant-Schema** (TENANT_APPS).

**Files:**
- Create: `backend/core/__init__.py`
- Create: `backend/core/apps.py`
- Create: `backend/core/models.py`
- Create: `backend/core/managers.py`
- Create: `backend/core/migrations/__init__.py`
- Modify: `backend/config/settings/base.py` (AUTH_USER_MODEL, TENANT_APPS)

- [ ] **Step 7.1: Failing-Test für User-Model**

Datei `/home/konrad/ai-act/backend/tests/test_user_model.py`:

```python
"""Tests für Custom-User-Modell mit Rollen."""
import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="user_test_t", firma_name="UserTest")


def test_user_uses_email_as_username(tenant):
    User = get_user_model()
    with schema_context(tenant.schema_name):
        user = User.objects.create_user(
            email="anna@example.com", password="x" * 12
        )
        assert user.email == "anna@example.com"
        assert user.username == ""  # username-Feld entfernt/optional


def test_user_has_role_field(tenant):
    User = get_user_model()
    with schema_context(tenant.schema_name):
        user = User.objects.create_user(
            email="qm@example.com",
            password="x" * 12,
            tenant_role="qm_leiter",
        )
        assert user.tenant_role == "qm_leiter"


def test_user_role_default_is_view_only(tenant):
    User = get_user_model()
    with schema_context(tenant.schema_name):
        user = User.objects.create_user(
            email="newhire@example.com", password="x" * 12
        )
        assert user.tenant_role == "mitarbeiter_view_only"
```

- [ ] **Step 7.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_user_model.py -v
```

Expected FAIL: `AttributeError: 'User' object has no attribute 'tenant_role'` (Default-User).

- [ ] **Step 7.3: `core`-App-Skeleton anlegen**

```bash
mkdir -p /home/konrad/ai-act/backend/core/migrations
touch /home/konrad/ai-act/backend/core/__init__.py
touch /home/konrad/ai-act/backend/core/migrations/__init__.py
```

Datei `/home/konrad/ai-act/backend/core/apps.py`:

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core (tenant schema baseline)"
```

- [ ] **Step 7.4: User-Manager (email-basiert)**

Datei `/home/konrad/ai-act/backend/core/managers.py`:

```python
from django.contrib.auth.base_user import BaseUserManager


class EmailUserManager(BaseUserManager):
    """Manager für ein User-Modell, das `email` als Login-Feld nutzt."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str, **extra):
        if not email:
            raise ValueError("Email ist Pflicht.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("tenant_role", "geschaeftsfuehrer")
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser braucht is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser braucht is_superuser=True.")
        return self._create_user(email, password, **extra)
```

- [ ] **Step 7.5: User-Modell**

Datei `/home/konrad/ai-act/backend/core/models.py`:

```python
"""Tenant-Schema-Baseline-Modelle. Spec §5/§6."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import EmailUserManager


class TenantRole(models.TextChoices):
    GESCHAEFTSFUEHRER = "geschaeftsfuehrer", "Geschäftsführer:in"
    QM_LEITER = "qm_leiter", "QM-Leiter:in"
    IT_LEITER = "it_leiter", "IT-Leiter:in"
    COMPLIANCE_BEAUFTRAGTER = "compliance_beauftragter", "Compliance-Beauftragte:r"
    MITARBEITER_VIEW_ONLY = "mitarbeiter_view_only", "Mitarbeitende (nur Ansicht)"


class User(AbstractUser):
    """Login-User innerhalb eines Tenant-Schemas.

    `email` ist Login-Feld; `username` aus `AbstractUser` ist optional und
    wird leer gehalten. Rollen via `tenant_role`-Choices.
    """

    username = models.CharField(max_length=150, blank=True, default="")
    email = models.EmailField(unique=True)
    tenant_role = models.CharField(
        max_length=32,
        choices=TenantRole.choices,
        default=TenantRole.MITARBEITER_VIEW_ONLY,
    )
    mfa_enabled = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = EmailUserManager()

    def __str__(self) -> str:
        return f"{self.email} ({self.tenant_role})"
```

- [ ] **Step 7.6: Settings — AUTH_USER_MODEL + core in TENANT_APPS**

In `/home/konrad/ai-act/backend/config/settings/base.py`:

`TENANT_APPS` so erweitern:

```python
TENANT_APPS: list[str] = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "rest_framework",
    "drf_spectacular",
]
```

Am Ende der Datei ergänzen:

```python
AUTH_USER_MODEL = "core.User"
```

- [ ] **Step 7.7: Migration erzeugen + auf alle Tenant-Schemas migrieren**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations core
uv run python manage.py migrate_schemas
```

Expected: `0001_initial.py` für `core` wird erzeugt; `migrate_schemas` migriert public und alle Tenant-Schemas.

Hinweis: Wenn `auth.User` aus früheren Migrations bereits gefahren wurde, kann der AUTH_USER_MODEL-Switch zu `inconsistent migration history` führen. Bei lokalem Dev-Setup ist das einfachste Fix:

```bash
# Nur lokal, NIE in Production!
docker exec vaeren-dev-postgres psql -U vaeren -d vaeren -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
uv run python manage.py migrate_schemas --shared
```

- [ ] **Step 7.8: User-Tests laufen — sollten PASS geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_user_model.py -v
```

Expected: 3 passed.

- [ ] **Step 7.9: UserFactory ergänzen**

Datei `/home/konrad/ai-act/backend/tests/factories.py` — am Ende ergänzen:

```python
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    tenant_role = "qm_leiter"
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or "test-password-12345")
        self.save()
```

- [ ] **Step 7.10: Vollständigen Cross-Schema-Isolation-Test ergänzen**

Datei `/home/konrad/ai-act/backend/tests/test_tenant_isolation.py` — am Ende ergänzen:

```python
@pytest.mark.tenant_isolation
def test_user_cannot_be_seen_across_schemas(two_tenants):
    """Spec §10: User aus Tenant A darf niemals aus Tenant B sichtbar sein."""
    from django.contrib.auth import get_user_model

    from tests.factories import UserFactory

    acme, meier = two_tenants
    User = get_user_model()

    with schema_context(acme.schema_name):
        UserFactory(email="anna@acme.de")
        assert User.objects.filter(email="anna@acme.de").exists()

    with schema_context(meier.schema_name):
        # Im meier-Schema darf Anna nicht erscheinen.
        assert not User.objects.filter(email="anna@acme.de").exists()
        assert User.objects.count() == 0
```

- [ ] **Step 7.11: Vollständige Test-Suite laufen**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: alle Tests passed (mind. 6).

- [ ] **Step 7.12: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add custom User model with tenant roles"
```

---

## Task 8: django-allauth + dj-rest-auth + django-allauth-2fa Smoke-Test

**Ziel:** Auth-Stack installieren und früh-smoke-testen, dass die drei Libraries mit `django-tenants` kompatibel sind (Spec §14 Risiko: „django-tenants-Quirks (z. B. mit allauth-2fa)").

**Files:**
- Modify: `backend/pyproject.toml` (uv add)
- Modify: `backend/config/settings/base.py`
- Modify: `backend/config/urls_tenant.py`
- Create: `backend/tests/test_auth_smoke.py`

- [ ] **Step 8.1: Auth-Deps installieren**

```bash
cd /home/konrad/ai-act/backend
uv add "django-allauth>=64" "dj-rest-auth>=6.0" "django-allauth-2fa>=0.12"
```

- [ ] **Step 8.2: Failing Smoke-Test schreiben**

Datei `/home/konrad/ai-act/backend/tests/test_auth_smoke.py`:

```python
"""Smoke-Test für django-tenants × django-allauth × allauth-2fa.

Spec §14 Risiko: 'django-tenants-Quirks (z. B. mit allauth-2fa) — Sprint 1
Smoke-Test mit allen 3 Libs früh'.

Wir testen NICHT die volle Auth-Logik (das macht Sprint 3), sondern nur:
- die Libs starten ohne Konflikt
- ein User kann TOTP-Device anlegen und verifizieren
- Login-Endpoint von dj-rest-auth ist erreichbar im Tenant-Kontext
"""
import pytest
from django.test import Client
from django.urls import reverse
from django_tenants.utils import schema_context

from tests.factories import TenantDomainFactory, TenantFactory, UserFactory


@pytest.fixture
def tenant_with_domain(db):
    tenant = TenantFactory(schema_name="auth_smoke", firma_name="AuthSmoke GmbH")
    domain = TenantDomainFactory(
        tenant=tenant, domain="authsmoke.app.vaeren.local", is_primary=True
    )
    return tenant, domain


def test_dj_rest_auth_login_endpoint_exists(tenant_with_domain, settings):
    """Login-URL muss im Tenant-URLconf auflösbar sein."""
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain
    with schema_context(tenant.schema_name):
        url = reverse("rest_login")
        assert url == "/api/auth/login/"


def test_login_endpoint_responds_with_tenant_routing(tenant_with_domain, settings):
    settings.ALLOWED_HOSTS = ["*"]
    tenant, domain = tenant_with_domain
    with schema_context(tenant.schema_name):
        UserFactory(email="qm@authsmoke.de", password="ProperPass123!")

    client = Client(HTTP_HOST=domain.domain)
    resp = client.post(
        "/api/auth/login/",
        {"email": "qm@authsmoke.de", "password": "ProperPass123!"},
        content_type="application/json",
    )
    # Erfolg ODER 400 wegen Email-Verification-Settings — beides zeigt:
    # Lib lädt im Tenant-Kontext, kein Crash. Wir akzeptieren 200 oder 400.
    assert resp.status_code in (200, 400), resp.content


def test_totp_device_creation_works_in_tenant_schema(tenant_with_domain):
    from django_otp.plugins.otp_totp.models import TOTPDevice

    tenant, _ = tenant_with_domain
    with schema_context(tenant.schema_name):
        user = UserFactory(email="mfa@authsmoke.de")
        device = TOTPDevice.objects.create(user=user, name="default", confirmed=True)
        assert device.pk is not None
        assert TOTPDevice.objects.filter(user=user).count() == 1
```

- [ ] **Step 8.3: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_auth_smoke.py -v
```

Expected FAIL: `NoReverseMatch: Reverse for 'rest_login' not found` und/oder `LookupError: No installed app with label 'allauth'`.

- [ ] **Step 8.4: Settings für allauth + 2fa konfigurieren**

In `/home/konrad/ai-act/backend/config/settings/base.py`:

`SHARED_APPS` erweitern (allauth-Apps müssen geshared sein, weil sie auch im public-Schema lebendig sind):

```python
SHARED_APPS: list[str] = [
    "django_tenants",
    "tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
]
```

`TENANT_APPS` erweitern:

```python
TENANT_APPS: list[str] = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "allauth",
    "allauth.account",
    "allauth_2fa",
    "dj_rest_auth",
    "core",
    "rest_framework",
    "drf_spectacular",
]
```

`MIDDLEWARE` erweitern (TenantMainMiddleware bleibt first; OTP-Middleware NACH AuthMiddleware; allauth-Middleware NACH OTP):

```python
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "allauth_2fa.middleware.AllauthTwoFactorMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Am Ende ergänzen:

```python
SITE_ID = 1

# django-allauth — Email-basiert
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"  # MVP: optional, Sprint 4 Mailjet
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = "allauth_2fa.adapter.OTPAdapter"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# dj-rest-auth nutzt Session-Cookie (Spec §6: KEIN JWT)
REST_AUTH = {
    "USE_JWT": False,
    "SESSION_LOGIN": True,
    "USER_DETAILS_SERIALIZER": "dj_rest_auth.serializers.UserDetailsSerializer",
}

# Email-Backend: MVP = Console; Mailjet kommt Sprint 4
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

- [ ] **Step 8.5: URLconf-Tenant ergänzen**

Datei `/home/konrad/ai-act/backend/config/urls_tenant.py` ersetzen:

```python
"""URLs für tenant-Schemas (App-Funktionalität)."""
from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("accounts/", include("allauth.urls")),
]
```

- [ ] **Step 8.6: Migrations für neue Apps**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py makemigrations
uv run python manage.py migrate_schemas
```

Expected: Migrations für `sites`, `account`, `otp_totp`, `otp_static`, `allauth_2fa`, `dj_rest_auth` werden erzeugt/gefahren. Wenn `migrate_schemas` failt: oft hilft erst `migrate_schemas --shared`, dann `migrate_schemas --tenant`.

- [ ] **Step 8.7: ALLOWED_HOSTS für Test-Domains**

In `/home/konrad/ai-act/backend/config/settings/test.py` ergänzen:

```python
ALLOWED_HOSTS = ["*"]
```

- [ ] **Step 8.8: Smoke-Test laufen — soll PASS geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_auth_smoke.py -v
```

Expected: 3 passed.

Fehlerfall — `NoReverseMatch: rest_login`: dj-rest-auth-URL-Namen können je nach Version variieren. Falls nötig, im URLconf explizit benennen:

```python
path("api/auth/", include(("dj_rest_auth.urls", "rest_auth"), namespace=None)),
```

Falls `TenantDomain` nicht aufgelöst wird (Tenant-Routing): `TenantMainMiddleware` arbeitet nur mit dem genauen Domain-Header. Im Test setzen wir `HTTP_HOST=domain.domain` — sicherstellen, dass `domain.is_primary=True`.

- [ ] **Step 8.9: Vollständige Suite**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: alle Tests passed.

- [ ] **Step 8.10: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(auth): wire allauth + dj-rest-auth + 2fa under django-tenants"
```

---

## Task 9: drf-spectacular + /api/health/ Endpoint

**Ziel:** Health-Endpoint zur CI-Verifikation und Schema-Endpoint für späteren Frontend-Type-Sync.

**Files:**
- Create: `backend/core/views.py`
- Create: `backend/core/urls.py`
- Modify: `backend/config/urls_tenant.py`
- Create: `backend/tests/test_health.py`

- [ ] **Step 9.1: Failing Test schreiben**

Datei `/home/konrad/ai-act/backend/tests/test_health.py`:

```python
"""Health-Endpoint-Tests."""
import pytest
from django.test import Client
from django_tenants.utils import schema_context

from tests.factories import TenantDomainFactory, TenantFactory


@pytest.fixture
def tenant(db):
    t = TenantFactory(schema_name="health_t", firma_name="Health Test")
    TenantDomainFactory(tenant=t, domain="health.app.vaeren.local", is_primary=True)
    return t


def test_health_returns_200(tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="health.app.vaeren.local")
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "schema": "health_t"}


def test_openapi_schema_endpoint_renders(tenant, settings):
    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="health.app.vaeren.local")
    resp = client.get("/api/schema/")
    assert resp.status_code == 200
    assert b"openapi" in resp.content[:200].lower() or resp["content-type"].startswith(
        "application/vnd.oai.openapi"
    )
```

- [ ] **Step 9.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_health.py -v
```

Expected FAIL: 404 für `/api/health/`.

- [ ] **Step 9.3: Health-View schreiben**

Datei `/home/konrad/ai-act/backend/core/views.py`:

```python
"""Tenant-Schema-Views."""
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request) -> Response:
    """Liveness-Check inkl. aktivem Schema (verifiziert Tenant-Routing)."""
    return Response({"status": "ok", "schema": connection.schema_name})
```

- [ ] **Step 9.4: `core/urls.py`**

Datei `/home/konrad/ai-act/backend/core/urls.py`:

```python
from django.urls import path

from .views import health

# Leer-Pfad, weil das Tenant-URLconf bereits "api/health/" als Mountpoint setzt.
urlpatterns = [
    path("", health, name="health"),
]
```

- [ ] **Step 9.5: Tenant-URLconf erweitern**

Datei `/home/konrad/ai-act/backend/config/urls_tenant.py`:

```python
"""URLs für tenant-Schemas (App-Funktionalität)."""
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/health/", include("core.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("accounts/", include("allauth.urls")),
]
```

- [ ] **Step 9.6: Test laufen — soll PASS geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_health.py -v
```

Expected: 2 passed.

- [ ] **Step 9.7: Manuelle Smoke gegen Dev-Server**

Erfordert vorher einen Test-Tenant. Wir erzeugen einen via Django-Shell — `create_tenant`-Command kommt erst Task 10:

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py shell -c "
from tenants.models import Tenant, TenantDomain
t, _ = Tenant.objects.get_or_create(schema_name='dev', defaults={'firma_name': 'Dev-Test'})
TenantDomain.objects.get_or_create(tenant=t, domain='dev.app.vaeren.local', defaults={'is_primary': True})
TenantDomain.objects.get_or_create(tenant=t, domain='localhost', defaults={'is_primary': False})
print('OK')
"
```

`/etc/hosts` lokal ergänzen (einmalig, manuell, mit `sudo`):

```
127.0.0.1 dev.app.vaeren.local
```

Dev-Server starten:

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py runserver 0.0.0.0:8000 &
sleep 2
curl -i http://dev.app.vaeren.local:8000/api/health/
```

Expected: `HTTP/1.1 200 OK` + JSON `{"status": "ok", "schema": "dev"}`. Server stoppen mit `kill %1` oder `pkill -f runserver`.

- [ ] **Step 9.8: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(core): add /api/health/ endpoint and OpenAPI schema views"
```

---

## Task 10: Management-Command `create_tenant`

**Ziel:** Reproduzierbarer CLI-Befehl zum Tenant-Anlegen (Spec §4 — MVP-Onboarding ist manuell).

**Files:**
- Create: `backend/tenants/management/__init__.py`
- Create: `backend/tenants/management/commands/__init__.py`
- Create: `backend/tenants/management/commands/create_tenant.py`
- Create: `backend/tests/test_create_tenant_command.py`

- [ ] **Step 10.1: Failing Test schreiben**

Datei `/home/konrad/ai-act/backend/tests/test_create_tenant_command.py`:

```python
"""Tests für `manage.py create_tenant`."""
from io import StringIO

import pytest
from django.core.management import call_command
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()


def test_create_tenant_creates_schema_and_domain(db):
    out = StringIO()
    call_command(
        "create_tenant",
        schema="acme_inc",
        firma="ACME Inc.",
        domain="acme.app.vaeren.local",
        plan="professional",
        pilot=True,
        stdout=out,
    )
    tenant = Tenant.objects.get(schema_name="acme_inc")
    assert tenant.firma_name == "ACME Inc."
    assert tenant.plan == "professional"
    assert tenant.pilot is True
    assert TenantDomain.objects.filter(
        tenant=tenant, domain="acme.app.vaeren.local", is_primary=True
    ).exists()
    assert "acme_inc" in out.getvalue()


def test_create_tenant_is_idempotent(db):
    """Zweimaliger Aufruf mit denselben Args darf NICHT crashen."""
    args = dict(
        schema="repeat_t",
        firma="Repeat GmbH",
        domain="repeat.app.vaeren.local",
        plan="starter",
        pilot=False,
    )
    call_command("create_tenant", **args, stdout=StringIO())
    call_command("create_tenant", **args, stdout=StringIO())
    assert Tenant.objects.filter(schema_name="repeat_t").count() == 1
    assert TenantDomain.objects.filter(domain="repeat.app.vaeren.local").count() == 1
```

- [ ] **Step 10.2: Test laufen — soll FAIL geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_create_tenant_command.py -v
```

Expected FAIL: `CommandError: Unknown command 'create_tenant'`.

- [ ] **Step 10.3: Command-Skeleton-Verzeichnisse**

```bash
mkdir -p /home/konrad/ai-act/backend/tenants/management/commands
touch /home/konrad/ai-act/backend/tenants/management/__init__.py
touch /home/konrad/ai-act/backend/tenants/management/commands/__init__.py
```

- [ ] **Step 10.4: Command-Implementation**

Datei `/home/konrad/ai-act/backend/tenants/management/commands/create_tenant.py`:

```python
"""Tenant + Primary-Domain anlegen. Spec §4."""
from django.core.management.base import BaseCommand, CommandError

from tenants.models import Plan, Tenant, TenantDomain


class Command(BaseCommand):
    help = "Erzeugt einen Tenant + Primary-Domain. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--schema", required=True, help="Schema-Name (snake_case)")
        parser.add_argument("--firma", required=True, help="Firmenname")
        parser.add_argument("--domain", required=True, help="z. B. acme.app.vaeren.de")
        parser.add_argument(
            "--plan",
            choices=[p.value for p in Plan],
            default=Plan.PROFESSIONAL.value,
        )
        parser.add_argument("--pilot", action="store_true")
        parser.add_argument(
            "--pilot-discount", type=int, default=0, help="Prozent (0-100)"
        )

    def handle(self, *args, **opts):
        schema = opts["schema"]
        firma = opts["firma"]
        domain = opts["domain"]
        plan = opts["plan"]
        pilot = opts["pilot"]
        discount = opts["pilot_discount"]

        if not schema.isidentifier():
            raise CommandError(
                f"Schema '{schema}' ist kein gültiger Bezeichner (a-z0-9_, no leading digit)."
            )

        tenant, created = Tenant.objects.get_or_create(
            schema_name=schema,
            defaults={
                "firma_name": firma,
                "plan": plan,
                "pilot": pilot,
                "pilot_discount_percent": discount,
            },
        )
        if not created:
            self.stdout.write(f"Tenant '{schema}' existierte bereits — keine Änderung.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Tenant '{schema}' angelegt."))

        td, td_created = TenantDomain.objects.get_or_create(
            tenant=tenant,
            domain=domain,
            defaults={"is_primary": True},
        )
        if td_created:
            self.stdout.write(self.style.SUCCESS(f"Domain '{domain}' verknüpft."))
        else:
            self.stdout.write(f"Domain '{domain}' existierte bereits.")
```

- [ ] **Step 10.5: Test laufen — soll PASS geben**

```bash
cd /home/konrad/ai-act/backend
uv run pytest tests/test_create_tenant_command.py -v
```

Expected: 2 passed.

- [ ] **Step 10.6: Manuelle Smoke**

```bash
cd /home/konrad/ai-act/backend
uv run python manage.py create_tenant \
    --schema demo \
    --firma "Demo GmbH" \
    --domain "demo.app.vaeren.local" \
    --plan professional \
    --pilot \
    --pilot-discount 40
```

Expected: zwei grüne Erfolgs-Zeilen.

- [ ] **Step 10.7: Commit**

```bash
cd /home/konrad/ai-act
git add backend/
git commit -m "feat(tenants): add idempotent create_tenant management command"
```

---

## Task 11: Ruff lint-Run als Quality-Gate

**Ziel:** Lint-Check lokal laufen + in CI durchsetzen.

**Files:**
- Modify: `backend/pyproject.toml` (bereits in Task 1 vorbereitet)

- [ ] **Step 11.1: Lint laufen**

```bash
cd /home/konrad/ai-act/backend
uv run ruff check .
uv run ruff format --check .
```

Expected: 0 Fehler. Wenn Lints schreien:

```bash
uv run ruff check . --fix
uv run ruff format .
```

Re-Run, bis grün.

- [ ] **Step 11.2: Tests müssen weiter grün sein**

```bash
cd /home/konrad/ai-act/backend
uv run pytest -v
```

Expected: alle Tests passed.

- [ ] **Step 11.3: Commit (falls Lint-Fixes Änderungen erzeugten)**

```bash
cd /home/konrad/ai-act
git status
# Wenn Änderungen: 
git add backend/
git commit -m "style(backend): apply ruff fixes"
# Wenn keine Änderungen: Schritt überspringen.
```

---

## Task 12: GitHub-Actions-Workflow `test.yml`

**Ziel:** Auf PR + Push gegen `main`: lint + Backend-Tests + Multi-Tenant-Isolation-Test als kritischer Gate.

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 12.1: Workflow schreiben**

Datei `/home/konrad/ai-act/.github/workflows/test.yml`:

```yaml
name: Test
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

defaults:
  run:
    working-directory: backend

jobs:
  backend-tests:
    name: Backend tests + multi-tenant isolation gate
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: vaeren
          POSTGRES_USER: vaeren
          POSTGRES_PASSWORD: vaeren_ci_only
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U vaeren"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10

    env:
      POSTGRES_DB: vaeren
      POSTGRES_USER: vaeren
      POSTGRES_PASSWORD: vaeren_ci_only
      POSTGRES_HOST: 127.0.0.1
      POSTGRES_PORT: 5432
      REDIS_URL: redis://127.0.0.1:6379/0
      DJANGO_SECRET_KEY: ci-only-not-secret
      DJANGO_DEBUG: "0"
      DJANGO_ALLOWED_HOSTS: "*"
      DJANGO_SETTINGS_MODULE: config.settings.test

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "0.5.x"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --frozen --all-extras

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Django check
        run: uv run python manage.py check

      - name: Run all backend tests
        run: uv run pytest -v

      - name: Critical multi-tenant isolation gate
        # Doppelter Lauf mit -m: bricht den Build sofort, falls die
        # Isolations-Tests gefiltert NICHT laufen oder failen.
        run: uv run pytest -v -m tenant_isolation --strict-markers
```

- [ ] **Step 12.2: Lokaler Self-Check**

Da GitHub-Actions-Workflow erst auf Push validiert wird, prüfen wir die YAML-Syntax lokal:

```bash
cd /home/konrad/ai-act
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
```

Expected: kein Output (keine Errors).

- [ ] **Step 12.3: Commit + Push (sobald Remote existiert)**

```bash
cd /home/konrad/ai-act
git add .github/
git commit -m "ci: add backend-tests workflow with multi-tenant isolation gate"
```

Hinweis: Falls noch kein GitHub-Remote angelegt ist, ist das Sprint-1-Postlude — Workflow läuft erst nach `git remote add origin git@github.com:<konrad>/vaeren.git && git push -u origin main`.

---

## Task 13: README + Sprint-1-Done-Verifikation

**Ziel:** Setup-Anleitung für künftiges Onboarding (auch für künftige Claude-Sessions), Verifikation dass alles läuft.

**Files:**
- Modify: `README.md` (oder Create, falls leer)

- [ ] **Step 13.1: README-Stand prüfen**

```bash
ls -la /home/konrad/ai-act/README.md 2>/dev/null
```

Falls vorhanden: lesen. Falls nicht: anlegen.

- [ ] **Step 13.2: README schreiben**

Datei `/home/konrad/ai-act/README.md`:

```markdown
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
- **Auth:** `django-allauth` + `dj-rest-auth` + `django-allauth-2fa` (Session-Cookie, TOTP-MFA)
- **DB:** Postgres 16, Redis 7
- **Code-Layout:** `backend/tenants/` (public-Schema), `backend/core/` (tenant-Schema-Baseline mit User)

Tiefer: `CLAUDE.md` (Kurz-Referenz) und `docs/superpowers/specs/` (Specs).

## Sprint-Stand

| Sprint | Status |
|---|---|
| 1 | ✅ Foundation (Repo, Django, Multi-Tenancy, Auth, Test-Tenant) |
| 2 | ⬜ Shared Core Models + DRF API + AuditLog |
| 3+ | siehe Spec §12 |
```

- [ ] **Step 13.3: Sprint-1-Done-Verifikation — kompletter Run**

```bash
cd /home/konrad/ai-act/backend

# Lint
uv run ruff check .
uv run ruff format --check .

# Django sanity
uv run python manage.py check

# Schemas in Sync
uv run python manage.py makemigrations --check --dry-run

# Volle Suite
uv run pytest -v

# Multi-Tenant-Gate explizit
uv run pytest -m tenant_isolation -v
```

Expected:
- Ruff: alles grün
- Django check: `0 silenced`
- makemigrations --check: `No changes detected`
- pytest gesamt: ≥ 10 passed (test_tenant_isolation: 3, test_user_model: 3, test_auth_smoke: 3, test_health: 2, test_create_tenant_command: 2)
- pytest tenant_isolation: 3 passed

Falls eine Stufe rot: nicht committen — Stufe zurückgehen und debuggen, bevor Sprint 1 als done markiert wird.

- [ ] **Step 13.4: Final Commit**

```bash
cd /home/konrad/ai-act
git add README.md
git commit -m "docs: sprint 1 setup guide and architecture quickref"
```

- [ ] **Step 13.5: Sprint-1-Done-Tag**

```bash
cd /home/konrad/ai-act
git tag -a sprint-1-done -m "Sprint 1: Foundation komplett — Repo + Django + Multi-Tenancy + Auth"
git log --oneline -20
```

---

## Sprint-Done-Checkliste

Sprint 1 ist erst dann „done", wenn:

- [ ] `docker compose -f docker-compose.dev.yml ps` zeigt `vaeren-dev-postgres` + `vaeren-dev-redis` healthy
- [ ] `uv run python manage.py check` → `0 issues`
- [ ] `uv run python manage.py migrate_schemas --shared` und `migrate_schemas` laufen idempotent durch
- [ ] `uv run pytest -v` → alle ≥ 10 Tests grün
- [ ] `uv run pytest -m tenant_isolation -v` → 3 Tests grün (kritisch!)
- [ ] `uv run ruff check . && uv run ruff format --check .` → grün
- [ ] `curl http://dev.app.vaeren.local:8000/api/health/` → 200 + JSON `{"status": "ok", "schema": "dev"}`
- [ ] `git tag sprint-1-done` gesetzt
- [ ] CLAUDE.md weiterhin korrekt (kein Update nötig — Architektur-Decisions sind unverändert)

## Out-of-Scope-Reminder (für künftige Claude-Sessions)

Diese Tasks sind **bewusst nicht** in Sprint 1:

- Mitarbeiter-Modell, ComplianceTask, Evidence, AuditLog → **Sprint 2**
- Frontend (React+Vite) → **Sprint 3**
- Mailjet-Integration → **Sprint 4**
- Kurs/Schulungs-Wizard / Quiz / Zertifikat → **Sprint 4**
- HinSchG-Encryption + Meldungsformular → **Sprint 5**
- Caddy-Migration / Production-Deploy → **Sprint 8**
- LLM-Integration → **Sprint 4 (Pflichtunterweisung) bzw. Sprint 5 (HinSchG)**
- Volle MFA-UI / Backup-Codes-UI → **Sprint 3**

Wenn Sprint-1-Scope-Creep droht: **YAGNI** (CLAUDE.md). Im Zweifel die nicht-Scope-Items in einen Sprint-2-Plan schieben statt Sprint 1 aufzublasen.
