# CLAUDE.md — Projekt-Anweisungen für Claude

> **Für künftige Claude-Sessions:** Diese Datei enthält die wichtigsten Architektur- und Konventions-Entscheidungen für das ai-act-Projekt. Sie ist die schnelle Referenz; die tiefe Wahrheit liegt in den Specs unter `docs/superpowers/specs/`.

## Projekt-Kurzbeschreibung

**ai-act** = SaaS „Compliance-Autopilot für den Industrie-Mittelstand".
Slogan: *„Wir übernehmen die Pflichten, ihr macht Produktion."*
Solo-Bootstrap von Konrad Bizer parallel zu seiner PayWise-Tätigkeit.

**Zielgruppe:** Industrie-Mittelstand DE (Maschinenbau, Metallverarbeitung, Kunststoff, Automotive-Zulieferer), 50–300 MA.
**MVP-Module:** Compliance-Dashboard + Pflichtunterweisungs-Suite + HinSchG-Hinweisgeberportal.

## Kanonische Referenz-Dokumente

Bei Unsicherheit immer zuerst hier nachsehen:

1. `docs/superpowers/specs/2026-04-24-icp-and-launch-story-design.md` — ICP, Personas, Pricing, Launch-Story, GTM, Risiken
2. `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md` — Tech-Stack, Datenmodell, Auth, Integrationen, LLM, Deployment, Tests, Sprint-Plan
3. `docs/superpowers/plans/2026-04-24-gtm-90-day-plan.md` — 90-Tage-Aktionsplan für Markt-Validierung & GTM
4. `infrastructure/README.md` — Server-Doku (Hetzner CAX31 ARM64 Helsinki, Co-Location mit Sponty)

## Tech-Stack (gefroren)

- **Backend:** Python 3.12 + Django 5 LTS + DRF + django-tenants (schema-per-tenant) + Celery + Redis + Postgres 16
- **Frontend:** React 18 + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query + Zustand + React Router 7
- **Auth:** django-allauth + dj-rest-auth + django-otp (TOTP-MFA aus dem MVP — `django-allauth-2fa` ist abandoned + inkompatibel mit allauth>=64, deshalb der Substitution), Session-Cookies KEIN JWT
- **Package-Manager:** `uv` (Python), `bun` (JS) — beide schneller als pip/npm, deterministische Lockfiles
- **Linting:** Ruff (Python), Biome oder ESLint (JS)
- **LLM:** OpenRouter als Provider-Aggregator (gleich wie Sponty), MVP-Defaults: `google/gemini-2.5-flash:free` (Fast) + `mistralai/mistral-small-3.2:free` (Reasoning). Migrations-Pfad zu Anthropic Claude in Phase 2.
- **Mail:** Mailjet via django-anymail
- **Storage:** Lokales Docker-Volume `ai-act-media` (NICHT S3 im MVP), Migrationspfad zu S3 dokumentiert
- **Hosting:** Hetzner CAX31 ARM64 Helsinki, co-located mit Sponty unter `/opt/ai-act/`. Caddy als zentraler Reverse-Proxy
- **Backup:** restic zu Hetzner Storage Box, daily, retention 7d/4w/12m
- **Monitoring:** Sentry EU-Region

## Nicht-verhandelbare Architektur-Regeln

1. **RDG-Schutz (3 Layer):** Jeder LLM-Output, der rechtliche Bewertung enthält, durchläuft (a) System-Prompt mit Vorschlags-Sprache-Erzwingung, (b) Output-Validator gegen verbotene Formeln, (c) Human-in-the-Loop-Gate vor jeder Wirkung. **Keine LLM-Klassifizierung wird je ohne Mensch-Bestätigung produktiv.** Verstoß → existenzielles Risiko für die Firma.
2. **Multi-Tenant-Isolation:** Jede HTTP-Anfrage MUSS via `django-tenants`-Middleware ein konkretes Schema setzen. Cross-Tenant-Queries sind verboten. Multi-Tenant-Isolation-Test ist kritischer CI-Gate — Build failed sonst.
3. **HinSchG-Verschlüsselung:** Inhalt von Whistleblower-Meldungen MUSS via `django-cryptography` AES-256-at-Rest verschlüsselt werden. Klartext nur via Application-Layer mit Tenant-Schlüssel sichtbar.
4. **Niemals API-Keys im Repo:** `.env*`-Files sind in `.gitignore`. Production-Secrets via `.env.production` lokal + `scp` aufs Deployment.
5. **Niemals echte LLM/Mail-Calls in Tests:** Mocking ist Pflicht (responses-lib für HTTP, mock für SDK).
6. **Audit-Log-Immutability:** `Evidence.immutable=True` und `AuditLog`-Einträge dürfen niemals nachträglich verändert werden. Manipulationsschutz via SHA-256 + Append-Only-Pattern.

## Coding-Konventionen

