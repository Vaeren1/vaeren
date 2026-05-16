# Vaeren Production-Runbook (Sprint 8)

Schritt-für-Schritt für den ersten go-live von Vaeren auf dem Hetzner-Server,
co-located mit Sponty. Jeder Schritt mit erwarteter Ausgabe + Rollback.

---

## A. Vor-Deploy-Checks (5 min)

### A.1 Sponty läuft

```bash
ssh hel1 'cd /opt/sponty && docker compose -f docker-compose.prod.yml ps'
```

Erwartet: alle 7 Container `Up (healthy)` oder `Up`.

### A.2 DNS-Records aktiv

```bash
dig +short app.vaeren.de
dig +short hinweise.app.vaeren.de
dig +short sponty.fun
```

Alle drei → `204.168.159.236`.

### A.3 Lokal: alles grün

```bash
cd ~/ai-act
docker compose -f docker-compose.dev.yml up -d
cd backend && uv run pytest -q
cd ../frontend && bun run typecheck && bun run build
```

### A.4 `.env.production` existiert + ist NICHT committed

```bash
[[ -f .env.production ]] && echo "ok" || echo "FEHLT"
git status --short .env.production  # darf nichts zeigen
```

### A.5 Backup von Sponty-nginx-Config (für Rollback)

```bash
mkdir -p ~/sponty-rollback
ssh hel1 'cat /opt/sponty/nginx-ssl.conf' > ~/sponty-rollback/nginx-ssl.conf
ssh hel1 'cat /opt/sponty/docker-compose.prod.yml' > ~/sponty-rollback/docker-compose.prod.yml
echo "Rollback-Files: ~/sponty-rollback/"
```

---

## B. Phase 1: ai-act-Stack initial deployen (~10 min, KEIN Sponty-Risiko)

In dieser Phase startet ai-act im internen Docker-Netz. Sponty bleibt unangetastet,
weil die Vaeren-Container keine Host-Ports belegen.

### B.1 Deploy

```bash
cd ~/ai-act
./deploy.sh --logs
```

Erwartet:
```
=== Vaeren Deploy → root@204.168.159.236:/opt/ai-act ===
[1/5] SSH-Erreichbarkeit prüfen …
ssh-ok: aarch64
[2/5] Remote-Verzeichnis vorbereiten …
[3/5] Code via rsync synchronisieren …
[4/5] .env.production hochladen …
[5/5] Container bauen + starten …
…
[+] Building 5/5 …
[+] Running 6/6 …
 ✔ Container vaeren-postgres        Healthy
 ✔ Container vaeren-redis           Healthy
 ✔ Container vaeren-django          Started
 ✔ Container vaeren-celery-worker   Started
 ✔ Container vaeren-celery-beat     Started
 ✔ Container vaeren-frontend        Started
```

### B.2 Health-Check (intern)

```bash
ssh hel1 'docker exec vaeren-django curl -sf http://localhost:8000/api/health/'
# erwartet: {"status":"ok","schema":"public"}

ssh hel1 'docker exec vaeren-frontend wget -qO- http://localhost/healthz'
# erwartet: ok
```

### B.3 Ersten Tenant + GF-User anlegen

```bash
ssh hel1 'docker exec -it vaeren-django python manage.py create_tenant \
    --schema demo --firma "Vaeren Demo GmbH" --domain app.vaeren.de --pilot'

ssh hel1 'docker exec -it vaeren-django python manage.py shell' <<'PY'
from django_tenants.utils import schema_context
from core.models import User, TenantRole
with schema_context("demo"):
    u = User.objects.create_user(
        email="konrad@vaeren.de",
        password="<starkes-passwort>",
        tenant_role=TenantRole.GESCHAEFTSFUEHRER,
        is_active=True,
    )
    print(f"Created: {u}")
PY
```

**Stop-Punkt:** Sponty läuft weiter, Vaeren ist intern bereit. Caddy-Switch = nächste Phase, **nur** wenn Phase 1 grün.

---

## C. Phase 2: Caddy-Switch (Wartungsfenster, ~5–15 min Sponty-Downtime)

### C.1 Konrad informiert ggf. Sponty-User

