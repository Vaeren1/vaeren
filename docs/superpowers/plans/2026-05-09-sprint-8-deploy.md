# Sprint 8 — Production-Deploy

> **Spec §12:** „Production-Deploy: Caddy-Migration + DNS + Backup + Erste Demo gegen Production-URL"
> **Aufwand:** ~10–14 h (zweiteilig: Build + Deploy).
> **Vorbedingung:** Sprint 1–7 ✅. Server SSH erreichbar, Sponty läuft stabil.
> **Sprint-Ende-Kriterium:** `https://app.vaeren.de/` lädt das Login. `https://hinweise.app.vaeren.de/` zeigt das anonyme HinSchG-Form. Sponty bleibt unterbrechungsfrei (oder mit klar dokumentiertem Wartungsfenster). `restic`-Backup läuft täglich. Health-Check + Smoke-Test grün.

---

## 0. Inventar-Status (2026-05-09 abend)

| Asset | Status |
|---|---|
| SSH zum Server | ✅ funktioniert (`root@204.168.159.236`) |
| Sponty | ✅ stabil up seit 2 Wochen, 7 Container, nginx-ssl auf 80/443 |
| Sponty `.env.production` | ✅ vorhanden, mit Cerebras-LLM + ACME-Email |
| Caddy auf Server | ❌ NICHT installiert |
| `/opt/ai-act/` | ❌ nicht angelegt |
| Hetzner DNS-Records | ✅ gesetzt (`@`, `app`, `*.app`, `hinweise`, `www` → 204.168.159.236) |
| Mailjet-Account + API-Keys | ❌ fehlt |
| OpenRouter-API-Key | ❌ fehlt |
| Sentry-EU-Project | ❌ fehlt |
| Hetzner Storage Box (für `restic`) | ❌ fehlt |
| Hetzner-DNS-API-Token (für Wildcard-Cert) | ❌ fehlt |

**Konsequenz:** Vollständiger Production-Betrieb braucht zusätzlich diese 5 Accounts. Sprint-8-Stack ist aber **demo-fähig auch ohne** durch Module-Fallbacks (Sprint 4/5 Design):
- Mailjet fehlt → Console-Backend (Mails ins Logfile)
- OpenRouter fehlt → Static-Fallback (vordefinierter Vorschlagstext)
- Sentry fehlt → Lokales Logging
- Storage Box fehlt → kein Backup (manuell oder TODO)
- Hetzner-DNS-API-Token fehlt → Caddy nutzt HTTP-01-Challenge statt DNS-01 (kein Wildcard-Cert für `*.app.vaeren.de`, sondern explizite Domains pro Tenant)

---

## 1. Architektur-Entscheidungen

| Entscheidung | Wahl | Begründung |
|---|---|---|
| **Caddy als Host-Service** | Caddy 2 als systemd-Service, ersetzt Sponty-nginx | Spec §3 + User-Wahl. Längerfristig sauberer (Auto-SSL, einfachere Domain-Anlage). Migration berührt Sponty live → Wartungsfenster nötig. |
| **Reverse-Proxy-Routing** | Per Domain in einem zentralen `Caddyfile`. Sponty + Vaeren parallel. | Single-source-of-truth. |
| **Wildcard-Cert** | **NICHT** im MVP — `caddy-dns/hetzner`-Plugin braucht API-Token (fehlt). Stattdessen explizite Hostnames. | YAGNI. Tenant-Subdomain-Anlage in Phase 2 automatisieren. |
| **Initial-Tenant-Domain** | `app.vaeren.de` (Multi-Tenant per Pfad oder einzelner Subdomain). MVP: Single-Tenant `app.vaeren.de` für die ersten Pilot-Demos. | Erst manuelle Tenant-Anlage; per-Tenant-Subdomain-Wildcard-Cert in Phase 2. |
| **HinSchG-Public-Subdomain** | `hinweise.app.vaeren.de` (DNS bereits gesetzt). | Spec §1: separate Domain pro Whistleblower-Channel. |
| **DB / Redis** | Eigene Container in `vaeren-postgres` / `vaeren-redis`. KEINE Mit-Nutzung der Sponty-DB. | Spec: Multi-Tenant-Isolation; Sponty-DB-Crash darf Vaeren nicht treffen. |
| **Frontend-Container** | `nginx-alpine` mit Vite-Build als Static. Caddy proxied auf den Container. | Trennt Frontend-Lifecycle vom Backend. |
| **Daphne (ASGI)** | Backend-Container startet `daphne config.asgi:application` auf `:8000`. | Spec §1 fordert ASGI für künftige WebSocket-Module. |
| **Celery** | Worker + Beat als separate Container. Beat ruft `dispatch_notifications --all-tenants` 1×/Stunde. | Sprint 6 Notification-Engine wird produktiv. |
| **Migrations** | `migrate_schemas --noinput` im Container-CMD vor Daphne-Start. | Spec §11: muss rückwärtskompatibel sein. |
| **Build-Strategy** | server-side ARM64-native Build (kein Cross-Compile). `docker compose build` läuft auf dem Server selbst. | Spec §11. |
| **Deploy-Trigger** | **manuell** durch `./deploy.sh` von Konrads Laptop. **Kein Auto-Deploy in CI.** | CLAUDE.md + Spec §11. |
| **Backup** | `restic` zu Hetzner Storage Box, täglich, retention 7 d / 4 w / 12 m. **Aktivierung erst nach Storage-Box-Account.** | Spec §11. |
| **Encryption-Key-Backup** | Tenant-Encryption-Keys liegen im Public-Schema → automatisch im `pg_dump` enthalten → automatisch im `restic`-Backup. | Sprint-5-Plan §5 dokumentiert: bei Key-Verlust = Datenverlust. |

