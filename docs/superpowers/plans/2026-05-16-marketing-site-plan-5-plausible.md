# Marketing-Site Plan 5: Plausible Analytics (self-hosted)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Self-hosted Plausible Analytics auf `stats.vaeren.de`. Marketing-Site bindet das Plausible-Script ein. Keine Cookies, kein Consent-Banner, DSGVO-konform.

**Architecture:** Eigener Compose-Stack `/opt/plausible/` mit Plausible + ClickHouse + Postgres-für-Plausible. Caddy proxied `stats.vaeren.de` → `plausible:8000`. Marketing-Site bindet `https://stats.vaeren.de/js/script.js` in `Layout.astro` ein.

---

## File Structure

```
infrastructure/plausible/
├─ docker-compose.yml         # Plausible + ClickHouse + Plausible-Postgres
├─ .env.example               # Plausible-spezifische Env-Vars
├─ clickhouse-config.xml      # ClickHouse-Tuning für Plausible
└─ README.md                  # Setup-Anleitung
```

Plus:
```
infrastructure/Caddyfile      # Modify: stats.vaeren.de-Block
marketing/src/components/Layout.astro  # Modify: Plausible-Script-Tag
```

---

## Task 1: Plausible-Compose-Stack

- [ ] **Step 1:** `infrastructure/plausible/docker-compose.yml` schreiben analog Sponty-Pattern, drei Services:
  - `plausible_db` (postgres:16-alpine, eigenes Volume)
  - `plausible_events_db` (clickhouse:24-alpine)
  - `plausible` (ghcr.io/plausible/community-edition:latest)
  - Healthchecks, restart unless-stopped, alle in eigenem Netzwerk `plausible-net`.
- [ ] **Step 2:** `infrastructure/plausible/.env.example` mit Plausible-Settings (SECRET_KEY_BASE, BASE_URL=https://stats.vaeren.de, DISABLE_REGISTRATION=true, etc.).
- [ ] **Step 3:** README mit Setup-Anleitung: erste Initialisierung, Admin-User anlegen, Site `vaeren.de` anlegen.
- [ ] **Step 4:** Commit.

## Task 2: Caddy-Routing

- [ ] `infrastructure/Caddyfile` ergänzen:
  ```caddyfile
  stats.vaeren.de {
      encode gzip zstd
      reverse_proxy plausible:8000 {
          header_up X-Forwarded-Proto https
          header_up X-Real-IP {remote_host}
          header_up Host {host}
      }
  }
  ```
- [ ] Caddy muss in `plausible-net` joinen — Doku im README.

## Task 3: Marketing-Site bindet Plausible ein

- [ ] `marketing/src/components/Layout.astro` ergänzen im `<head>`:
  ```astro
  <script defer data-domain="vaeren.de" src="https://stats.vaeren.de/js/script.js" is:inline></script>
  ```
- [ ] Build-Test: `bun run build` muss weiter laufen, Script-Tag im HTML.

## Task 4: Konrad-Onboarding

- [ ] **Konrad-Aufgabe:** DNS A-Record `stats.vaeren.de` → 204.168.159.236.
- [ ] **Konrad-Aufgabe:** Auf Server: Plausible-Stack hochfahren, Admin-User anlegen, Site `vaeren.de` registrieren.
- [ ] **Konrad-Aufgabe:** Plausible-Dashboard nach 24h checken — Sessions sollten erscheinen.

## Akzeptanz

Plan 5 ist abgeschlossen, wenn `stats.vaeren.de` ein Plausible-Dashboard mit Live-Daten von `vaeren.de` zeigt und die Marketing-Site keine Cookie-Banner / 3rd-Party-Tracker außer Plausible nutzt.

## Aufwand

Ca. 4 Stunden inkl. Konrads Onboarding-Schritte.
