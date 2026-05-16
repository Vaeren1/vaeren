# Plausible Analytics — self-hosted für Vaeren

> **Stand:** 2026-05-16
> **Status:** Stack-Definition + Setup-Anleitung. Erstinstallation manuell.

Plausible ist ein leichtgewichtiges, DSGVO-konformes Analytics-System.
Im Gegensatz zu Google Analytics werden weder Cookies gesetzt noch
personenbezogene Daten verarbeitet. Daher kein Cookie-Banner nötig.

## Architektur

```
stats.vaeren.de  →  Caddy  →  plausible:8000
                              ├─ plausible-postgres (App-DB)
                              └─ plausible-clickhouse (Event-DB, säulenorientiert für Aggregationen)
```

Eigenes Netzwerk `plausible-net`, getrennt vom Vaeren-Stack. Kein Datenfluss
zwischen den Stacks außer durch Caddy.

## Initial-Setup auf dem Server

```bash
# 1. Verzeichnis + Dateien
mkdir -p /opt/plausible
cd /opt/plausible
# Stack-Definition vom Repo ziehen:
scp -r konrads-laptop:/home/konrad/ai-act/infrastructure/plausible/* .

# 2. Secrets generieren
cp .env.example .env
SECRET_KEY=$(openssl rand -hex 32)
TOTP_KEY=$(openssl rand -hex 32)
DB_PW=$(openssl rand -hex 24)
sed -i "s|CHANGE_ME_SECRET|$SECRET_KEY|" .env
sed -i "s|CHANGE_ME_TOTP|$TOTP_KEY|" .env
sed -i "s|CHANGE_ME_DB|$DB_PW|" .env
chmod 600 .env

# 3. Stack hochfahren
docker compose up -d

# 4. Caddy ins plausible-net hängen
docker network connect plausible-net caddy

# 5. Caddy reload (Caddyfile-Block für stats.vaeren.de muss aktiv sein)
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS-Voraussetzung

`stats.vaeren.de` A-Record auf `204.168.159.236` setzen (Hetzner-Robot-DNS).
TTL: 300.

## Admin-User anlegen

Da `DISABLE_REGISTRATION=true` gesetzt ist, muss der erste User über die
Console erstellt werden:

```bash
docker exec -it plausible /entrypoint.sh seed
# Oder via mix-task wenn seed fehlt:
docker exec -it plausible bin/plausible remote
# > Plausible.Auth.User.changeset(%Plausible.Auth.User{}, %{email: "konrad@...", password: "...", name: "Konrad"}) |> Plausible.Repo.insert!
```

Alternativ: kurzfristig `DISABLE_REGISTRATION=false` setzen, sich
registrieren, dann wieder zurückstellen.

## Site anlegen

Nach Login im Plausible-Dashboard: **Add Website**, Domain `vaeren.de`,
Zeitzone `Europe/Berlin`. Plausible zeigt einen JavaScript-Snippet —
der ist in Vaerens Marketing-Site bereits eingebaut:

```html
<script defer data-domain="vaeren.de" src="https://stats.vaeren.de/js/script.js"></script>
```

(siehe `marketing/src/components/Layout.astro`)

## Monitoring

```bash
# Status
docker compose ps

# Logs
docker compose logs -f plausible

# DB-Größe
docker exec plausible-postgres psql -U plausible plausible_db -c "SELECT pg_size_pretty(pg_database_size('plausible_db'))"

# Backup ist in restic-Daily-Backup eingeschlossen
# (Volumes: plausible-postgres-data + plausible-clickhouse-data)
```

## Datenschutz-Hinweise

Plausible setzt nach eigener Angabe **keine Cookies** und erhebt **keine
personenbezogenen Daten**. IP-Adressen werden via hashed-Daily-Salt
anonymisiert. Damit ist Plausible nach DSGVO ohne Cookie-Banner
zulässig.

Vaerens Datenschutzerklärung erwähnt Plausible bereits (siehe
`marketing/src/data/static-content.ts → DATENSCHUTZ.analyse`).
