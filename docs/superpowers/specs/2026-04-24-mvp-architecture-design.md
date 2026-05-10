# Design-Spec: MVP-Architektur — Compliance-Autopilot

| | |
|---|---|
| **Status** | Approved (Konrad Bizer, 2026-04-24) |
| **Autor** | Konrad Bizer + Claude (Brainstorming-Session) |
| **Datum** | 2026-04-24 |
| **Scope** | Tech-Stack, System-Komponenten, Datenmodell, Auth, Integrationen, LLM-Strategie, Deployment, Testing, Sprint-Plan |
| **Out of Scope** | UI-Designs (Wireframes/Mockups → eigener Spec), Modul-Detail-Specs (Feature-Liste pro Modul → eigene Specs ab Phase 1.5), Self-Service-Sign-Up (Phase 1.5+) |
| **Vorgänger-Spec** | `2026-04-24-icp-and-launch-story-design.md` (ICP, Personas, Launch-Story, Pricing, GTM, Risiken) |
| **Folge-Dokumente** | Implementation-Plan via `superpowers:writing-plans` (TDD-Tasks) |
| **App-Name** | **Vaeren** — finalisiert in Naming-Session 2026-04-27 (siehe `2026-04-27-naming-decision-vaeren.md`). Domain `vaeren.de` registriert + DNS bei Hetzner gesetzt. |

## 1. Kontext und Architektur-Leitprinzipien

Aus dem Vorgänger-Spec übernommen (kurze Ableitungen, nicht wiederholt):

- **ICP:** Industrie-Mittelstand DE, 50–300 MA (Kern), Pilot-Phase 0–10 Kunden
- **Slogan:** „Wir übernehmen die Pflichten, ihr macht Produktion."
- **Bundle-Vision:** Compliance-Autopilot mit modularer Erweiterung (AI Act + DSGVO + NIS2 + ISO + Pflichtschulungen + HinSchG + …)
- **Solo-Bootstrap-Constraint:** 8–12 Std/Woche neben PayWise-Hauptjob
- **Codegen-Modus:** Konrad architektiert, Claude generiert Code → Stack muss für Konrad lesbar/reviewbar sein

### Architektur-Leitprinzipien

1. **Time-to-MVP über Premature-Optimization** — Stack auf Konrads Stärken (Django) statt Performance-Sprachen (Go/Rust) — MVP-Performance reicht 100×
2. **YAGNI ruthlessly** — keine Features bauen, bis Pilot-Kunden sie verlangen
3. **Bundle-Synergie als Moat** — gemeinsame Engine (Mitarbeiter, ComplianceTask, Evidence) bedient alle Module
4. **RDG-Schutz technisch verankert** — kein „Disclaimer reicht", sondern Architektur-Pflicht (3 Schutzschichten)
5. **Migrierbarkeit > Perfektion** — Storage-Backend-Switch, Hosting-Wechsel, LLM-Provider-Switch jederzeit möglich
6. **Compliance-Sales-Argument first** — Hosting-Standort, Verschlüsselung, Audit-Logs, Multi-Tenancy-Isolation als Verkaufsargumente sichtbar machen

## 2. Tech-Stack (gefroren)

### Backend

| Komponente | Wahl | Grund |
|---|---|---|
| Sprache | **Python 3.12** | Konrad-Stärke (Django-Tagesarbeit) |
| Framework | **Django 5.0 LTS** (LTS bis 2028) | Tägliche Konrad-Arbeit, Batteries-Included, Admin-UI gratis |
| API-Framework | **Django REST Framework** | Industry-Standard, integriert mit Django |
| OpenAPI-Schema | **drf-spectacular** | Auto-generiert Schema → Frontend-TS-Types |
| Multi-Tenancy | **django-tenants** (schema-per-tenant) | Stärkstes Isolations-Argument für Compliance-Sales |
| Async | **Django Async-Views nur gezielt** für I/O-parallele Endpunkte (z. B. M365 + Google parallel abfragen). 95% Sync. | Mixed-Sync/Async-Bugs sind teuer; Celery löst Background-Bedarf besser |
| Background-Jobs | **Celery + Redis** | Standard, robust, Sponty-erprobt |
| Scheduled-Jobs | **celery-beat** mit `django_celery_beat` Database-Scheduler | Periodische Compliance-Checks, Frist-Tracking |
| ORM | **Django ORM** (built-in) | Konrad-vertraut |
| Migrations | **django.db.migrations** + `migrate_schemas` (django-tenants) | Standard |
| Auth | **django-allauth + dj-rest-auth + django-allauth-2fa** (TOTP) | Email/Password + MFA via TOTP ab MVP |
| Verschlüsselung at rest | **django-cryptography** (`BinaryField`-Encryption mit Fernet) | Pflicht für HinSchG-Meldungs-Inhalte |
| LLM-Client | **OpenAI-SDK gegen OpenRouter-Endpoint** | Provider-agnostisch via env-Var, gleiches Pattern wie Sponty |
| Mail-Backend | **django-anymail mit Mailjet-Backend** (FR, DSGVO-konform) | Transaktionsmail |
| Package-Manager | **uv** (statt pip) | 10–15× schneller, deterministische Lockfile, Docker-Build-Cache effizienter |
| Linting/Formatting | **Ruff** (statt black + flake8 + isort) | Astral-Stack, Single-Tool für alles |
| Storage | **Lokales Docker-Volume** `ai-act-media` + `django-storages` als Backend-Abstraktion | YAGNI bis 30+ Tenants, dann Switch zu Object Storage trivial |
| Backup | **restic** zu Hetzner Storage Box (verschlüsselt, off-site) | Daily, Retention 7d/4w/12m |

### Frontend

