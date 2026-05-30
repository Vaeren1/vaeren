# CLAUDE.md — Projekt-Anweisungen für Claude

> **Für künftige Claude-Sessions:** Diese Datei enthält die wichtigsten Architektur- und Konventions-Entscheidungen für das ai-act-Projekt. Sie ist die schnelle Referenz; die tiefe Wahrheit liegt in den Specs unter `docs/superpowers/specs/`.

## Stand 2026-05-30 — Phase 4 / Feature 1 (Onboarding-Wizard) deployed

**Phase 4 = 4 Demo-/Vertriebs-Features** für die Präsentation vor Kanzlei-Partner + ersten Kunden (Reihenfolge: 1 Wizard → 4 Fragebögen → 3 Schulungs-Generator → 2 Vishing). Specs: `docs/superpowers/specs/2026-05-30-onboarding-wizard-compliance-radar-design.md`. Plan: `docs/superpowers/plans/2026-05-30-feature1-onboarding-wizard.md`.

**Feature 1 — Onboarding-Wizard / Compliance-Radar: deployed 2026-05-30** (PR #1 squash-merged, Commit `f48feff`). Erst-Login-Wizard: KI-Firmen-Recherche → Regulierungs-Relevanz-Engine (deterministisch, kein LLM, verallgemeinert NIS2-`klassifiziere_automatisch`) → Compliance-Radar mit Abdeckungs-Gradient (🟢 Voll-Modul / 🟡 LLM-Basis-Hinweis / ⚪ in Vorbereitung) → Ein-Klick-Modul-Aktivierung. Neue Bausteine: `core/regulierungen.py` + `core/betriebsmerkmale.py` (Kataloge als Code, anwaltsfest), `core/relevanz_engine.py`, `core/modules.py` (Modul-Registry, spiegelt Legacy-Flag `module_iso42001_aktiv`), `core/unternehmens_osint.py` (Demo-Cache; **echte `_llm_recherche` ist NotImplementedError-Stub = Backlog, Demo läuft über Fixture**), `core/basis_hinweis.py` (RDG-validiert). Neue Tenant-App `onboarding_wizard` (UnternehmensProfil/RegulierungsBefund/OperativeEmpfehlung). Migrations: `onboarding_wizard/0001` + `tenants/0007_tenant_aktive_module`. Entwickelt via subagent-driven-development + 3 PR-Review-Runden. Demo-Tenant geseedet (`seed_onboarding_demo`): 13 Befunde + 31 Empfehlungen. Tenant-API GF-gated (403 live verifiziert).

**Wichtig — bekannte CI-Altlast (NICHT von Feature 1):** Die Backend- (`ruff` repo-weit, ~190 pre-existing Findings) und Frontend-CI-Gates (`bun test` globt Playwright-E2E-Specs → bricht) sind auf `main` **dauerhaft rot** und waren es schon vor Feature 1. Feature-1-eigener Code ist ruff-clean. PR #1 wurde per `--admin` gemergt (keine echte Branch-Protection). Aufräumen = eigenes Ticket.

**Feature 4 — OEM-Fragebogen-Auswerter: deployed 2026-05-31** (PR #2 squash-merged, Commit `ef5770b`). Beliebige Fragebögen hochladen → Auto-Antworten aus ALLEN Firmendaten (Wiederverwendung `auditor_export`-Aggregator-Registry) + `UnternehmensProfil` + kuratierbarer **Antwort-Bibliothek** (Auto-Übernahme bei Attestierung, dedupliziert, Engine-Quelle Nr. 1) → seiten-basierter Review (kein Klick pro Antwort, finale Attestierung als RDG-Gate) → ausgefülltes Original. Neue Tenant-App `fragebogen` (Models Fragebogen/Frage/Antwort/AntwortQuelle/AntwortBibliothekEintrag, Migrations 0001+0002). **3 Tiers:** Tier 1 strukturiert sync (xlsx/PDF-Formular via openpyxl/pypdf), Tier 3 Beiblatt (WeasyPrint), Tier 2 unstrukturierte PDF async (Tesseract-OCR + reportlab-Overlay + 2-Agenten-Vision-Review-Loop + Celery, fail-safe). **RDG:** Single-Source-Gate `fragebogen/rdg.py::ist_rdg_freigegeben` an jedem Export-Austritt + Bibliothek-Übernahme; kein ungeprüfter LLM-Text raus. GF + Compliance-gated. **Dockerfile:** tesseract-ocr (deu/eng) + poppler-utils ergänzt. 87 Tests grün, 3 PR-Review-Runden (2 Critical gefixt: Tier-2-OCR nie verdrahtet, Celery-Task ohne Tenant-Schema). Demo-Seed `seed_fragebogen_demo`: 7 Fragen + 7 Bibliothek-Einträge.

**Backlog Phase 4:** Live-OSINT (`_llm_recherche`, Feature 1), Feature 3 (KI-Schulungs-Generator YouTube→Quiz), Feature 2 (Vishing/Voice-Clone-Demo — Quality-Gate: überzeugt der Klon nicht, fliegt es raus; Cloud-Demo, self-hosted EU fürs Produkt). Fragebogen-Detailbacklog: docx-Tier-1-fill, Bibliothek-Direkt-CRUD-RDG-Validator, Pagination-UI, schema-getrenntes Datei-Storage (projektweit).

## Stand 2026-05-18 — Phase 3 deployed in Production (nach Audit-Review-Pass)

**Deploy erfolgt am 2026-05-18** (Commit `0778c36`). Vorher Audit-Review-Pass mit 4 parallelen Audit-Agenten: **6 Deploy-Blocker + 12 HOCH-Findings + 30 Mittel/Niedrig** gefunden, alle 6 Blocker + 12 HOCH gefixt + 5 Frontend-Skeletons ausgebaut. Compliance-Index Demo-Tenant: 89 → **91/100 green**. Tests: 102/102 Phase-3-Modul-Tests grün. Details (inkl. Blocker-Liste: DSGVO-Art.-9-Bruch bei Unfall-Gesundheitsdaten, inaktiver RDG-Layer-2-Validator, Aggregator-Stubs, tenant_schema-Leak) in `~/.claude/projects/-home-konrad-ai-act/memory/project_phase3_status.md`.

**Phase-3-Module fertig integriert** (4 parallele Subagent-Worktrees → sequenziell gemerged):
- `iso27001/` — ISO-27001-Evidence-Sammler (93 Annex-A-Controls, RDG-3-Layer, SoA-PDF, Risk-Register, 39 Tests / 92% Coverage)
- `iso42001/` + `iso42001_catalog/` — KI-Management-System nach ISO 42001 (38 Controls Public-Schema, AIIA-4-Augen, Policy-CRUD, Incident→Datenpanne-Eskalation, Module-Activation-Gate, 46 Tests / 85% Coverage)
- `arbeitsschutz/` — GBU + ASA + Unfälle (verschlüsselt) + Beauftragte + Betriebsanweisungen (76 Gefährdungs-Seed, STOP-Hierarchie, Compliance-Score-Formel-Änderung auf 0.40/0.15/0.45, 34 Tests)
- `auditor_export/` — OSCAL + PDF (WeasyPrint) + ZIP-Bundle mit HMAC-Signatur, 10 Aggregatoren, public Verify-Endpoint (44 Tests)

**Tenant-Model erweitert:** `module_iso42001_aktiv` (BooleanField), `audit_signing_key` (BinaryField, HMAC-SHA256). Migrations `tenants/0005_iso42001` und `tenants/0006_audit_signing_key`.

**Bekannter pre-existing Test-Break (NICHT durch Phase 3 verursacht):** `tests/test_redaktion_pipeline.py` mockt `redaktion.pipeline.curator.call_json` — wurde in Commit c6ff49a zu `call_json_with_fallback` umbenannt, Test-Mock blieb. Vor Phase 3 schon kaputt.

**Migrations deployed** (5 tenant-schema: iso27001/0001, iso27001/0002 seed, iso42001/0001, arbeitsschutz/0001, auditor_export/0001 + tenants/0005_iso42001 + tenants/0006_audit_signing_key).

**Backlog Phase 3b/4** (bewusst nicht gebaut): KI-Beauftragter als eigene Rolle, ISO-42001-Policy-Templates, Demo-Fixtures + Storybook/Playwright-E2E für die 4 neuen Module, Vollkatalog 120 Gefährdungen (aktuell 76), PDF/A-3-Konformität, OSCAL-Schema-Validation in CI, Policy-Kenntnisnahme-Reminder (Celery-Beat).

## Stand 2026-05-10 — Vaeren ist live in Production (MVP)

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
- **Feature-Completion-Discipline:** Jedes Feature wird *komplett* ausgebaut und abgeschlossen, bevor das nächste begonnen wird. „Komplett" = Backend + Frontend + Tests + Migration + Deploy-fähig. Keine halbfertigen Module, keine TODO-Stubs, kein Parallel-Switching zwischen Features. Begründung: Konrad ist Solo-Builder und braucht den Kopf frei für die nächste Aufgabe — angefangene Halbfertig-Features sind kognitive Last + technische Schulden gleichzeitig. Wenn ein Feature zu groß für einen Schritt ist, in Spec/Plan in vollständige Sub-Features schneiden — jedes für sich abgeschlossen.

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
- **Trigger:** Claude darf nach Feature-Fertigstellung autonom `git push origin main && ./deploy.sh` ausführen — keine Bestätigung nötig. Sonderfall riskante Datenmigrationen / Schema-Drops / Tenant-Lösch-Ops: vorher kurz erklären, dann ausführen. **Kein Auto-Deploy in CI** (bleibt manuell-aus-Laptop-getriggert, aber Claude darf das triggern)
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