(Falls aktive Sponty-Demo läuft: kurz Bescheid geben.)

### C.2 Caddy installieren

```bash
ssh hel1 << 'EOF'
set -e
apt-get update
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
    gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
    tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update && apt-get install -y caddy
systemctl stop caddy           # wir starten gleich kontrolliert
systemctl disable caddy        # eigene Unit ersetzt das Default
EOF
```

### C.3 Caddyfile + caddy.service deployen

```bash
ssh hel1 'mkdir -p /etc/caddy'
scp /home/konrad/ai-act/infrastructure/Caddyfile hel1:/etc/caddy/Caddyfile
scp /home/konrad/ai-act/infrastructure/caddy.service hel1:/etc/systemd/system/caddy.service
ssh hel1 'systemctl daemon-reload'
```

### C.4 Sponty-nginx stoppen (Sponty-Downtime startet HIER)

```bash
ssh hel1 'docker stop sponty-nginx sponty-certbot'
```

→ sponty.fun ist ab jetzt **offline**, bis Caddy übernimmt.

### C.5 Caddy in beide Docker-Netze einhängen

```bash
ssh hel1 << 'EOF'
# Caddy braucht Netz-Zugriff zu sponty-backend UND vaeren-django.
# Wir schaffen ein gemeinsames Bridge-Netz, in dem beide Stacks + Caddy hängen.
docker network create caddy-net 2>/dev/null || true
docker network connect caddy-net sponty-backend || true
docker network connect caddy-net vaeren-django || true
docker network connect caddy-net vaeren-frontend || true
EOF
```

**Wichtig:** Damit Caddy den Container per Hostname `sponty-backend` / `vaeren-django` erreicht, muss Caddy entweder als Container im selben Netz oder als Host-Service mit DNS-Resolver-Trick laufen. Da Caddy als systemd-Service auf Host-Ebene läuft, brauchen wir die Container-IPs:

```bash
ssh hel1 << 'EOF'
docker inspect sponty-backend  | grep IPAddress | head -2
docker inspect vaeren-django   | grep IPAddress | head -2
docker inspect vaeren-frontend | grep IPAddress | head -2
EOF
```

→ Trage diese IPs INS Caddyfile statt der Hostnames ein, ODER deploye Caddy stattdessen als Container im `caddy-net`.

**Empfehlung (sauberer):** Caddy als Container, siehe §D.

### C.6 (Variante A — Caddy als systemd) Caddy starten

```bash
ssh hel1 'systemctl start caddy && systemctl status caddy --no-pager'
```

Erwartet: `active (running)`. Logs: `journalctl -u caddy -f`.

Caddy holt Let's-Encrypt-Certs für sponty.fun + app.vaeren.de + hinweise.app.vaeren.de
(jeweils HTTP-01-Challenge — Caddy belegt nur 80/443, das geht).

### C.7 Smoke-Tests (Sponty-Downtime endet HIER)

```bash
curl -sIL https://sponty.fun/                 | head -1   # HTTP/2 200
curl -sIL https://app.vaeren.de/              | head -1   # HTTP/2 200
curl -sIL https://hinweise.app.vaeren.de/     | head -1   # HTTP/2 200
```

### C.8 Wenn Smoke fehlschlägt → ROLLBACK

```bash
ssh hel1 << 'EOF'
systemctl stop caddy
docker start sponty-nginx sponty-certbot
EOF

# Wartung beendet, sponty wieder up. ai-act bleibt intern.
# Caddy-Switch verschoben, untersuche Ursache.
```

---

## D. Variante B: Caddy als Container (empfohlen, sauberer)

Wenn Caddy-als-systemd Probleme macht, alternativ einen Caddy-Container als
Host-Service (Port 80/443 binden) im `caddy-net` starten:

```yaml
# /opt/caddy/docker-compose.yml
services:
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - caddy-net

networks:
  caddy-net:
    external: true

volumes:
  caddy_data:
  caddy_config:
```

```bash
ssh hel1 'mkdir -p /opt/caddy && docker network create caddy-net 2>/dev/null || true'
scp /opt/caddy/docker-compose.yml hel1:/opt/caddy/
ssh hel1 'docker stop sponty-nginx sponty-certbot'
ssh hel1 'docker network connect caddy-net sponty-backend && \
          docker network connect caddy-net vaeren-django && \
          docker network connect caddy-net vaeren-frontend'
ssh hel1 'cd /opt/caddy && docker compose up -d'
```

