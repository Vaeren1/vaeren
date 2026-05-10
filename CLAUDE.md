# CLAUDE.md — Projekt-Anweisungen für Claude

> **Für künftige Claude-Sessions:** Diese Datei enthält die wichtigsten Architektur- und Konventions-Entscheidungen für das ai-act-Projekt. Sie ist die schnelle Referenz; die tiefe Wahrheit liegt in den Specs unter `docs/superpowers/specs/`.

## Stand 2026-05-10 — Vaeren ist live in Production

8 Sprints abgeschlossen, MVP deployed auf Hetzner CAX31, 5 Live-Domains:

- `https://app.vaeren.de` — Vaeren-App-Login + Compliance-Cockpit
- `https://hinweise.app.vaeren.de` — anonymes HinSchG-Hinweisgeber-Form
- `https://errors.app.vaeren.de` — GlitchTip Error-Tracking (self-hosted)
- `https://vaeren.de` + `www.vaeren.de` — Apex-Redirect zu app

Demo-Tenant `demo` mit GF + CB + 3 Mitarbeiter + 1 SchulungsWelle SENT (1 erfolgreich) + 2 HinSchG-Meldungen (1 in Prüfung). Compliance-Index aktuell `89/100 yellow`.

**Aktive Integrationen:** Brevo (Mail), OpenRouter (LLM mit Gemma-4 26B), Hetzner Storage Box (restic daily), GlitchTip (Sentry-API self-hosted). Mailjet wurde versucht, schlug fehl (Anti-Abuse-Block bei fresh Account), Code-Pfad bleibt als Fallback. Vollständige Live-Konfiguration in `~/.claude/projects/-home-konrad-ai-act/memory/vaeren_production_state.md`.

**DPMA-Markenanmeldung:** vom User auf 2026-05-10 explizit postponed. Vor Pilot-Vertrag mit Anwalt prüfen.

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
- **LLM:** OpenRouter als Provider-Aggregator. **2026-Defaults (Stand 2026-05-10):** `google/gemma-4-26b-a4b-it:free` (Fast) + `nvidia/nemotron-3-super-120b-a12b:free` (Reasoning) — die ursprünglichen Spec-Modelle (`gemini-2.5-flash:free`, `mistral-small-3.2:free`) existieren nicht mehr im OpenRouter-Lineup. Override via env `OPENROUTER_MODEL_FAST` / `_REASONING`. Migrations-Pfad zu Anthropic Claude in Phase 2.
- **Mail:** **Brevo** via `django-anymail[brevo]` (300/Tag forever-free, EU-Hosting). Provider-Priorität in `prod.py`: Brevo > Mailjet > Console-Fallback. Mailjet ist code-mäßig vorhanden aber ein Anti-Abuse-Block des Free-Accounts beim ersten API-Call hat den Provider blockiert — durch Brevo ersetzt am 2026-05-09.
- **Storage:** Lokales Docker-Volume `vaeren-media` (NICHT S3 im MVP), Migrationspfad zu S3 dokumentiert
- **Hosting:** Hetzner CAX31 ARM64 Helsinki, co-located mit Sponty unter `/opt/ai-act/`. Caddy als zentraler Reverse-Proxy als **Container** in `/opt/caddy/` (NICHT Host-Service — anders als ursprünglich Spec, weil Container-DNS einfacher als systemd-resolver-Trick).
- **Backup:** **restic auf Hetzner Storage Box BX11** (`u591277.your-storagebox.de`, Falkenstein FSN1, 3,81 €/Mo). Daily 03:00 cron, retention 7d/4w/12m. Restore-verifiziert. **Wichtig:** Storage Box hört auf Port 23 (nicht 22), Pfad muss relativ sein (`vaeren-restic`, kein `/`-Prefix), SSH-Config (`/root/.ssh/config_vaeren_backup`) übernimmt Key+Port.
- **Monitoring:** **GlitchTip self-hosted** (Sentry-API-kompatibel) auf `errors.app.vaeren.de`, eigener Compose-Stack in `/opt/glitchtip/` mit eigenem Postgres+Redis. Vorteil ggü. Sentry-SaaS: Daten EU-side, kein Quota, kein Vendor-Lock.

## Nicht-verhandelbare Architektur-Regeln

