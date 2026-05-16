# Marketing-Site Plan 3: Caddy-Routing + Deploy-Integration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `vaeren.de` und `www.vaeren.de` schwenken von App-Redirect auf statischen Marketing-Site-Serve. `api.vaeren.de` wird als neue öffentliche API-Subdomain etabliert, die die Marketing-Site (und perspektivisch andere Public-Clients) bedient. `deploy.sh` baut das Marketing-Projekt mit + rsynct Output auf den Server.

**Architecture:** Marketing-Build läuft auf Konrads Laptop vor dem Deploy (Node/bun-frei auf dem Server). `marketing/dist/` wird per rsync ins server-seitige `/var/www/vaeren-marketing/` gespiegelt. Caddy (Host-Service) serviert es per `file_server`. Eine neue TenantDomain `api.vaeren.de` mapped auf das Public-Schema, sodass `https://api.vaeren.de/api/public/news/` direkt erreichbar ist.

**Tech Stack:** Caddy 2 (Host-systemd), Astro statisch, django-tenants Domain-Routing.

---

## File Structure

```
ai-act/
├─ deploy.sh                        # Modify: Marketing-Build + rsync
├─ infrastructure/
│  └─ Caddyfile                     # Modify: vaeren.de file_server, neuer api.vaeren.de Block
├─ marketing/
│  └─ .env.example                  # NEW: PUBLIC_API_BASE-Beispiel
└─ backend/
   └─ tenants/management/commands/
      └─ ensure_public_domains.py   # NEW: idempotente Pflege der public-TenantDomains
```

---

## Voraussetzungen (Konrad-Aufgaben außerhalb Code)

- [ ] **DNS A-Record `api.vaeren.de` → 204.168.159.236** in der Hetzner-DNS-Konsole. ~15 Min Propagation.
- [ ] **`/var/www/vaeren-marketing/`** auf dem Server anlegen: `ssh root@204.168.159.236 'mkdir -p /var/www/vaeren-marketing && chown caddy:caddy /var/www/vaeren-marketing'`.

## Task 1: Marketing-Build-Konfiguration (PUBLIC_API_BASE)

- [ ] **Step 1:** `marketing/.env.example` schreiben:

  ```bash
  # Marketing-Site Build-Env. Pro Umgebung anders.
  # Dev:  PUBLIC_API_BASE=http://localhost:8000
  # Prod: PUBLIC_API_BASE=https://api.vaeren.de
  PUBLIC_API_BASE=http://localhost:8000
  ```

- [ ] **Step 2:** `marketing/.gitignore` ergänzen um `.env` (sollte schon dort sein durch Astro-Default — verifizieren).

- [ ] **Step 3:** Commit.

## Task 2: Public-TenantDomain Management-Command

Astro fetched Build-Zeitlich gegen `https://api.vaeren.de/api/public/news/`. Damit dieser Hostname auf das Public-Schema gemappt ist, muss eine TenantDomain im public-Schema existieren.

- [ ] **Step 1:** Datei schreiben `backend/tenants/management/commands/ensure_public_domains.py`:

  ```python
  """Stellt sicher, dass die public-Schema-TenantDomains konfiguriert sind.

  Domains, die public-only sind: hinweise.app.vaeren.de (HinSchG-Formular)
  und api.vaeren.de (Marketing-API). Idempotent.
  """
  from django.core.management.base import BaseCommand
  from django.db import transaction
  from django_tenants.utils import get_public_schema_name, schema_context

  from tenants.models import Tenant, TenantDomain

  PUBLIC_DOMAINS = [
      "hinweise.app.vaeren.de",
      "api.vaeren.de",
      # Dev:
      "localhost",
      "127.0.0.1",
  ]


  class Command(BaseCommand):
      help = "Registriert public-Schema-TenantDomains (idempotent)."

      def handle(self, *args, **options):
          public_schema = get_public_schema_name()
          with schema_context(public_schema):
              public_tenant, created = Tenant.objects.get_or_create(
                  schema_name=public_schema,
                  defaults={"firma_name": "Public", "plan": "public"},
              )
              if created:
                  self.stdout.write(self.style.WARNING(
                      f"Public-Tenant neu angelegt: {public_tenant.pk}"
                  ))
              for domain in PUBLIC_DOMAINS:
                  td, td_created = TenantDomain.objects.update_or_create(
                      domain=domain,
                      defaults={"tenant": public_tenant, "is_primary": False},
                  )
                  state = "neu" if td_created else "bestätigt"
                  self.stdout.write(f"  {domain} — {state}")
  ```

- [ ] **Step 2:** Smoke-Test schreiben `backend/tests/test_ensure_public_domains.py`:

  ```python
  import pytest
  from django.core.management import call_command

  from tenants.models import TenantDomain


  @pytest.mark.django_db
  def test_command_creates_required_public_domains():
      call_command("ensure_public_domains")
      assert TenantDomain.objects.filter(domain="api.vaeren.de").exists()
      assert TenantDomain.objects.filter(domain="hinweise.app.vaeren.de").exists()


  @pytest.mark.django_db
  def test_command_is_idempotent():
      call_command("ensure_public_domains")
      call_command("ensure_public_domains")
      assert TenantDomain.objects.filter(domain="api.vaeren.de").count() == 1
  ```