In diesem Setup funktionieren die Hostnames im Caddyfile direkt
(`vaeren-django:8000`, `sponty-backend:8000`).

---

## E. Post-Deploy

- [ ] Login-Test: `https://app.vaeren.de/login` mit dem Phase-B-User
- [ ] HinSchG-Test: anonyme Meldung über `https://hinweise.app.vaeren.de/hinweise`
- [ ] Audit-Log-Test: GF sieht Login-Eintrag
- [ ] Compliance-Cockpit lädt mit Score (~100, weil keine Tasks)
- [ ] Sponty läuft weiter: `https://sponty.fun/`

---

## F. Wenn Phase-1 (B) fehlschlägt

- ai-act-Container weg: `ssh hel1 'cd /opt/ai-act && docker compose -f docker-compose.prod.yml down -v'`
- Sponty bleibt unverändert, kein Schaden.
- Lokal Logs analysieren: `ssh hel1 'cd /opt/ai-act && docker compose -f docker-compose.prod.yml logs vaeren-django --tail=200'`

## G. Wenn Phase-2 (C) fehlschlägt → siehe §C.8

---

## H. Backup aktivieren (sobald Hetzner-Storage-Box vorhanden)

Stand 2026-05-09 erfolgreich auf u591277.your-storagebox.de durchgeführt.
Wichtige Lessons learned:

1. **Storage-Box-Bestellung**: SSH-Support + Äußere Erreichbarkeit aktivieren
   (sonst kein Port 23, kein restic). Public-Key beim Bestellen einsetzen.
2. **Hetzner Storage Box hört auf Port 23, nicht 22** (Port 22 ist SFTP-only).
3. **Pfad relativ zum SFTP-Home**, NICHT absolut (`vaeren-restic` statt `/vaeren-restic`).
4. **SSH-Config statt RESTIC_SFTP_COMMAND** — restic ignoriert die env-Variable;
   stattdessen Host-Eintrag in `/root/.ssh/config_vaeren_backup` (siehe unten).

```bash
ssh hel1
mkdir -p /etc/vaeren && chmod 700 /etc/vaeren

# Dedizierter Backup-Key
ssh-keygen -t ed25519 -N "" -f /etc/vaeren/backup_id_ed25519 \
    -C "vaeren-backup@$(hostname)-$(date +%Y%m%d)"
chmod 600 /etc/vaeren/backup_id_ed25519
# Public-Key in Hetzner-Console pro-Box einsetzen (NICHT nur Account-weit!)
cat /etc/vaeren/backup_id_ed25519.pub

# SSH-Config für Storage-Box-Host (Port 23 + Key)
cat > /root/.ssh/config_vaeren_backup <<'EOF'
Host uXXXXXX.your-storagebox.de
    User uXXXXXX
    Port 23
    IdentityFile /etc/vaeren/backup_id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 /root/.ssh/config_vaeren_backup
grep -q config_vaeren_backup /root/.ssh/config 2>/dev/null || \
    echo "Include /root/.ssh/config_vaeren_backup" >> /root/.ssh/config

# restic-Passwort + env (relativer Pfad!)
python3 -c "import secrets; print(secrets.token_urlsafe(40))" > /etc/vaeren/restic.passwd
chmod 600 /etc/vaeren/restic.passwd
cat > /etc/vaeren/restic.env <<EOF
export RESTIC_REPOSITORY="sftp:uXXXXXX@uXXXXXX.your-storagebox.de:vaeren-restic"
export RESTIC_PASSWORD_FILE="/etc/vaeren/restic.passwd"
EOF
chmod 600 /etc/vaeren/restic.env

apt-get install -y restic
source /etc/vaeren/restic.env
restic init    # → "created restic repository ... at sftp:..."

# Erster Backup-Lauf
/opt/ai-act/infrastructure/restic-backup.sh

# Restore-Verify (sollte Tenant-Encryption-Key in pg_dump enthalten)
mkdir -p /tmp/restore-probe
restic restore latest --target /tmp/restore-probe
zcat /tmp/restore-probe/var/lib/vaeren-restic/*.sql.gz | grep encryption_key

# Cron 03:00 täglich
( crontab -l 2>/dev/null | grep -v vaeren-restic; \
  echo '0 3 * * * /opt/ai-act/infrastructure/restic-backup.sh > /var/log/vaeren-restic.log 2>&1' \
) | crontab -
```