| Komponente | Wahl | Grund |
|---|---|---|
| Build-Tool | **Vite** | Kein Next.js-Overhead, schnellster Dev-Server |
| Framework | **React 18 + TypeScript** | Industry-Standard, Konrad TS-affin |
| Routing | **React Router 7** | SPA-Standard für Dashboards |
| Server-State | **TanStack Query (React Query)** | Modern Standard für API-Daten-Caching |
| Client-State | **Zustand** | Leichtgewichtig (3kb), simpler als Redux |
| UI-Library | **shadcn/ui + Tailwind CSS** | Copy-paste Components, voll anpassbar |
| Forms | **React Hook Form + Zod** | Beste DX für komplexe Formulare |
| Tables | **TanStack Table** | Headless, perfekt für Mitarbeiter-/Compliance-Listen |
| Charts | **Tremor** (Dashboard-fokussiert) + Recharts (für Custom-Charts) | Tremor ist auf SaaS-Dashboards spezialisiert |
| Type-Sync | **openapi-typescript** generiert TS-Types aus drf-spectacular Schema | Eine Quelle der Wahrheit |
| Package-Manager + Runtime + Test-Runner | **bun** | 25–50× schneller als npm, native Tests |
| Component-Doc + Interaction-Tests | **Storybook 8 + @storybook/test-runner** | UI-Logic-Tests ohne Browser |

### Daten & Storage

| Komponente | Wahl |
|---|---|
| Datenbank | **Postgres 16 (Alpine, multi-arch ARM64)** mit row-level-security verfügbar (für Phase 2) |
| Cache + Celery-Broker | **Redis 7 (Alpine)** |
| File-Storage MVP | Docker-Volume `ai-act-media`, abstrahiert via `django-storages.FileSystemStorage` |
| File-Storage Migrationspfad | Ab ~30 Tenants oder zweitem App-Server: Switch auf `storages.backends.s3.S3Storage` (1–2 Tage Migration, env-Var-basiert) |
| Volltextsuche | **Postgres Full-Text-Search** (MVP) — ElasticSearch erst ab echtem Skalierungsbedarf |

### Hosting & Infrastructure

| Komponente | Wahl |
|---|---|
| Server | **Hetzner CAX31 ARM64 in Helsinki** (`hel1`), 8 vCPU, 16 GB RAM, 160 GB Disk, ~19 €/Monat |
| Co-Location | **Parallel zu bestehendem Sponty-Stack** unter `/opt/ai-act/`, eigene Container mit `ai-act-`-Prefix, eigenes Docker-Network `ai-act-network` |
| Reverse-Proxy | **Caddy 2 als Host-Service** (nicht Container), ersetzt Sponty-nginx als Port-80/443-Owner. Routet nach Domain zu Sponty-Backend bzw. ai-act-Django |
| SSL-Zertifikate | **Let's Encrypt** über Caddy automatic HTTPS, Wildcard-Cert für `*.app.vaeren.de` via DNS-Challenge (Hetzner-DNS-API-Token, `caddy-dns/hetzner` Plugin) |
| DNS-Provider | **Hetzner DNS Console** (`dns.hetzner.com`) — gleiche Hetzner-Verwaltung wie Server, kostenlos, EU-konform, API-tauglich für Caddy-Wildcard-Cert. **Bereits eingerichtet** für vaeren.de mit Records `@`, `app`, `*.app`, `hinweise`, `www` → 204.168.159.236 |
| Container-Runtime | **Docker + Docker Compose** (Sponty-Pattern) |
| Backup | **Hetzner Storage Box** (~4 €/Monat, 100 GB), `restic` verschlüsselt |
| Monitoring | **Sentry EU-Region** (Free-Tier MVP, später Team-Plan), **Plausible Analytics** für Marketing-Site |
| DSGVO-Standort-Note | Helsinki ist EU-/DSGVO-konform, aber NICHT Deutschland. Migration nach FSN1/Frankfurt dokumentiert als Trigger-Event ab 5+ Pilot-Kunden mit „muss DE sein"-Blocker. |

### CI/CD

| Komponente | Wahl |
|---|---|
| Code-Repo | **GitHub Private** (eigener Account, getrennt von PayWise/Sponty) |
| CI | **GitHub Actions** — `test.yml` (PR + Push), `deploy.yml` nur manuell triggerbar |
| Container-Build | **Server-side via Docker Compose** (Sponty-Pattern, keine Cross-Compile-Komplexität) |
| Container-Registry | nicht benötigt (Build auf Server) |
| Secret-Mgmt MVP | `.env.production` lokal, deployed via `scp`, niemals im Repo |
| Secret-Mgmt Phase 2 | Bitwarden Secrets Manager oder HashiCorp Vault, ab 5+ Kunden |
| Deploy-Trigger | **Manuell:** `./deploy.sh` von Konrads Laptop |

## 3. System-Topologie