- [ ] **Step 3:** Lokal verifizieren via `manage.py check` (DB-Test braucht Docker).
- [ ] **Step 4:** Commit.

## Task 3: Caddyfile-Update

- [ ] **Step 1:** `infrastructure/Caddyfile` modifizieren:
  - Block `vaeren.de, www.vaeren.de` von `redir` umstellen auf `file_server` aus `/var/www/vaeren-marketing/`.
  - Neuen Block `api.vaeren.de` einfügen, der auf `vaeren-django:8000` proxied.
  - WWW → Apex Redirect (kanonisch).

  Konkret:

  ```caddyfile
  # --- Vaeren Marketing-Site --------------------------------------------
  www.vaeren.de {
      redir https://vaeren.de{uri} permanent
  }

  vaeren.de {
      encode gzip zstd
      root * /var/www/vaeren-marketing
      file_server
      try_files {path} {path}/index.html /404.html
      header /_astro/* Cache-Control "public, max-age=31536000, immutable"
      header / Cache-Control "public, max-age=600, must-revalidate"
      header X-Content-Type-Options "nosniff"
      header X-Frame-Options "DENY"
      header Referrer-Policy "strict-origin-when-cross-origin"
      header Permissions-Policy "geolocation=(), microphone=(), camera=()"
  }

  # --- Vaeren Public-API (für Marketing-Site + andere Clients) ----------
  api.vaeren.de {
      encode gzip zstd
      reverse_proxy vaeren-django:8000 {
          header_up X-Forwarded-Proto https
          header_up X-Real-IP {remote_host}
          header_up Host {host}
      }
  }
  ```

- [ ] **Step 2:** Commit.

## Task 4: Deploy-Skript erweitern (Marketing-Build + rsync)

- [ ] **Step 1:** `deploy.sh` modifizieren:
  - Vor dem Backend-rsync: `cd marketing && bun install --frozen-lockfile && PUBLIC_API_BASE=https://api.vaeren.de bun run build`
  - Nach dem Backend-rsync (Schritt 3): zusätzlicher rsync `marketing/dist/` → `${SERVER}:/var/www/vaeren-marketing/`
  - Nach dem Compose-up (Schritt 5): `ssh ${SERVER} 'cd ${REMOTE_DIR}/backend && docker compose exec vaeren-django python manage.py ensure_public_domains'`
  - Caddy reload: `ssh ${SERVER} 'systemctl reload caddy'`

  Genauer Diff in der Datei (siehe Task-5-Sektion in der Spec; Schritt-Nummerierung anpassen).

- [ ] **Step 2:** Lokal Smoke-Test: `bash -n deploy.sh` (Syntax-Check).
- [ ] **Step 3:** Commit.

## Task 5: Update `.env.production` (manuell, nicht im Repo)

- [ ] **Konrad-Aufgabe:** `DJANGO_ALLOWED_HOSTS` um `api.vaeren.de` ergänzen.
- [ ] **Konrad-Aufgabe:** `DJANGO_CSRF_TRUSTED_ORIGINS` braucht KEINE Ergänzung (GET-Endpoints, kein CSRF).

## Task 6: Deploy ausführen (Konrad-Aufgabe)

- [ ] **Step 1:** DNS-Record für `api.vaeren.de` setzen (Voraussetzungen).
- [ ] **Step 2:** Auf dem Server: `/var/www/vaeren-marketing/` anlegen + chown caddy.
- [ ] **Step 3:** Lokal `./deploy.sh` ausführen. Bei erstem Lauf läuft Build mit unreachable API (api.vaeren.de noch nicht bei Caddy registriert) — Site geht ohne News live.
- [ ] **Step 4:** Auf dem Server: `seed_redaktion` ausführen, damit Initial-Posts in der DB sind.
  ```bash
  ssh root@204.168.159.236 'cd /opt/ai-act && docker compose exec vaeren-django python manage.py seed_redaktion'
  ```
- [ ] **Step 5:** Re-Deploy: `./deploy.sh` — diesmal fetcht der Build die Initial-Posts korrekt.
- [ ] **Step 6:** Smoke-Test im Browser:
  - https://vaeren.de — Marketing-Site sichtbar
  - https://www.vaeren.de — redirected zu vaeren.de
  - https://api.vaeren.de/api/public/news/ — JSON mit 10 Posts
  - https://vaeren.de/news/ai-act-gpai-pflichten-2026 — News-Detail mit Quellen
  - https://app.vaeren.de — App-Login unverändert (Regression-Check)

## Abschluss

Plan 3 ist abgeschlossen, wenn vaeren.de live die Marketing-Site zeigt, api.vaeren.de die public-News-API ausliefert und app.vaeren.de unverändert funktioniert.
