#!/usr/bin/env bash
# Vaeren Backup mit restic → Hetzner Storage Box (Sprint 8).
#
# Lebt auf dem Server unter `/opt/ai-act/infrastructure/restic-backup.sh`.
# Wird via cron 1×/Tag aufgerufen:
#   0 3 * * * /opt/ai-act/infrastructure/restic-backup.sh > /var/log/vaeren-restic.log 2>&1
#
# Voraussetzungen (Konrads-TODO vor go-live):
#   1. Hetzner Storage Box bestellt (~4 €/Mo, 100 GB)
#   2. SSH-Schlüssel auf der Storage-Box hinterlegt
#   3. /etc/vaeren/restic.env mit:
#        export RESTIC_REPOSITORY="sftp:u123456@u123456.your-storagebox.de:/vaeren-restic"
#        export RESTIC_PASSWORD_FILE="/etc/vaeren/restic.passwd"
#   4. `restic init` einmalig:
#        source /etc/vaeren/restic.env && restic init
#
# Retention: 7d / 4w / 12m via `forget --keep-*`.

set -euo pipefail

# Lädt RESTIC_REPOSITORY + RESTIC_PASSWORD_FILE
if [[ ! -f /etc/vaeren/restic.env ]]; then
    echo "Skipping backup: /etc/vaeren/restic.env nicht vorhanden (Storage-Box-Account fehlt?)" >&2
    exit 0
fi
source /etc/vaeren/restic.env

LOG_TS="$(date '+%Y-%m-%d %H:%M:%S')"
echo "[$LOG_TS] Vaeren restic backup start"

# --- 1. Postgres-Dump ----------------------------------------------------
DUMP_DIR=/var/lib/vaeren-restic
mkdir -p "$DUMP_DIR"
DUMP_FILE="$DUMP_DIR/vaeren-postgres-$(date +%Y%m%d).sql.gz"

docker exec vaeren-postgres pg_dump \
    -U "${POSTGRES_USER:-vaeren}" \
    --no-owner --no-acl --clean --if-exists \
    "${POSTGRES_DB:-vaeren}" \
    | gzip -9 > "$DUMP_FILE"

echo "[$LOG_TS] Postgres-Dump: $(du -h "$DUMP_FILE" | cut -f1)"

# --- 2. Backup ----------------------------------------------------------
# Backup: DB-Dump + Media-Volume (User-Uploads).
restic backup \
    --tag "vaeren" \
    --tag "auto" \
    --host "vaeren-prod" \
    "$DUMP_FILE" \
    /var/lib/docker/volumes/ai-act_vaeren-media/_data

# --- 3. Retention -------------------------------------------------------
restic forget \
    --tag "vaeren" \
    --keep-daily 7 \
    --keep-weekly 4 \
    --keep-monthly 12 \
    --prune

# --- 4. Lokalen Dump aufräumen ------------------------------------------
find "$DUMP_DIR" -name "vaeren-postgres-*.sql.gz" -mtime +2 -delete

# --- 5. Health-Check ----------------------------------------------------
restic check --read-data-subset=2%

echo "[$LOG_TS] Vaeren restic backup done"