- **Domain-Driven Boundaries:** Module (`pflichtunterweisung/`, `hinschg/`, `core/`) rufen sich nur über Domain-Service-Schnittstellen auf, nicht über direkte Model-Imports cross-module
- **Single-Responsibility pro Datei:** wenn `views.py` >300 Zeilen → splitten
- **Type-Safety End-to-End:** Backend-API-Schema (drf-spectacular) → Frontend-Types (openapi-typescript). Backend-Bruch ohne Frontend-Update = TypeScript-Build-Fehler. CI-Pflicht.
- **YAGNI ruthlessly:** Keine Features bauen, bis Pilot-Kunden sie verlangen. Keine Mocks für Hypothesen.
- **Tests-First für kritische Pfade:** Multi-Tenant-Isolation, Frist-Berechnungen, RDG-Layer-2 (Output-Validator), Permission-Tests.

## 4-Schichten-Test-Strategie (Pflicht-Coverage)

1. **API-Integration-Tests** (pytest-django, 90% Coverage Business-Logic) — Hauptbollwerk gegen Regression
2. **OpenAPI-Schema-Sync** in CI — automatischer Contract-Schutz
3. **Storybook + Interaction-Tests** für UI-Logic ohne Browser
4. **Playwright** sparsam (8 kritische User-Journeys), nur auf main-Branch

**Anti-Patterns:**
- ❌ Echte LLM/Mail-API-Calls in Tests
- ❌ Snapshot-Tests für komplexe UIs
- ❌ Parallele „Test-Endpoints" neben echten Endpoints (verfälscht Coverage)

## Deployment

- **Pattern:** rsync + scp + docker compose up (analog Sponty `deploy.sh`)
- **Build:** server-side ARM64-native (kein Cross-Compile)
- **Trigger:** **manuell** durch `./deploy.sh` von Konrads Laptop. **Kein Auto-Deploy in CI** (bewusste Entscheidung — weniger Risiko, weniger Secrets in CI)
- **Migrations:** `migrate_schemas --noinput` im Container-CMD vor Daphne-Start. Migrations müssen rückwärtskompatibel sein
- **Reverse-Proxy:** Caddy 2 als Host-Service (NICHT Container), belegt Port 80/443, routet sponty-Domains und ai-act-Domains

## LLM-Strategy für Code-Generierung (Konrad-Workflow)

- **Konrad ist Architekt, Claude generiert Code.** Aber: Konrad muss generierten Code **lesen + verstehen + im Notfall ändern** können. Stack ist deshalb auf seine Stärken (Django, Python, TypeScript) optimiert.
- Beim Generieren von Code: bestehende Dateien ergänzen statt neue zu erfinden. `panels/_base.py`-Pattern aus `paywise-dashboard` ist Inspiration für modulare Erweiterung.
- Code-Reviews durch Konrad sind ernst zu nehmen — wenn er „warum so" fragt, ist es eine echte Frage, nicht rhetorisch.

## Sprint-Plan & Aktueller Stand

8-Wochen-MVP-Plan in `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md` §12.

Aktueller Stand (Stand 2026-04-24): **Planungs-Phase abgeschlossen.** Pre-Sprint-1 Prerequisites laufen (Naming-Session, Account-Setups). Code-Start nach Naming-Entscheidung.

## Wichtige Quervernetzungen mit anderen Projekten

- **Sponty-Repo (`/home/konrad/sponty/`):** Dient als Vorbild für Docker-Compose-Pattern, deploy.sh, OpenRouter-LLM-Config, ARM64-Build. Co-Location auf demselben Server.
- **paywise-dashboard:** Architektur-Inspiration für Plugin-Pattern (`panels/_base.py`, BasePanel-Interface, Auto-Discovery). NICHT direkt-Code-übernehmen wegen Arbeitgeber-IP.

## Kommunikations-Konventionen mit Konrad

- **Sprache:** Deutsch. Code/Code-Comments können englisch sein (üblich), User-facing Strings sind deutsch (de-DE).
- **Direktheit:** Konrad will kritische Rückfragen statt Jasager-Antworten. Wenn eine Idee suboptimal ist, klar sagen warum, mit Alternative.
- **Compliance-Domain-Wissen:** Konrad ist Compliance-Neuling — Abkürzungen und Fachbegriffe immer kurz erklären. Glossar in `~/.claude/projects/-home-konrad-ai-act/memory/glossar_compliance.md`.
- **YAGNI über Premature-Optimization:** Konrad neigt zu Scope-Erweiterungen — diese kritisch hinterfragen, nicht blind übernehmen.

## Produktname

**Vaeren** (finalisiert in Naming-Session 2026-04-27, siehe `docs/superpowers/specs/2026-04-27-naming-decision-vaeren.md`).

- Schreibung Marketing/Logo: **Vaeren** (Initial-Capital)
- Schreibung Code/Domain: `vaeren` (alles klein)
- Hauptdomain: `vaeren.de` (registriert bei Hetzner, 4,90 €/Jahr Auto-Renewal)
- DNS: Hetzner DNS Console (`dns.hetzner.com`)
- DNS-Records gesetzt: `@`, `app`, `*.app`, `hinweise`, `www` → 204.168.159.236
- `.com` bewusst NICHT im MVP-Scope (Squatter; Phase-3-Ziel)

**Markenrechts-TODO vor Pilot-Kunden-Vertrag:** anwaltliche DPMA-Recherche + DPMA-Wortmarken-Anmeldung Klassen 9, 35, 42 (~290 € + Anwaltsgebühr).