```
┌──────────────┐
│   Browser    │ (KMU-Mitarbeiter, QM-Leiter, GF, IT-Leiter)
└──────┬───────┘
       │ HTTPS (TLS via Caddy + Let's Encrypt)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Hetzner CAX31 ARM64 — Helsinki — 204.168.159.236               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Caddy 2 (Host-Service) — Port 80/443 Reverse-Proxy      │   │
│  │  *.app.vaeren.de  →  ai-act-django:8000              │   │
│  │  hinweise.app.vaeren.de  →  ai-act-django:8000       │   │
│  │  vaeren.de  →  ai-act-django:8000 (Marketing)        │   │
│  │  sponty.de  →  sponty-nginx:80                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│       ┌────────────────────┼─────────────────────┐               │
│       ▼                    ▼                     ▼               │
│  ┌─────────┐        ┌──────────────┐      ┌────────────┐        │
│  │ /opt/   │        │ /opt/ai-act/ │      │ /opt/ai-   │        │
│  │ sponty/ │        │              │      │ act/       │        │
│  │ (existing)│      │  ai-act-     │      │  ai-act-   │        │
│  │         │        │  django      │      │  postgres  │        │
│  │         │        │  (Daphne ASGI│      │  (schema-  │        │
│  │         │        │  +DRF+Static)│      │   per-tenant)│       │
│  └─────────┘        └──────┬───────┘      └────────────┘        │
│                            │                                     │
│                ┌───────────┼───────────┐                         │
│                ▼           ▼           ▼                         │
│         ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│         │ai-act-   │ │ai-act-   │ │ai-act-   │                  │
│         │redis     │ │celery-   │ │celery-   │                  │
│         │(broker+  │ │worker    │ │beat      │                  │
│         │ cache)   │ │          │ │          │                  │
│         └──────────┘ └──────────┘ └──────────┘                  │
│                                                                  │
│  Docker-Volumes:                                                 │
│  • ai-act-postgres-data                                          │
│  • ai-act-redis-data                                             │
│  • ai-act-media (Files, später Migration zu S3 möglich)          │
│                                                                  │
│  Cron (täglich): restic-Backup → Hetzner Storage Box             │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTPS (alles outbound)
       ┌─────────────┼─────────────┬──────────────┬───────────────┐
       ▼             ▼             ▼              ▼               ▼
  ┌─────────┐  ┌─────────┐  ┌──────────┐   ┌──────────┐    ┌──────────┐
  │OpenRouter│  │ Mailjet │  │ Hetzner  │   │ Sentry   │    │ Hetzner  │
  │(LLM-     │  │ (Trans- │  │ DNS      │   │ EU       │    │ Storage  │
  │ Multi-   │  │  aktion-│  │(Records +│   │ (Errors) │    │ Box      │
  │ Provider)│  │  ale    │  │ DNS-     │   │          │    │ (Backup) │
  │          │  │  Mail)  │  │ Challenge│   │          │    │          │
  └─────────┘  └─────────┘  └──────────┘   └──────────┘    └──────────┘
```

## 4. Multi-Tenant-Architektur

### Pattern: Schema-per-Tenant via django-tenants

- **Eine Datenbank** `ai_act_db`, **mehrere Schemas** (eines pro Tenant + ein `public`-Schema)
- Tenant-Erkennung via Subdomain: `acme.app.vaeren.de` → Schema `acme_gmbh`
- HTTP-Anfrage triggert `django-tenants`-Middleware: liest Subdomain, schaltet `connection.schema_name` für die gesamte Request-Laufzeit
- Cross-Tenant-Datenleak strukturell unmöglich, weil Tenant-A-Session physisch nie Tenant-B-Schema sieht

### Schemas

**`public`-Schema** (global, alle Tenants gemeinsam):
- `Tenant`, `TenantDomain`, `GlobalAdminUser`, `BillingRecord`, `CrossTenantAuditLog`
- Niemals Kunden-Geschäftsdaten

**Tenant-Schema** (pro Kunde, z. B. `acme_gmbh`):
- Shared Core: `User`, `Mitarbeiter`, `ComplianceTask`, `Evidence`, `Notification`, `AuditLog`, `LLMCallLog`
- Modul-spezifisch: siehe §5

### Tenant-Erstellung (MVP, manuell)

```python
# Management-Command python manage.py create_tenant
tenant = Tenant.objects.create(
    schema_name="acme_gmbh", firma_name="ACME GmbH",
    plan="professional", pilot=True, pilot_discount_percent=40,
    contract_start=date(2026,5,1), contract_end=date(2027,4,30),
)
TenantDomain.objects.create(
    tenant=tenant, domain="acme.app.vaeren.de", is_primary=True,
)
# Schema wird automatisch durch django-tenants angelegt + Migrations gefahren
```

Self-Service-Tenant-Onboarding kommt **erst Phase 1.5** (siehe §11).

## 5. Datenmodell

### Detail-Schema-Definitionen

Konkrete Modelle (zur tieferen Detaillierung in Folge-Modul-Specs):

**Public-Schema:**
- `Tenant(schema_name, firma_name, plan, pilot, mfa_required, locale, contract_start, contract_end)`
- `TenantDomain(domain, tenant_FK, is_primary)`
- `GlobalAdminUser(...)` — Konrads/Support-Team
- `BillingRecord(tenant, period_start/end, amount_eur, status, invoice_pdf_path)`
- `CrossTenantAuditLog(tenant, actor_email, action, timestamp, detail_json)`

**Tenant-Schema — Shared Core:**
- `User(email, tenant_role, mfa_enabled, last_password_change)` — Login-User innerhalb des Tenants. Rollen: `geschaeftsfuehrer`, `qm_leiter`, `it_leiter`, `compliance_beauftragter`, `mitarbeiter_view_only`
- `Mitarbeiter(vorname, nachname, email, abteilung, rolle, eintritt, austritt, external_id)` — NICHT Login-User, sondern Pflicht-Adressaten. `external_id` für ERP-Sync (Phase 2)
- `ComplianceTask(titel, modul, kategorie, frist, verantwortlicher, betroffene[M2M Mitarbeiter], status, extension[GenericFK])` — die Engine. Polymorphe Erweiterung über `GenericForeignKey` zu Modul-spezifischen Tasks
- `Evidence(titel, datei_path, sha256, mime_type, groesse_bytes, bezug_task, aufbewahrung_bis, immutable=True)` — Audit-Beleg, manipulationssicher via SHA-256
- `Notification(empfaenger_user, empfaenger_mitarbeiter, channel[email/in_app/sms], template, template_kontext[JSON], geplant_fuer, versandt_am, geoeffnet_am, status)`
- `AuditLog(actor, actor_email_snapshot, aktion, target[GenericFK], aenderung_diff[JSON], timestamp, ip_address)` — immutable

