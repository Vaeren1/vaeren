#!/usr/bin/env bash
# Vaeren Marketing-Site Auto-Rebuild.
#
# Wird vom Host-Cron alle 15 Minuten aufgerufen. Prüft, ob seit dem
# letzten Build neue published News-Posts in der DB sind. Wenn ja:
#   1. Astro-Build im docker-Netzwerk (kann vaeren-django:8000 erreichen)
#   2. rsync nach /var/www/vaeren-marketing/
#   3. Marker-Datei aktualisieren
#
# Idempotent: wenn nichts Neues, exit 0 ohne Build.
#
# Installation auf Server:
#   sudo cp /opt/ai-act/infrastructure/vaeren-marketing-rebuild.sh /usr/local/bin/
#   sudo chmod +x /usr/local/bin/vaeren-marketing-rebuild.sh
#   sudo tee /etc/cron.d/vaeren-marketing-rebuild >/dev/null <<EOF
#   */15 * * * * root /usr/local/bin/vaeren-marketing-rebuild.sh >> /var/log/vaeren-marketing-rebuild.log 2>&1
#   EOF

set -euo pipefail

MARKETING_DIR="${VAEREN_MARKETING_DIR:-/opt/ai-act/marketing}"
TARGET_DIR="${VAEREN_TARGET_DIR:-/var/www/vaeren-marketing}"
MARKER_FILE="${VAEREN_MARKER_FILE:-/var/www/vaeren-marketing/.last-build-utc}"
COMPOSE_FILE="${VAEREN_COMPOSE_FILE:-/opt/ai-act/docker-compose.prod.yml}"
LOCK_FILE="/var/run/vaeren-marketing-rebuild.lock"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"
}

# Verhindere Parallel-Läufe (Build dauert ~10s, Cron alle 15 min — aber sicher ist sicher).
exec 9>"$LOCK_FILE" || { log "Konnte Lock-File nicht öffnen, abbreche."; exit 1; }
if ! flock -n 9; then
    log "Anderer Rebuild läuft bereits, exit."
    exit 0
fi

# Hole das jüngste published-Timestamp aus der DB.
NEWEST_PUBLISH=$(docker compose -f "$COMPOSE_FILE" exec -T django python -c "
from redaktion.models import NewsPost, NewsPostStatus
p = NewsPost.objects.filter(status=NewsPostStatus.PUBLISHED).order_by('-published_at').first()
print(p.published_at.isoformat() if p and p.published_at else '')
" 2>/dev/null | tr -d '[:space:]' || true)

if [[ -z "$NEWEST_PUBLISH" ]]; then
    log "Keine published Posts in der DB — nichts zu tun."
    exit 0
fi

# Wenn Marker existiert und der Newest-Timestamp nicht neuer ist: nichts tun.
if [[ -f "$MARKER_FILE" ]]; then
    LAST_BUILD=$(cat "$MARKER_FILE")
    if [[ "$NEWEST_PUBLISH" <= "$LAST_BUILD" ]]; then
        # Keine neuen Posts seit letztem Build.
        exit 0
    fi
fi

log "Rebuild getriggert: newest_publish=$NEWEST_PUBLISH last_build=${LAST_BUILD:-(none)}"

cd "$MARKETING_DIR"
docker run --rm --network vaeren-net \
    -v "$MARKETING_DIR":/work -w /work \
    -e PUBLIC_API_BASE=http://vaeren-django:8000 \
    oven/bun:1-alpine bun run build

rsync -a --delete dist/ "$TARGET_DIR/"
echo "$NEWEST_PUBLISH" > "$MARKER_FILE"

log "Rebuild abgeschlossen."
