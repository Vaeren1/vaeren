#!/bin/bash
# Konvertiert das von backend/scripts/export-openapi.sh erzeugte
# `frontend/src/lib/api/openapi.json` in TypeScript-Types
# (`frontend/src/lib/api/types.gen.ts`).
#
# CI-Pipeline:
#   ./backend/scripts/export-openapi.sh
#   ./frontend/scripts/sync-openapi.sh
#   git diff --exit-code -- frontend/src/lib/api/

set -euo pipefail

cd "$(dirname "$0")/.."   # nach frontend/

# `bun x` ist die explizite Form von `bunx` und immer verfügbar, sobald
# `bun` im PATH ist (manche bun-Installationen liefern bunx nicht als
# Symlink mit).
bun x openapi-typescript src/lib/api/openapi.json \
    --output src/lib/api/types.gen.ts

echo "TypeScript-Types geschrieben nach: src/lib/api/types.gen.ts"