**Tenant-Schema — Pflichtunterweisungs-Modul:**
- `Kurs(titel, pflicht_kategorie, inhalt_html, quiz_fragen[JSON], bestehens_schwellwert, frequenz_monate, pflicht_fuer_rollen, aktiv)`
- `SchulungsTask(compliance_task[1:1], kurs, welle_nummer)` — extends `ComplianceTask`
- `Teilnahme(schulungs_task, mitarbeiter, eingeladen_am, gestartet_am, abgeschlossen_am, quiz_score_prozent, bestanden, zertifikat_evidence[1:1])`

**Tenant-Schema — HinSchG-Modul:**
- `Meldung(eingangs_token, eingangs_kanal, anonym, melder_kontakt_verschluesselt[BinaryField AES-256], titel, beschreibung_verschluesselt[BinaryField], kategorie, schweregrad, bestaetigung_versandt_am, rueckmeldung_faellig_bis, status)`
- `MeldungsTask(compliance_task[1:1], meldung, pflicht_typ[bestaetigung_7d/rueckmeldung_3m/abschluss])` — extends `ComplianceTask`
- `Bearbeitungsschritt(meldung, bearbeiter, aktion, notiz, timestamp)`

**Tenant-Schema — LLM-Audit:**
- `LLMCallLog(user, task_type, model, prompt_hash, response_text, input_tokens, output_tokens, cache_hit_tokens, cost_eur, latency_ms, timestamp, related_task)`

### Schema-Erweiterungs-Pattern für neue Module

Jedes neue Modul (KI-Inventar, Datenpannen, Transparenzregister, ISO-27001) erweitert `ComplianceTask` nach demselben 1:1-Pattern wie `SchulungsTask`/`MeldungsTask`. **Nie neues Engine-Modell, immer Erweiterung.**

## 6. Auth & Sessions

### Login-Flow

- **Mechanismus:** HTTP-only Session-Cookie auf `*.app.vaeren.de` (Same-Site-Domain). KEIN JWT.
- **Library:** `django-allauth` + `dj-rest-auth` + `django-allauth-2fa`
- **Tenant-Erkennung:** Subdomain → `django-tenants`-Middleware → Schema-Switch
- **CSRF:** Django-CSRF-Token in Header `X-CSRFToken` für mutierende Requests, automatisch erzwungen durch `SessionAuthentication`

### MFA

- **TOTP** (Google Authenticator, Authy, 1Password) im MVP
- **10 Backup-Codes** pro User beim Setup, ausdruckbar
- **Per-Tenant-Policy:** Default „optional", per Tenant-Setting `mfa_required=True` erzwingbar
- **Recovery:** Backup-Code-Login → MFA-Reset durch Tenant-Admin (NICHT durch Konrad — vermeidet Support-Aufwand)
- **Phase 2:** WebAuthn (Hardware-Keys, Face-ID), SSO/SAML/OIDC für Enterprise

### Permissions

Rollen-Matrix pro Modul (Beispiel):

| Aktion | GF | QM-Leiter | IT-Leiter | Compliance-Beauftr. | Mitarbeiter-View |
|---|---|---|---|---|---|
| Kurs erstellen | ✅ | ✅ | ❌ | ✅ | ❌ |
| Schulungs-Welle starten | ✅ | ✅ | ❌ | ✅ | ❌ |
| HinSchG-Meldung lesen | ✅ | ❌ | ❌ | ✅ | ❌ |
| HinSchG-Meldung bearbeiten | ❌ | ❌ | ❌ | ✅ | ❌ |
| Compliance-Score sehen | ✅ | ✅ | ✅ | ✅ | ❌ |
| Mitarbeiter editieren | ✅ | ✅ | ❌ | ✅ | ❌ |
| Eigene Schulungen sehen | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tenant-Settings ändern | ✅ | ❌ | ❌ | ❌ | ❌ |

Rollen-Mapping erfolgt via `django-rules`-Library (Object-Level-Permissions).

## 7. Integrationen

### Phase 1 (MVP)

| Integration | Zweck | Lib | Aufwand | Kritikalität |
|---|---|---|---|---|
| Mailjet | Transaktionsmails | django-anymail[mailjet] | 1 Tag | 🔴 hoch |
| Lokales Storage | File-Speicherung | django-storages.FileSystemStorage | 0,5 Tag | 🔴 hoch |
| OpenRouter (LLM) | Gemini 2.5 Flash + Mistral Small 3.2 (free) | OpenAI-SDK | 2 Tage | 🟡 mittel |
| Sentry EU | Error-Monitoring | sentry-sdk[django] | 0,5 Tag | 🟢 niedrig |
| Plausible Analytics | Marketing-Site Tracking | `<script>` snippet | 0,1 Tag | 🟢 niedrig |
| Caddy + Let's Encrypt + Hetzner DNS | SSL + Routing, Wildcard-Cert via Hetzner-DNS-API (caddy-dns/hetzner) | Caddy + Plugin | 1 Tag | 🔴 hoch |
| Hetzner Storage Box | Backup | restic | 0,5 Tag | 🔴 hoch |

### Phase 1.5 (~Monat 5–6)

| Integration | Zweck |
|---|---|
| Bundesanzeiger / Transparenzregister-API | Tenant-Stammdaten + Änderungs-Monitoring |
| Handelsregister-API | Tenant-Onboarding-Auto-Füllung |

### Phase 2 (~Monat 6–9)

| Integration | Zweck |
|---|---|
| Microsoft Graph API (M365) | KI-Tool-Auto-Discovery |
| Google Workspace Admin API | Gleiches für G-Workspace-Kunden |
| Browser-Extension | Lokales KI-Tracking ohne API-Zugang |

