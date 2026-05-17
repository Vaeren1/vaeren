#!/usr/bin/env bash
# Vaeren Production Deployment (Sprint 8 + Marketing-Site).
#
# Pattern analog Sponty (`/home/konrad/sponty/deploy.sh`):
#   1. Marketing lokal bauen (Astro statisch)
#   2. rsync Code → Server
#   3. rsync marketing/dist → Server:/var/www/vaeren-marketing
#   4. scp .env.production → Server (.env)
#   5. docker compose build + up
#   6. ensure_public_domains (api.vaeren.de + hinweise.app.vaeren.de + apex)
#   7. Caddy reload
#
# Aufruf vom Repo-Root:
#   ./deploy.sh                  # Standard
#   ./deploy.sh --no-build       # kein Container-Rebuild
#   ./deploy.sh --skip-marketing # Marketing-Build überspringen
#   ./deploy.sh --logs           # nach up: Logs streamen
#
# Trigger: MANUELL durch Konrad, KEIN Auto-Deploy aus CI (Spec §11).

set -euo pipefail

SERVER="${VAEREN_SERVER:-root@204.168.159.236}"
REMOTE_DIR="${VAEREN_REMOTE_DIR:-/opt/ai-act}"
REMOTE_MARKETING_DIR="${VAEREN_MARKETING_DIR:-/var/www/vaeren-marketing}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
PROD_API_BASE="${PROD_API_BASE:-https://api.vaeren.de}"

# --- Args ---------------------------------------------------------------
BUILD_FLAG="--build"
SKIP_MARKETING=0
TAIL_LOGS=0
for arg in "$@"; do
    case "$arg" in
        --no-build)        BUILD_FLAG="" ;;
        --skip-marketing)  SKIP_MARKETING=1 ;;
        --logs)            TAIL_LOGS=1 ;;
        *) echo "Unbekanntes Argument: $arg"; exit 1 ;;
    esac
done

# --- Pre-Flight ---------------------------------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
    cat <<EOF >&2
Fehler: $ENV_FILE nicht im Repo-Root gefunden.

Lege es an als Kopie von infrastructure/.env.production.example und füge
deine Secrets ein. NICHT committen — bereits in .gitignore.
EOF
    exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
    echo "rsync nicht installiert" >&2; exit 1
fi

echo "=== Vaeren Deploy → $SERVER:$REMOTE_DIR ==="

# --- 1. Marketing-Site bauen (lokal) -----------------------------------
if [[ "$SKIP_MARKETING" -eq 0 ]]; then
    echo "[1/7] Marketing-Site bauen (Astro, lokal) …"
    if ! command -v bun >/dev/null 2>&1; then
        if [[ -x "$HOME/.bun/bin/bun" ]]; then
            export PATH="$HOME/.bun/bin:$PATH"
        else
            echo "bun nicht gefunden (weder im PATH noch unter ~/.bun/bin)" >&2
            echo "Installation: https://bun.sh" >&2
            exit 1
        fi
    fi
    (
        cd marketing
        bun install --frozen-lockfile
        PUBLIC_API_BASE="$PROD_API_BASE" bun run build
    )
    echo "      Marketing-Build fertig (marketing/dist)."
else
    echo "[1/7] Marketing-Build übersprungen (--skip-marketing)."
fi

# --- 2. SSH ping --------------------------------------------------------
echo "[2/7] SSH-Erreichbarkeit prüfen …"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$SERVER" 'echo "ssh-ok: $(uname -m)"'

# --- 3. Remote-Dir vorbereiten -----------------------------------------
echo "[3/7] Remote-Verzeichnisse vorbereiten …"
ssh "$SERVER" "mkdir -p $REMOTE_DIR $REMOTE_MARKETING_DIR"

# --- 4. Code synchronisieren -------------------------------------------
echo "[4/7] Code via rsync synchronisieren …"
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.github' \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.venv' \
    --exclude 'frontend/dist' \
    --exclude 'frontend/storybook-static' \
    --exclude 'frontend/test-results' \
    --exclude 'frontend/playwright-report' \
    --exclude 'marketing/node_modules' \
    --exclude 'marketing/dist' \
    --exclude 'marketing/.astro' \
    --exclude '.pytest_cache' \
    --exclude '.ruff_cache' \
    --exclude 'htmlcov' \
    --exclude '.coverage' \
    --exclude 'docker-compose.dev.yml' \
    --exclude '.env' \
    --exclude '.env.local' \
    --exclude '.env.production' \
    --exclude 'docs' \
    --exclude '*.md' \
    ./ "$SERVER:$REMOTE_DIR/"

# --- 5. Marketing-Static-Files synchronisieren -------------------------
if [[ "$SKIP_MARKETING" -eq 0 ]]; then
    echo "[5/7] Marketing-Static nach $REMOTE_MARKETING_DIR synchronisieren …"
    rsync -avz --delete \
        marketing/dist/ "$SERVER:$REMOTE_MARKETING_DIR/"
else
    echo "[5/7] Marketing-Static rsync übersprungen."
fi

# --- 6. .env.production hochladen --------------------------------------
echo "[6/7] .env.production hochladen …"
scp "$ENV_FILE" "$SERVER:$REMOTE_DIR/.env"

# --- 7. Build + up + Public-Domains + Caddy reload ---------------------
echo "[7/7] Container bauen, starten, Public-Domains pflegen, Caddy reload …"
ssh "$SERVER" "cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE up -d $BUILD_FLAG --remove-orphans"
# ensure_public_domains nach jedem Deploy laufen lassen (idempotent, billig).
# Service-Name im Compose ist `django` (Container-Name ist `vaeren-django` über
# container_name:) — docker compose exec verlangt den Service-Namen.
ssh "$SERVER" "cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE exec -T django python manage.py ensure_public_domains || echo '  (warnung: ensure_public_domains failed, manuell prüfen)'"
# Caddy läuft als eigener Container im /opt/caddy/-Stack (NICHT systemd-Unit) —
# Reload erzwingt frische DNS-Resolution für die Backend-Container, die gerade
# neu erstellt wurden (sonst kann Caddy auf alte IPs zeigen und 502 liefern).
ssh "$SERVER" "docker exec caddy caddy reload --config /etc/caddy/Caddyfile || echo '  (warnung: caddy reload failed, manuell prüfen: docker logs caddy)'"

echo ""
echo "=== Deploy abgeschlossen ==="
echo "Status:    ssh $SERVER 'cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE ps'"
echo "Logs:      ssh $SERVER 'cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE logs -f'"
echo "Smoke:     curl -s https://vaeren.de | head -5"
echo "API Smoke: curl -s https://api.vaeren.de/api/public/news/ | jq '.results | length'"

if [[ "$TAIL_LOGS" -eq 1 ]]; then
    ssh "$SERVER" "cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE logs -f --tail=50"
fi
