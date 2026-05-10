# Infrastructure & Deployment

> **Stand:** 2026-05-10
> **Status:** ✅ Live in Production. Vaeren MVP deployed, alle 8 Sprints abgeschlossen, 5 Domains aktiv. Detail-Runbook in `RUNBOOK.md` (Schritt-für-Schritt-Wiederherstellung + Caddy-Switch + restic-Backup).

## Server

| Feld | Wert |
|---|---|
| Provider | Hetzner Cloud |
| Server-Typ | CAX31 (ARM64) |
| Standort | Helsinki, Finnland (`hel1`) |
| vCPU / RAM / Disk | 8 / 16 GB / 160 GB |
| Hostname | `ubuntu-16gb-hel1-3` |
| IPv4 | `204.168.159.236` |
| IPv6 | `2a01:4f9:c014:ef00::/64` |
| Monatskosten | ~19 € (gesamtserver, geteilt mit Sponty) |
| OS | Ubuntu (16gb-Image) |
| Kernel-Arch | `aarch64` (ARM64) |

## SSH-Zugang

```bash
ssh root@204.168.159.236
```

Login funktioniert via bereits hinterlegtem SSH-Key (gleicher Key wie für Sponty-Deployment). Der Key liegt in `~/.ssh/` auf der Workstation und ist auf dem Server in `~/.ssh/authorized_keys` registriert.

**Optional — SSH-Config-Eintrag** (in `~/.ssh/config` ergänzen, um statt der IP einen Alias zu nutzen):

```
Host hel1
    HostName 204.168.159.236
    User root
```

Dann reicht: `ssh hel1`.

## Co-Location-Architektur

Auf dem Server laufen drei unabhängige Stacks parallel als Docker-Compose:

```
/opt/sponty/        — Sponty-Stack (Django+Postgres+Redis+Meilisearch+Backend+Celery)
                     Container-Prefix: sponty-*
                     Domains: sponty.fun, www.sponty.fun, api.sponty.fun
                     Eigenes Postgres + Redis (DB-Volume seit Monaten persistent)

/opt/ai-act/        — Vaeren-Stack (Django+Postgres+Redis+Daphne+Celery+Frontend-nginx)
                     Container-Prefix: vaeren-*
                     Domains: app.vaeren.de, hinweise.app.vaeren.de, vaeren.de(redir)
                     Eigenes Postgres + Redis (Tenant-Daten, HinSchG-encrypted)

/opt/glitchtip/     — GlitchTip self-hosted (Sentry-API für Production-Error-Tracking)
                     Container-Prefix: glitchtip-*
                     Domain: errors.app.vaeren.de
                     Eigenes Postgres + Redis (Issue-History, getrennt von Vaeren)

/opt/caddy/         — Reverse-Proxy-Container (Port 80/443) — ersetzt seit 2026-05-09
                     den ursprünglichen sponty-nginx. Routet nach Hostname auf
                     Sponty-Backend / Vaeren-Stack / GlitchTip / Apex-Redirect.
                     Auto-SSL via Let's Encrypt, alle Stacks im `caddy-net`.
```

### Reverse-Proxy: Caddy als Container im `caddy-net`

Spec §3 hatte ursprünglich Caddy als Host-Service vorgesehen. **Stand 2026-05-09:** Caddy läuft als Container — sauberer, weil DNS-Resolution via Docker-Bridge (`vaeren-django:8000`, `sponty-backend:8000`, `glitchtip-web:8000`) ohne systemd-resolver-Tricks funktioniert. Alle drei Stacks plus Caddy hängen im gemeinsamen `caddy-net`-Bridge-Netzwerk; bei Container-Recreate muss Caddy ggf. neu connected werden.

Caddyfile-Quelle: `/home/konrad/ai-act/infrastructure/Caddyfile` → wird per `scp` nach `/opt/caddy/Caddyfile` deployt + `docker exec caddy caddy reload --config /etc/caddy/Caddyfile` (zero-downtime).

## Deployment-Pattern (analog zu Sponty)

Sponty nutzt folgendes Pattern (Vorlage `/home/konrad/sponty/deploy.sh`):

1. `rsync` synchronisiert Quelldateien zum Server (`/opt/sponty/`)
2. `scp .env.production` kopiert Production-Secrets in `/opt/sponty/.env`
3. `ssh ... docker compose -f docker-compose.prod.yml up -d --build`

ai-act folgt demselben Pattern mit `/opt/ai-act/` als Zielverzeichnis.

**Wichtig zu Secrets:**
- `.env.production` wird **NICHT** ins Repo committet (`.gitignore`)
- Gleiches Schema wie Sponty: lokal `.env.production` halten, per `scp` aufs Deployment ziehen
- Schlüssel-Inhalt (DB-Passwort, Django-Secret, Anthropic-API-Key, Mailjet-Token, etc.) wird separat verwaltet