### Phase 3+

| Integration | Zweck |
|---|---|
| SAP / Odoo / ProAlpha ERP | Mitarbeiter-Sync |
| DATEV | HR-Daten-Sync |
| TÜV / DEKRA Audit-Export | OSCAL/JSON |
| Stripe | Self-Service-Checkout (falls jemals nötig) |
| BNetzA-Meldekanal | AI-Act-Vorfälle |

### Architektur-Pattern für externe APIs

```python
# integrations/<service>/client.py — pure HTTP-Client, kein Django-Coupling
class MailjetClient:
    def send(self, to, template, context) -> SendResult: ...

# integrations/<service>/tasks.py — Celery-Wrapper mit Retry
@shared_task(bind=True, autoretry_for=(RequestException,), max_retries=5,
             retry_backoff=True, retry_backoff_max=600)
def send_mail_task(self, notification_id):
    notification = Notification.objects.get(id=notification_id)
    client = MailjetClient(...)
    result = client.send(...)
    notification.versandt_am = timezone.now()
    notification.save()
```

**Drei nicht-verhandelbare Regeln:**

1. **Niemals synchron im HTTP-Request.** Alles geht durch Celery
2. **Retry mit Exponential Backoff** für transient errors, **Dead-Letter-Queue** für permanente Failures
3. **API-Keys nur in `.env.production`** — niemals im Repo, niemals im Frontend-Bundle

### Webhooks vs. Polling

- **Mailjet-Bounce/Open-Tracking:** Webhook
- **Transparenzregister-Änderungen:** Polling (1×/Woche)
- **Anthropic/OpenRouter:** Sync request/response in Celery-Task
- **Stripe (Phase 2+):** Webhook + Signature-Verification

## 8. LLM-Strategie

### Provider-Architektur

- **Provider:** OpenRouter als Multi-Provider-Aggregator (gleiches Pattern wie Sponty)
- **Client:** OpenAI-Python-SDK gegen OpenRouter-Endpoint
- **Provider-Switch:** env-Variable, kein Code-Refactor

```python
LLM_API_BASE = "https://openrouter.ai/api/v1"
LLM_API_KEY = "<OpenRouter-Key>"
LLM_MODEL_FAST = "google/gemini-2.5-flash:free"          # MVP
LLM_MODEL_REASONING = "mistralai/mistral-small-3.2:free"  # MVP
LLM_DAILY_BUDGET_EUR = 0.0                                # MVP free
```

**Migrations-Pfad zu Bezahl-Modellen** (ab Phase 2 mit zahlenden Kunden):

```python
LLM_MODEL_FAST = "anthropic/claude-haiku-4-5"
LLM_MODEL_REASONING = "anthropic/claude-sonnet-4-6"
LLM_DAILY_BUDGET_EUR = 2.0
```

### MVP-Default-Models (free tier)

| Tier | Model | Latenz | DE-Qualität | Free-Limit |
|---|---|---|---|---|
| Fast | `google/gemini-2.5-flash:free` | niedrig | sehr gut | ~1.500 req/Tag |
| Reasoning | `mistralai/mistral-small-3.2:free` | niedrig | sehr gut, EU-hosted | limited |

### RDG-Schutz-Architektur (3 Layer, Pflicht)

1. **System-Prompt erzwingt Vorschlags-Sprache** — alle LLM-Outputs beginnen mit „Vorschlag:" und enden mit Mensch-Validierungs-Aufforderung
2. **Output-Validator (Code, post-hoc):** verbotene Formeln (`ist Hochrisiko`, `muss gemeldet werden`) führen zur Re-Generierung mit verschärftem Prompt
3. **HITL-Gate vor jeder Wirkung:** Mensch bestätigt vor Versand/Speicherung. Auto-Akzeptanz nur bei kategorisch sicheren Tasks (Schulungs-Reminder ohne juristischen Inhalt)

### LLM-Audit-Log

Jeder LLM-Call wird in `LLMCallLog` (Tenant-Schema) protokolliert mit Model, Prompt-Hash, Response, Tokens, Kosten, Latenz, related Task. Auditor-tauglich, Kostenanalyse-tauglich.

### Tenant-Tagesbudget (ab Phase 2)

| Plan | Tagesbudget | Monatsbudget |
|---|---|---|
| Starter | 0,50 € | ~15 € |
| Professional | 2,00 € | ~60 € |
| Business | 5,00 € | ~150 € |

Bei 80% → Alert. Bei 100% → Fallback auf statische Templates.

### Prompt-Library (versionsverwaltet)

```
backend/integrations/llm/prompts/
  ├── system/
  │   ├── compliance-context.de.md
  │   └── compliance-context.en.md
  ├── schulung_einladung.de.md
  ├── hinschg_eingangsbestaetigung.de.md
  ├── compliance_score_erklaerung.de.md
  └── tests/
      └── *.test.md  (Beispiel-Inputs + erwartete Output-Eigenschaften)
```

## 9. Deployment

### Repo-Struktur

```
ai-act/
├── backend/
│   ├── Dockerfile, pyproject.toml, uv.lock, manage.py
│   ├── config/ (settings, asgi, urls)
│   ├── core/, pflichtunterweisung/, hinschg/, dashboard/
│   ├── tenants/, integrations/{llm,mailjet,storage}/
│   └── tests/
├── frontend/
│   ├── Dockerfile.builder, package.json, bun.lockb, vite.config.ts
│   ├── src/{routes,components,lib/api}/
│   └── tests/, .storybook/
├── caddy/Caddyfile
├── docker-compose.{prod,dev}.yml
├── deploy.sh
├── .github/workflows/{test,deploy}.yml
├── docs/superpowers/{specs,plans}/
├── infrastructure/README.md
├── .env.example, .gitignore
└── README.md
```