1. **RDG-Schutz (3 Layer):** Jeder LLM-Output, der rechtliche Bewertung enthält, durchläuft (a) System-Prompt mit Vorschlags-Sprache-Erzwingung, (b) Output-Validator gegen verbotene Formeln, (c) Human-in-the-Loop-Gate vor jeder Wirkung. **Keine LLM-Klassifizierung wird je ohne Mensch-Bestätigung produktiv.** Verstoß → existenzielles Risiko für die Firma.
2. **Multi-Tenant-Isolation:** Jede HTTP-Anfrage MUSS via `django-tenants`-Middleware ein konkretes Schema setzen. Cross-Tenant-Queries sind verboten. Multi-Tenant-Isolation-Test ist kritischer CI-Gate — Build failed sonst.
3. **HinSchG-Verschlüsselung:** Inhalt von Whistleblower-Meldungen MUSS at-rest verschlüsselt werden. Implementierung: `core/fields.py::EncryptedTextField` mit `cryptography.fernet.Fernet` (AES-128-CBC + HMAC-SHA256), per-Tenant-Key aus `Tenant.encryption_key` (auto-generiert in `Tenant.save()`). **Spec sagt `django-cryptography`, das Paket ist aber abandoned** — eigene 80-Zeilen-Implementation auf `cryptography`-Lib stattdessen. Cross-Tenant-Decrypt ist mathematisch unmöglich + CI-Test-verifiziert.
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
- **Reverse-Proxy:** Caddy 2 als **Container** in `/opt/caddy/`, belegt Port 80/443, routet sponty-Domains + vaeren-Domains + glitchtip. Caddy hängt im `caddy-net`-Docker-Bridge mit allen Backends, daher direkt via Container-Name reachable. Spec sagte „Host-Service" — Container ist sauberer (Konfig in einem File pro Stack, kein systemd-DNS-Trick nötig).

## LLM-Strategy für Code-Generierung (Konrad-Workflow)

- **Konrad ist Architekt, Claude generiert Code.** Aber: Konrad muss generierten Code **lesen + verstehen + im Notfall ändern** können. Stack ist deshalb auf seine Stärken (Django, Python, TypeScript) optimiert.
- Beim Generieren von Code: bestehende Dateien ergänzen statt neue zu erfinden. `panels/_base.py`-Pattern aus `paywise-dashboard` ist Inspiration für modulare Erweiterung.
- Code-Reviews durch Konrad sind ernst zu nehmen — wenn er „warum so" fragt, ist es eine echte Frage, nicht rhetorisch.

## Sprint-Plan & Aktueller Stand

8-Wochen-MVP-Plan in `docs/superpowers/specs/2026-04-24-mvp-architecture-design.md` §12 — alle 8 Sprints abgeschlossen 2026-04-23 bis 2026-05-10.

| Sprint | Stand | Hauptergebnis |
|---|---|---|
| 1 | ✅ | Foundation: Repo + Django + Multi-Tenancy + Auth + Test-Tenant |
| 2 | ✅ | Shared Core (Mitarbeiter, ComplianceTask, Evidence, Notification, AuditLog) + DRF-API + django-rules + AuditLog-Auto-Population |
| 3 | ✅ | Frontend-Foundation (React + Login + MFA + Mitarbeiter-CRUD + Demo-Form, openapi-typescript-Pipeline, CI 3-Job) |
| 4 | ✅ | Pflichtunterweisung-Modul (Kurs/Welle/Wizard/Public-Quiz, LLM-Personalisierung mit RDG-Layer-2-Validator, WeasyPrint-Zertifikate) |
| 5 | ✅ | HinSchG (Per-Tenant-Fernet-Encryption, Meldung/Bearbeitungsschritt, 7d/3m-Auto-Pflichten, Public-Form, Bearbeiter-Dashboard) |
| 6 | ✅ | Compliance-Cockpit (Sidebar-Layout, Score-Donut + KPIs + ToDo-Liste + Activity-Feed, Notification-Bell, AuditLog-Viewer, Settings) |
| 7 | ✅ | Test-Hardening (pytest-cov 86 %+ Baseline, CI-Gate `--cov-fail-under=80`, Storybook 10, Playwright 8 E2E-Specs nur main) |
| 8 | ✅ | Production-Deploy (Multi-stage Dockerfiles ARM64, prod-Compose, Caddy-Switch, Brevo + OpenRouter + restic-Backup + GlitchTip live) |

**Phase-1.5+** (nicht im MVP-Scope): Self-Service-Tenant-Onboarding, KI-Inventar-Modul (AI Act), Datenpannen-Register (Art. 33 DSGVO), Transparenzregister-Sync, Hetzner-DNS-API-Wildcard-Cert.

Detail-Sprint-Plans liegen pro Sprint unter `docs/superpowers/plans/2026-05-08*` bis `2026-05-09-sprint-8*`.

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
- DNS: Hetzner DNS Console (`dns.hetzner.com`, Migration zu `console.hetzner.com` läuft Mai 2026)
- DNS-Records aktiv: `@`, `app`, `*.app` (Wildcard deckt `errors.app` etc.), `hinweise`, `www` → 204.168.159.236
- TXT-Records aktiv: `mailjet._domainkey` (legacy, kann weg), `brevo1._domainkey` + `brevo2._domainkey` (CNAME, DKIM), `@` mit `brevo-code:...`, `_dmarc`
- `.com` bewusst NICHT im MVP-Scope (Squatter; Phase-3-Ziel)

**Markenrechts-Status (2026-05-10):** vom User explizit auf später verschoben. Vor Pilot-Vertrag mit Anwalt prüfen lassen (DPMA-Recherche + Anmeldung Klassen 9/35/42, ~290 € + Anwaltsgebühr). Risiko: Konkurrent meldet zwischenzeitlich an, Konrad muss umbenennen.
