#!/usr/bin/env bash
# Vaeren Production Deployment (Sprint 8).
#
# Pattern analog Sponty (`/home/konrad/sponty/deploy.sh`):
#   1. rsync Code → Server
#   2. scp .env.production → Server (.env)
#   3. ssh: docker compose build + up
#
# Aufruf vom Repo-Root:
#   ./deploy.sh                # Standard
#   ./deploy.sh --no-build     # nur up, kein rebuild
#   ./deploy.sh --logs         # nach up: Logs streamen
#
# Trigger: MANUELL durch Konrad, KEIN Auto-Deploy aus CI (Spec §11).

set -euo pipefail

SERVER="${VAEREN_SERVER:-root@204.168.159.236}"
REMOTE_DIR="${VAEREN_REMOTE_DIR:-/opt/ai-act}"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# --- Args ---------------------------------------------------------------
BUILD_FLAG="--build"
TAIL_LOGS=0
for arg in "$@"; do
    case "$arg" in
        --no-build) BUILD_FLAG="" ;;
        --logs)     TAIL_LOGS=1 ;;
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

# --- 1. SSH ping ---------------------------------------------------------
echo "[1/5] SSH-Erreichbarkeit prüfen …"
ssh -o BatchMode=yes -o ConnectTimeout=10 "$SERVER" 'echo "ssh-ok: $(uname -m)"'

# --- 2. Remote-Dir vorbereiten ------------------------------------------
echo "[2/5] Remote-Verzeichnis vorbereiten …"
ssh "$SERVER" "mkdir -p $REMOTE_DIR"

# --- 3. Code synchronisieren --------------------------------------------
echo "[3/5] Code via rsync synchronisieren …"
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

# --- 4. .env.production hochladen ---------------------------------------
echo "[4/5] .env.production hochladen …"
scp "$ENV_FILE" "$SERVER:$REMOTE_DIR/.env"

# --- 5. Build + up ------------------------------------------------------
echo "[5/5] Container bauen + starten …"
ssh "$SERVER" "cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE up -d $BUILD_FLAG --remove-orphans"

echo ""
echo "=== Deploy abgeschlossen ==="
echo "Status: ssh $SERVER 'cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE ps'"
echo "Logs:   ssh $SERVER 'cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE logs -f'"

if [[ "$TAIL_LOGS" -eq 1 ]]; then
    ssh "$SERVER" "cd $REMOTE_DIR && docker compose -f $COMPOSE_FILE logs -f --tail=50"
fi
