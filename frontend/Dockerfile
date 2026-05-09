# Vaeren Frontend — Production Dockerfile
# Multi-stage: bun-Build → nginx-static.
# Frontend-Build kommt mit dem Backend-API-Schema gerendert; OpenAPI-Sync ist
# CI-Gate, deshalb hier kein zusätzlicher Schema-Pull nötig.

FROM oven/bun:1 AS builder

WORKDIR /app

# Lock-File-cache
COPY frontend/package.json frontend/bun.lock /app/
RUN bun install --frozen-lockfile

COPY frontend/ /app/
RUN bun run build


# --- Runtime: nginx-alpine, serviert statisches dist/ ---
FROM nginx:1.27-alpine AS runtime

# Vite-build → nginx-html-Verzeichnis
COPY --from=builder /app/dist /usr/share/nginx/html

# SPA-Routing: alle Pfade auf index.html fallback'en (außer /api & /accounts)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