---

## I. Konrads Account-TODO-Liste (vor go-live)

| Account | Aufwand | Status |
|---|---|---|
| Mailjet (mit `vaeren.de` SPF/DKIM/DMARC) | ~30 min + 24 h Propagation | ❌ tot (Anti-Abuse-Block bei fresh-account) — durch Brevo ersetzt |
| Brevo (Mail-Provider, 300/Tag free, EU) | ~30 min | ✅ aktiv 2026-05-09 |
| OpenRouter API-Key | ~10 min | ✅ aktiv 2026-05-10 |
| Hetzner Storage Box (restic) | ~15 min | ✅ aktiv 2026-05-09, daily 03:00 |
| GlitchTip self-hosted (Sentry-API) | ~30 min | ✅ aktiv 2026-05-10 — `errors.app.vaeren.de` |
| DPMA-Wortmarken-Anmeldung | Anwalt, ~6 Mo | offen (vor Pilot-Vertrag) |

Auch ohne offene Punkte ist Vaeren **demo-fähig** dank Module-Fallbacks
(Console-Mail, Static-LLM, Console-Logging) — siehe Sprint 4/5/6/8 by-design.

---

## J. Operations — Wiederkehrende & gelegentliche Befehle

Alle Befehle laufen aus `/opt/ai-act/` auf dem Production-Server gegen
den Backend-Container. Vorlauf: `docker compose exec backend …`.

### J.1 Demo-Tenant pflegen

**Standard-Schulungskatalog seeden** (20 Pflicht-Kurse: DSGVO,
Arbeitsschutz, Brandschutz, Gefahrstoffe, PSA, Maschinen, Lärm,
Antikorruption, AGG, HinSchG, Gabelstapler, LkSG, GwG, Schweißen,
Ladungssicherung, Exportkontrolle, Umweltschutz, ISO 9001 …):

```bash
ssh hel1 'cd /opt/ai-act && docker compose exec backend \
    uv run python manage.py seed_kurs_katalog --tenant demo --dry-run'
# Treffer prüfen — dann ohne --dry-run:
ssh hel1 'cd /opt/ai-act && docker compose exec backend \
    uv run python manage.py seed_kurs_katalog --tenant demo'
```

Idempotent über Kurs-Titel: bestehende Kurse bleiben unverändert,
nur fehlende werden ergänzt. Sicher mehrfach ausführbar.

**E-Mail-Domain-Rewrite** (z. B. Demo-Daten von PayWise auf
vaeren-demo umstellen):

```bash
# Erst dry-run!
ssh hel1 'cd /opt/ai-act && docker compose exec backend \
    uv run python manage.py rename_emails \
        --tenant demo --from-domain paywise.de --to-domain vaeren-demo.de \
        --dry-run'
# Nach Prüfung der Liste — ohne --dry-run wiederholen:
ssh hel1 'cd /opt/ai-act && docker compose exec backend \
    uv run python manage.py rename_emails \
        --tenant demo --from-domain paywise.de --to-domain vaeren-demo.de'
```

Touched: `core.Mitarbeiter.email` + `core.User.email`, case-insensitivem
Suffix-Match. AuditLog-Eintrag pro Umbenennung mit
`actor_email_snapshot="system:rename_emails"`. Ziel-Email-Konflikte
werden übersprungen, nicht abgebrochen.

### J.2 Notifications

Stündlich via Celery-Beat. Manuell auslösen für Debugging:

```bash
ssh hel1 'cd /opt/ai-act && docker compose exec backend \
    uv run python manage.py dispatch_notifications --all-tenants'
```

### J.3 Backup-Status

```bash
ssh hel1 'tail -50 /var/log/vaeren-restic.log'
```

Restore-Übungs-Snippets in §H oben.

