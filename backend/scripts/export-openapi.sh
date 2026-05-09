#!/bin/bash
# Generiert das OpenAPI-Schema aus drf-spectacular nach
# `frontend/src/lib/api/openapi.json`. Konsumiert von
# `frontend/scripts/sync-openapi.sh` (openapi-typescript).
#
# Aufruf: vom Repo-Root oder vom backend/-Verzeichnis aus.
# CI ruft das Script vor `git diff --exit-code` auf, um Schema-Drift zu
# detektieren.

set -euo pipefail

cd "$(dirname "$0")/.."   # nach backend/

OUT="../frontend/src/lib/api/openapi.json"
mkdir -p "$(dirname "$OUT")"

uv run python manage.py spectacular \
    --file "$OUT" \
    --format openapi-json \
    --validate

echo "OpenAPI-Schema geschrieben nach: $OUT"
