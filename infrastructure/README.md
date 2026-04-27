# Infrastructure & Deployment

> **Stand:** 2026-04-27
> **Status:** Geplant für Co-Location mit Sponty auf bestehendem Hetzner-Server.

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

Auf dem Server laufen zwei unabhängige Apps parallel als Docker-Compose-Stacks:

```
/opt/sponty/        — bestehender Sponty-Stack (läuft seit Wochen stabil)
                     Container-Prefix: sponty-*
                     Ports: 80, 443 via sponty-nginx
                     Eigenes Postgres, Redis, Meilisearch, Backend, Celery

/opt/ai-act/        — neue ai-act-Stack (ai-act/ wird hier deployt)
                     Container-Prefix: ai-act-*
                     Ports: hochnummerierte (8080?) hinter zentralem Reverse-Proxy
                     Eigenes Postgres, Redis, Backend, Celery, Frontend
```

### Wichtig: Port- & Domain-Trennung

Beide Stacks brauchen Port 80/443 für ihre Domains. Lösungsoptionen:

**Variante A (empfohlen): Zentraler Reverse-Proxy**
- Aktuell: `sponty-nginx` belegt Port 80/443 und routet nur sponty-Domains
- Umbau: separater **Caddy-Container auf dem Host** (oder als eigener Compose-Stack), der Port 80/443 belegt und nach Domain auf Sponty-Backend bzw. ai-act-Backend routet
- Vorteil: Auto-SSL via Let's Encrypt, beide Apps profitieren, einfache Domain-Anlage

**Variante B: Sponty-Nginx erweitern**
- nginx-ssl.conf von Sponty bekommt zusätzliche `server { listen 443; server_name app.ai-act.de; ... }` Blöcke
- Vorteil: Weniger Container
- Nachteil: Config-Coupling beider Apps, Sponty-Deploy könnte ai-act stören

→ **Entscheidung in der MVP-Architektur-Spec festlegen.** Aktuelle Empfehlung: A.

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

## Backups

Sponty nutzt Hetzner-Snapshots + manuelle DB-Dumps (siehe `/home/konrad/sponty/docs/`). ai-act sollte das gleiche Pattern nutzen + zusätzlich:
- Tägliche pg_dump pro Tenant-Schema (oder Cluster-weite Dumps)
- Off-site Backup zu Hetzner Storage Box (verschlüsselt mit `restic`)

→ Detail-Spec in der MVP-Architektur-Spec.

## Monitoring (gemeinsam mit Sponty?)

Sponty hat aktuell kein dediziertes Monitoring. Vorschlag für ai-act:
- **Sentry (EU-Region)** für Error-Tracking — beide Apps können denselben Sentry-Account nutzen, separate Projekte
- **Plausible Analytics** für Website-Analytics (DSGVO-konform, EU-hosted)
- **Uptime-Monitoring** via UptimeRobot oder Hetzner-Notifications

## Test-Verbindung — bestätigt 2026-04-27

```bash
$ ssh root@204.168.159.236 'hostname && uname -m && docker ps --format "{{.Names}}"'
ubuntu-16gb-hel1-3
aarch64
sponty-backend
sponty-celery-worker
sponty-celery-beat
sponty-nginx
sponty-postgres
sponty-meilisearch
sponty-redis
```

Alle Sponty-Container laufen healthy. Server hat genug Reserve für Co-Location.