### Multi-Stage Dockerfile

Backend-Image baut in 3 Stages:
1. Python-Deps via `uv sync --frozen`
2. Frontend-Build via `bun run build` → statische Assets
3. Runtime: Python + Statics + Daphne als ASGI-Server

Build erfolgt **server-side** (ARM64-native) — keine Cross-Compile-Komplexität.

### docker-compose.prod.yml

- `ai-act-postgres` (postgres:16-alpine, multi-arch)
- `ai-act-redis` (redis:7-alpine)
- `ai-act-django` (Custom-Build, Daphne ASGI auf Port 8000)
- `ai-act-celery-worker` (gleiche Image, Concurrency 2)
- `ai-act-celery-beat` (gleiche Image, scheduler `django_celery_beat.schedulers:DatabaseScheduler`)
- Volumes: `ai-act-postgres-data`, `ai-act-redis-data`, `ai-act-media`
- Network: `ai-act-network` (isoliert von `sponty-network`)

### Caddy als Host-Service

Caddy läuft direkt auf dem Host (apt-installed, nicht Docker), belegt Port 80/443. Caddyfile routet:

- `*.app.vaeren.de` + `vaeren.de` → `ai-act-django:8000`
- `sponty.de` → `sponty-nginx:80`

Wildcard-Cert für `*.app.vaeren.de` via Hetzner-DNS-Challenge (`HETZNER_DNS_API_TOKEN` als Env-Var, generiert in Hetzner DNS Console → API-Tokens).

**Migration sponty-nginx → Caddy:** Geplante 30-Min-Wartung (am besten Sonntag-Nacht), siehe Sprint 8.

### deploy.sh

```bash
# 1. Pre-flight: .env.production existiert? Tests grün?
# 2. rsync Source-Files zum Server (excl. .git, .venv, node_modules, .env*, .superpowers/)
# 3. scp .env.production → /opt/ai-act/.env
# 4. ssh: docker compose -f docker-compose.prod.yml up -d --build
# 5. Smoke-Test: curl /api/health/
```

### CI

```yaml
# .github/workflows/test.yml — bei jedem PR + Push
jobs:
  backend-tests:    # pytest + Multi-Tenant-Isolation-Test (kritisch, blockt Merge bei Fail)
  frontend-tests:   # bun test + bun run typecheck
  storybook-tests:  # bun run test-storybook
  openapi-sync:     # generiert TS-Types, prüft im PR ob aktuell
  e2e-tests:        # nur auf main: playwright
```

**Kein Auto-Deploy.** Konrad triggers manuell via `./deploy.sh`.

### Migrations-Strategie

- `migrate_schemas --noinput` läuft im Container-CMD vor Daphne-Start
- Migrations müssen **rückwärtskompatibel** sein: kein Spalten-Drop direkt — erst Code anpassen + deployen, dann Spalte droppen in Folge-PR

### Backup

```bash
# /etc/cron.daily/ai-act-backup
restic -r sftp:storagebox.hetzner.com:/ai-act backup \
  /var/lib/docker/volumes/ai-act-postgres-data/_data \
  /var/lib/docker/volumes/ai-act-media/_data \
  /opt/ai-act/.env
restic -r sftp:storagebox.hetzner.com:/ai-act forget \
  --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
```

## 10. Test-Strategie (4 Schichten)

### Schicht 1: API-Integration-Tests (Hauptbollwerk gegen Regression)

- **Tool:** pytest-django + factory_boy + responses (HTTP-Mocking)
- **Coverage-Ziel:** 90% Business-Logic, 75% Views/Serializers
- **~250+ Tests**, gesamt ~30 Sekunden
- Testet **denselben Code-Pfad** wie der echte UI-Klick (durch React → DRF-API)

### Schicht 2: OpenAPI-Schema-Sync

- drf-spectacular generiert OpenAPI-Schema → openapi-typescript erzeugt TS-Types
- CI-Check: Frontend-Build failed wenn Backend-Schema bricht
- **Automatischer Contract-Schutz**, ohne weiteren Test-Code

### Schicht 3: Storybook + Interaction-Tests

- **Tool:** Storybook 8 + @storybook/test-runner
- Component-Stories mit `play`-Functions simulieren Klicks/Inputs ohne Browser
- Testet UI-Logik: State-Übergänge, conditional rendering, Form-Validation
- ~50–100 Tests, jeder <100ms
- Ergänzt natürlich den Component-Dev-Workflow

### Schicht 4: Playwright (sparsam)

- Nur die **8 kritischen User-Journeys**:
  1. Tenant-Anlage (manuell durch Admin)
  2. QM-Leiter erstellt Schulungs-Welle, versendet Einladungen
  3. Mitarbeiter absolviert Schulung (Quiz)
  4. HinSchG-Meldung anonym einreichen
  5. QM-Leiter bearbeitet HinSchG-Meldung
  6. Compliance-Dashboard zeigt korrekten Score
  7. MFA-Login-Flow (Setup + Login mit TOTP)
  8. Demo-Request-Form
- Läuft nur auf main-Branch, nicht jeder PR

### Multi-Tenant-Isolation-Test (kritischer CI-Gate)

```python
def test_tenant_isolation_strikt(acme_tenant, meier_tenant, db):
    with schema_context("acme_test"):
        MitarbeiterFactory(vorname="Anna", nachname="Acme")
    with schema_context("meier_test"):
        MitarbeiterFactory(vorname="Bert", nachname="Meier")
        assert not Mitarbeiter.objects.filter(nachname="Acme").exists()
        assert Mitarbeiter.objects.count() == 1
```

**Build failed wenn dieser Test bricht.** Datenleck-Schutz ist nicht verhandelbar.