---

## 2. Build-Phase (autonom, ohne Server-Risiko)

| # | Artefakt | Pfad |
|---|---|---|
| 1 | `backend/Dockerfile` (multi-stage, ARM64-native, WeasyPrint-Deps) | `backend/Dockerfile` |
| 2 | `frontend/Dockerfile` (bun-Build → nginx-static) | `frontend/Dockerfile` |
| 3 | `docker-compose.prod.yml` mit 6 Services | repo-root |
| 4 | `config/settings/prod.py` (Sentry, Mailjet, secure cookies, ALLOWED_HOSTS) | `backend/config/settings/prod.py` |
| 5 | `infrastructure/Caddyfile` mit Sponty + Vaeren Routes | `infrastructure/Caddyfile` |
| 6 | `infrastructure/caddy.service` (systemd-Unit) | `infrastructure/caddy.service` |
| 7 | `deploy.sh` analog Sponty + Differenzen-Hinweise | repo-root |
| 8 | `.env.production.example` mit allen Variablen + Kommentaren | `infrastructure/.env.production.example` |
| 9 | `infrastructure/restic-backup.sh` + cron-Snippet | `infrastructure/restic-backup.sh` |
| 10 | `infrastructure/RUNBOOK.md` (Schritt-für-Schritt Caddy-Switch + Rollback) | `infrastructure/RUNBOOK.md` |

---

## 3. Deploy-Phase (manuell, mit Konrad-Bestätigung pro Schritt)

### 3.1 Vor-Deploy-Checks

- [ ] Sponty grün: `ssh hel1 'cd /opt/sponty && docker compose -f docker-compose.prod.yml ps'`
- [ ] DNS-Auflösung: `dig app.vaeren.de A` → `204.168.159.236`
- [ ] Lokal grün: alle Tests + Build
- [ ] `.env.production` lokal erstellt (mit allen Werten oder `MAILJET_API_KEY=` für Console-Fallback)
- [ ] **Wartungsfenster** vereinbart (Sponty-Downtime ~5–15 min während Caddy-Switch)
- [ ] **Sponty-nginx-Config-Backup** auf Konrads Laptop gezogen

### 3.2 ai-act-Stack initial deployen (vor Caddy-Switch — kein Sponty-Risiko)

1. `./deploy.sh` synchronisiert Code + `.env`
2. Server-side: `docker compose -f docker-compose.prod.yml build` (~5 min ARM64-native)
3. Server-side: `docker compose up -d` startet Postgres + Redis + Backend + Celery + Frontend
4. Smoke via direkter Container-IP: `docker exec vaeren-django curl localhost:8000/api/health/`
5. Tenant anlegen: `docker exec vaeren-django python manage.py create_tenant --schema dev --firma "Vaeren Demo GmbH" --domain app.vaeren.de --pilot`

→ Bis hierhin **kein Sponty-Risiko**. ai-act läuft im internen Docker-Netz.

### 3.3 Caddy-Switch (Wartungsfenster, Sponty-Downtime ~5–15 min)

**Rollback-Vorbereitung:**
- Sponty-nginx-Config + cert-Verzeichnis auf Konrads Laptop gesichert
- Sponty-Container `sponty-nginx` + `sponty-certbot` `docker stop` (NICHT `down`)
- Sponty-Stack ohne nginx weiter up (Backend, DB, etc. erreichbar via Container-Netz für Caddy)

**Switch-Sequenz:**
1. `docker stop sponty-nginx sponty-certbot`
2. Caddy installieren: `apt install caddy`
3. `caddy.service` (systemd) + `Caddyfile` deployen
4. Caddy bekommt Zugriff auf Sponty-Backend via Docker-Network (`docker network connect`)
5. `systemctl start caddy` — holt Let's-Encrypt-Certs für sponty.fun + app.vaeren.de + hinweise.app.vaeren.de
6. Smoke-Test:
    - `curl -sI https://sponty.fun/` → 200
    - `curl -sI https://app.vaeren.de/` → 200
    - `curl -sI https://hinweise.app.vaeren.de/` → 200