## DSGVO-Implikation: Helsinki vs Frankfurt

Helsinki (Finnland) ist EU-Mitglied, DSGVO gilt voll, **AVV-konform**. Aber:

- Im B2B-Vertrieb fragen viele KMU-Compliance-Beauftragte „wo stehen die Server?". Antwort „Finnland (EU)" ist juristisch perfekt, aber psychologisch schwächer als „Frankfurt".
- Zum MVP-Launch akzeptabel.
- **Migrations-Pfad:** Wenn 5+ Pilot-Kunden tatsächlich „Hosting in DE" als Sales-Blocker nennen, eigenen CAX31 in Hetzner-Frankfurt (`fsn1` oder `nbg1`) provisionieren und ai-act dorthin migrieren. Sponty bleibt in Helsinki.
- **Sales-Sprache jetzt:** „Hosting in der EU, ISO-27001-zertifizierte Hetzner-Infrastruktur, DSGVO-konformer AVV". Standort-Frage ehrlich beantworten, nicht verstecken.

## Ressourcen-Auslastung (Stand 2026-04-27)

- Disk: 11 GB / 160 GB (8% — viel Reserve)
- CPU: 8 vCPU geteilt zwischen Sponty + ai-act (nominell ausreichend für beide bei ~10 Pilot-Kunden)
- RAM: 16 GB geteilt (Postgres + Redis + Backend + Celery × 2 Apps = ~6–8 GB Bedarf erwartet)

**Skalierungs-Trigger:** Wenn ai-act 20+ Tenants oder Sponty-Last steigt, separaten Server provisionieren (CAX21 für ai-act allein = 8 €/Monat).

## Backups (Stand 2026-05-09 live)

**Vaeren:** restic auf Hetzner Storage Box BX11 (Falkenstein, 3,81 €/Mo, 1 TB).
- Cron daily 03:00 Server-Zeit
- Inhalt: pg_dump (alle Tenant-Schemas inkl. encrypted HinSchG-Daten + Tenant-`encryption_key`s im public-Schema) + `vaeren-media`-Volume
- Retention: 7 daily, 4 weekly, 12 monthly snapshots
- **Restore-Verifikation 2026-05-09 erfolgreich** — Tenant-Encryption-Keys im Dump enthalten, HinSchG-Inhalte nach Restore wieder entschlüsselbar
- Keys in `/etc/vaeren/restic.passwd` (chmod 600, root-only)
- SSH-Backup-Key: `/etc/vaeren/backup_id_ed25519`

**Sponty:** unverändert — Hetzner-Snapshots + manuelle DB-Dumps. **Nicht auf restic migriert** (separater Job, hier nicht in scope).

**GlitchTip:** kein automatisches Backup. Wenn Issue-History-Verlust akzeptabel ist (neuer Setup = leerer Tracker, weiterhin funktional) → keine Aktion. Bei Bedarf zweites restic-Repo auf gleicher Storage-Box anlegen.

## Monitoring

**Production-Error-Tracking:** GlitchTip self-hosted unter `https://errors.app.vaeren.de`. Drop-in Sentry-API-kompatibel, Vaeren-Backend nutzt `sentry-sdk[django]` mit DSN-Switch in `.env.production`. Vorteil ggü. Sentry-SaaS: Daten EU-side (DSGVO), kein Quota, kein Vendor-Lock-in.

**Uptime + Performance:** noch nicht aufgesetzt. Optionen für später:
- UptimeRobot (extern, kostenlos, prüft alle 5 Min)
- Plausible Analytics für Website-Traffic (DSGVO-konform)
- Hetzner-Notifications via API für Server-Events

## Live-Container-Stand (2026-05-10)

```bash
$ ssh root@204.168.159.236 'docker ps --format "{{.Names}}: {{.Status}}"'

# Caddy (Reverse-Proxy, Port 80/443)
caddy: Up

# Vaeren-Stack
vaeren-django: Up (healthy)
vaeren-celery-worker: Up
vaeren-celery-beat: Up
vaeren-postgres: Up (healthy)
vaeren-redis: Up (healthy)
vaeren-frontend: Up (healthy)

# GlitchTip-Stack
glitchtip-web: Up
glitchtip-worker: Up
glitchtip-postgres: Up (healthy)
glitchtip-redis: Up (healthy)

# Sponty-Stack (parallel weiter live)
sponty-backend: Up (Wochen)
sponty-celery-worker: Up
sponty-celery-beat: Up
sponty-postgres: Up (healthy)
sponty-redis: Up (healthy)
sponty-meilisearch: Up (healthy)
# sponty-nginx + sponty-certbot: gestoppt seit Caddy-Switch
```

13 aktive Container. Sponty unverändert + Vaeren live + GlitchTip live + zentraler Caddy.