### Anti-Patterns, die wir vermeiden

- ❌ Echte LLM-API-Calls in Tests
- ❌ Echte Mails versenden in Tests
- ❌ Snapshot-Tests für komplexe UIs
- ❌ Mocking ohne Verifikation (Mock-Check Pflicht)
- ❌ Parallele „Test-Endpoints" neben echten Endpoints (verfälscht Coverage, doppelte Pflege)

## 11. Phasenplan

*Sprint-Nummern sind relativ zum Projekt-Start (Sprint 1 = Tag 1 aktive MVP-Entwicklung). „Monat X" Angaben in späteren Phasen sind relativ zur ersten Demo bei Pilot-Kunden (≈ Ende Sprint 8).*

### MVP (Phase 1, Sprint 1–8 = 8 Wochen × ~10 Std)

3 Module: Compliance-Dashboard + Pflichtunterweisungs-Suite + HinSchG-Hinweisgeberportal. Konkreter Sprint-Plan in §12.

### Phase 1.2 (Sprint 9–11, ~3 Wochen)

- KI-Tool-Inventar via M365 / Google Workspace API
- Erste echte Demos mit Pilot-Kunden, Feedback einarbeiten

### Phase 1.5 (Sprint 12–16, ~5 Wochen)

- Transparenzregister-Monitor
- Datenpannen-Notfall-Workflow
- TTDSG-Cookie-Scanner
- Self-Service-Sign-Up Light (Demo-Request → Tenant-Auto-Provisioning ohne Bezahlung)
- Sponty-Style ARM64-Build-Optimierungen wenn Build-Zeiten lästig werden

### Phase 2 (Monat 6–10)

- DPA/AV-Vertragsmanagement
- Phishing-Simulation (white-label SoSafe oder eigene Light-Version)
- NIS2-Basis-Modul
- Vulnerability-Scan-Light (Partner-Integration)
- LLM-Switch zu Anthropic Claude (bezahlt, höhere Qualität)
- Sentry Team-Plan, Plausible Pro-Plan

### Phase 3 (Monat 10–16)

- ISO-27001-Evidence-Sammler
- ISO-42001-Modul
- Arbeitsschutz / Gefährdungsbeurteilung
- Auditor-Export (OSCAL/PDF)

### Phase 4 (Monat 16–22)

- Live-Compliance-Status / Ops-Cockpit
- Versicherungs-Renewal-Cockpit
- Branchen-Pakete (GwG für Immobilien, MDR für Medizin)
- Migration zu Frankfurt-Server wenn DSGVO-DE-Forderungen häufen

## 11.5 Pre-Sprint-1 Prerequisites (Pflicht vor Code-Start)

| Prerequisite | Verantwortlich | Status |
|---|---|---|
| **Naming-Session** abschließen → Name **Vaeren** | Konrad + Claude | ✅ erledigt 2026-04-27 |
| **`vaeren.de`-Domain registrieren** bei Hetzner | Konrad | ✅ erledigt 2026-04-27 (4,90 €/Jahr, Auto-Renewal) |
| **DNS für vaeren.de einrichten** in Hetzner DNS Console (Records `@`, `app`, `*.app`, `hinweise`, `www` → 204.168.159.236) | Konrad | ✅ erledigt 2026-04-27 |
| **Hetzner-DNS-API-Token** für Caddy DNS-Challenge generieren | Konrad | offen (vor Sprint 8) |
| **OpenRouter-Account** + API-Key | Konrad | offen |
| **Mailjet-Account** + API-Keys, Domain-Verifizierung mit SPF/DKIM/DMARC für vaeren.de | Konrad | offen (vor Sprint 4) |
| **Sentry-EU-Account** | Konrad | offen |
| **Anwaltliche DPMA + EUIPO Markenrecherche** für „Vaeren" und Wortmarken-Anmeldung Klassen 9/35/42 (~500–800 € + 290 € DPMA-Gebühr) | Konrad | offen (vor Pilot-Kunden-Vertrag, idealerweise vor Sprint 4) |

**Geschätzter Aufwand:** ~3–5 Std verteilt auf 1 Woche (vor Sprint 1).

## 12. Sprint-Plan MVP (8 Wochen) — ✅ abgeschlossen 2026-05-10

| Sprint | Status | Hauptziel |
|---|---|---|
| 1 | ✅ | Foundation: Repo + Django + Multi-Tenancy + Auth + Test-Tenant |
| 2 | ✅ | Shared Core Models + DRF API + AuditLog + Multi-Tenant-Tests |
| 3 | ✅ | Frontend-Foundation: React + Login + MFA + Mitarbeiter-CRUD + Demo-Form |
| 4 | ✅ | Pflichtunterweisungs-Modul: Kurs + Schulungs-Wizard + Mail + LLM-Personalisierung + Quiz + Zertifikat-PDF |
| 5 | ✅ | HinSchG-Modul: Verschlüsselte Meldungen (Fernet, custom EncryptedTextField) + Bearbeiter-Dashboard + Frist-Tracking |
| 6 | ✅ | Cockpit: Score-Donut + KPI-Karten + ToDo-Liste + Activity-Feed + Notification-Bell + AuditLog-Viewer + Settings (Sidebar-Layout) |
| 7 | ✅ | Tests: pytest-cov 86 %+ Baseline + CI-Gate `--cov-fail-under=80` + Storybook + Playwright (8 E2E-Specs nur main) |
| 8 | ✅ | Production-Deploy: Caddy-Container statt Host-Service + Brevo statt Mailjet (Anti-Abuse-Block) + restic-Backup + GlitchTip statt Sentry-SaaS |