**Rollback wenn Smoke fehlschlägt:**
- `systemctl stop caddy`
- `docker start sponty-nginx sponty-certbot`
- Sponty-Domains wieder grün; ai-act intern weiter erreichbar; Switch verschoben.

### 3.4 Post-Deploy

- [ ] First-User-Account anlegen: `docker exec vaeren-django python manage.py createsuperuser_in_tenant`
- [ ] Login auf `https://app.vaeren.de/login` testen
- [ ] HinSchG-Public-Form auf `https://hinweise.app.vaeren.de/hinweise` testen
- [ ] Sentry erreichbar (wenn DSN gesetzt)
- [ ] Mailjet-Test-Mail (wenn Keys gesetzt)
- [ ] `restic` täglichen Backup-Cron einrichten (wenn Storage-Box-Account da)

---

## 4. Risiko-Matrix

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|---|---|---|---|
| Caddy-Switch bricht Sponty | mittel | hoch | Wartungsfenster + Rollback-Plan in §3.3. Sponty-nginx-Config gesichert. |
| Let's-Encrypt-Rate-Limit | niedrig | mittel | Caddy holt nur fehlende Certs (3 Domains, Limit 50/Wo). |
| ARM64-Build bricht für native deps (cffi/cryptography) | niedrig | hoch | server-side Build, Dockerfile installiert build-essential. |
| `migrate_schemas` schlägt fehl im laufenden Container | mittel | hoch | Migrations sind rückwärtskompatibel + getestet (CI). Bei Fehler: Container-Restart-Loop, alte Version bleibt aktiv. |
| Mailjet/OpenRouter-Fallbacks nicht offensichtlich genug | mittel | niedrig | Static-Fallback hat sichtbares „Kein LLM verfügbar"-Banner. Console-Mail-Backend loggt prominent. |
| Encryption-Key-Verlust durch DB-Restore-Fehler | niedrig | sehr hoch | Public-Schema enthält `Tenant.encryption_key`; restic-Backup ist die einzige Versicherung. **Restore-Test** in Sprint 8b. |
| Konrad führt destruktive Schritte ohne mich | niedrig | mittel | Runbook ist präzise, jeder Schritt mit erwarteter Ausgabe + Rollback. |

---

## 5. Out-of-Scope (Sprint 8b oder später)

- Hetzner-DNS-API-Wildcard-Cert (braucht Token; manuelle Tenant-Anlage reicht für Pilot)
- Self-Service-Tenant-Onboarding (Spec §3 sagt: erst Phase 1.5)
- Auto-Deploy-Pipeline in CI (Spec §11: bewusst NICHT)
- Storage-Box `restic`-Backup (sobald Account da, ist es 1 systemd-timer + 1 cron-Job)
- Sentry-Integration (sobald DSN da, 5 Zeilen in `prod.py`)
- Mailjet-Domain-Verifizierung mit SPF/DKIM/DMARC
- Tenant-Restore-Drill (Sprint 8b: zerstöre dev-Tenant, restore aus Backup, prüfe ob Encryption funktioniert)
- Production-Smoke-Tests im CI (gegen `app.vaeren.de` post-deploy)
- HSTS + CSP-Header-Hardening (über Caddy easy)
- IPv6-Routing-Test (DNS hat AAAA-Records?)

---

## 6. Konrads-TODO-Liste vor go-live

(Diese Sprint-8-Vorbereitung erstellt nur die Code-Artefakte. Vor echtem go-live braucht Konrad zusätzlich:)

| Account | Zweck | Aufwand |
|---|---|---|
| Mailjet | Transaktionsmails | Account anlegen, Domain `vaeren.de` verifizieren, SPF/DKIM/DMARC-DNS setzen, API-Keys ins `.env.production` | ~30 min |
| OpenRouter | LLM-Personalisierung | API-Key generieren, Test-Call, Limit setzen | ~10 min |
| Sentry-EU | Error-Monitoring | Project anlegen (EU-Region), DSN ins `.env.production` | ~10 min |
| Hetzner Storage Box | Backup-Ziel | Storage Box bestellen (~4 €/Mo, 100 GB), SSH-Key hinterlegen, Pfad ins `.env.production` | ~15 min |
| (optional) Hetzner-DNS-API-Token | Wildcard-Cert für künftige Tenants | Read-Write-Token für Zone `vaeren.de` generieren | ~5 min |

**Gesamt-Account-Aufwand:** ~75 Min plus Mailjet-DNS-Propagation (24 h).