**Tatsächlicher Aufwand:** ~80 h verteilt auf ~3 Wochen real-time (statt 8 Wochen nominell). Spec-Schätzung war konservativ — alle Sprints unter time-cap durch.

**Live seit 2026-05-10** auf 5 Domains (`app.vaeren.de`, `hinweise.app.vaeren.de`, `errors.app.vaeren.de`, `vaeren.de`+`www.vaeren.de`-Apex-Redirect). Sponty parallel unverändert.

**Abweichungen von der Original-Spec** (alle dokumentiert in CLAUDE.md):
- LLM-Modelle (Sprint 4): Spec sagte `gemini-2.5-flash:free` + `mistral-small-3.2:free` — beide existieren nicht mehr im OpenRouter-Lineup, ersetzt durch `gemma-4-26b-a4b-it:free` + `nemotron-3-super-120b-a12b:free`
- Encryption (Sprint 5): Spec sagte `django-cryptography` — Paket ist abandoned, eigener `EncryptedTextField` auf `cryptography.fernet` stattdessen
- Mail-Provider (Sprint 8): Spec sagte Mailjet — Mailjet-Free-Account wurde durch Anti-Abuse beim ersten API-Call gesperrt, durch Brevo (300/Tag, EU-Hosting) ersetzt
- Reverse-Proxy (Sprint 8): Spec sagte Caddy als Host-Service — Container-Variante gewählt für saubere Docker-DNS
- Monitoring (Sprint 8): Spec sagte Sentry-EU-SaaS — GlitchTip self-hosted gewählt für DSGVO + kein Vendor-Lock

## 13. Pricing & Vertragskonditionen (aus Vorgänger-Spec)

| Tier | MA-Range | Listenpreis/Jahr | Pilot (40% Rabatt, erste 10) |
|---|---|---|---|
| Starter | 50–120 MA | 4.800 € | 2.880 € |
| Professional | 121–250 MA | 9.600 € | 5.760 € |
| Business | 251–500 MA | 19.200 € | 11.520 € |

Jahresvertrag, Onboarding 1.500 € (Pilot frei), Hosting Helsinki (EU-DSGVO).

## 14. Risiken & Mitigationen

Aus Vorgänger-Spec übernommen + architektur-spezifisch ergänzt:

| Risiko | Mitigation |
|---|---|
| RDG-Falle | 3-Layer-Schutz (Prompt + Validator + HITL), siehe §8 |
| django-tenants-Quirks (z. B. mit allauth-2fa) | Sprint 1: Smoke-Test mit allen 3 Libs früh |
| LLM-Free-Tier-Rate-Limits brechen Demo | Fallback auf statische Templates |
| Caddy-Migration brichts Sponty | Geplantes Wartungsfenster, Rollback-Plan |
| Solo-Bootstrap-Burnout | Hard-Cap 10–12h/Woche, Sprint-Scope reduzieren statt mehr Stunden |
| LLM-Output-Qualität auf Free-Tier zu schlecht | Sprint 4: mit echten Beispiel-Mails testen, ggf. Switch zu Anthropic |
| Helsinki vs. Frankfurt Sales-Blocker | Migrations-Pfad dokumentiert, Trigger ab 5 Pilot-Kunden mit „muss DE sein" |
| Cross-Tenant-Datenleak | Multi-Tenant-Isolation-Test als kritisches CI-Gate |

## 15. Offene Fragen / Future Work

- **Kanzlei-Auswahl** spätestens Sprint 4 — Output-Texte brauchen Legal-Review (3 Top-Kandidaten aus Vorgänger-Spec: SKW Schwarz, Heuking, Taylor Wessing)
- ~~DNS-Provider-Entscheidung~~ entschieden 2026-04-27: **Hetzner DNS** (EU-clean, kostenlos, gleiche Verwaltung wie Server, `caddy-dns/hetzner` Plugin für Wildcard-Cert)
- **Marketing-Site Tech-Stack:** Phase 1 als Django-Templates aus dem ai-act-Container, Phase 2 evtl. separates Astro/Nuxt für SEO-Boost
- **Sentry vs. GlitchTip self-hosted:** Sentry-EU im MVP, GlitchTip-Switch ab 50+ Tenants wenn Sentry-Kosten steigen
- **Tenant-Subdomain-Strategie:** Pro Subdomain (z. B. `acme.app.vaeren.de`) oder unter Ein-Subdomain mit Pfad-Routing? Spec setzt Subdomain — bei DNS-Limit-Treffern (Hetzner DNS hat keine harten Limits für Wildcard, aber ggf. Rate-Limits beim Cert-Renewal von Let's Encrypt) revaluieren
- **HinSchG-Encryption-Key-Rotation:** Wie wird der Tenant-Schlüssel rotiert wenn z. B. ein User ausscheidet, der ihn kannte? Spec für Phase 2

(Pre-Sprint-1 Prerequisites siehe §11.5)

## 16. Glossar-Referenz

Alle Fachbegriffe in `~/.claude/projects/-home-konrad-ai-act/memory/glossar_compliance.md`. Architektur-spezifische Begriffe:

- **HITL** — Human-in-the-Loop, Mensch klickt final
- **ASGI** — Async Server Gateway Interface (Daphne, Uvicorn)
- **OpenAPI / Swagger** — API-Schema-Spezifikation
- **drf-spectacular** — Django-DRF-Library, generiert OpenAPI-Schema
- **TOTP** — Time-Based One-Time Password (RFC 6238), MFA-Standard
- **AVV / DPA** — Auftragsverarbeitungsvertrag / Data Processing Agreement
- **OSCAL** — NIST Open Security Controls Assessment Language

## 17. Versionsverlauf

| Datum | Änderung | Autor |
|---|---|---|
| 2026-04-24 | Initial-Version, durch Brainstorming-Session validiert | Konrad Bizer + Claude |
