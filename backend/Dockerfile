# Vaeren Backend — Production Dockerfile
# Multi-stage: builder (uv deps) + runtime (lean).
# ARM64-native: gebaut auf Hetzner CAX31, NICHT cross-compile.
# Spec §11: WeasyPrint braucht libcairo + libpango.

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# uv-Installer (ARM64-kompatibel)
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

WORKDIR /app

# Build-deps für native Python-Wheels (cffi, cryptography)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Lock-Files zuerst (cache-friendly)
COPY backend/pyproject.toml backend/uv.lock /app/
RUN uv sync --frozen --no-dev --no-install-project

# Code (separater Layer für schnellere Iterationen)
COPY backend/ /app/


# --- Runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# Runtime-System-Libs:
# - libpq5 für psycopg
# - libcairo2 + libpango-1.0-0 + libpangoft2-1.0-0 + libgdk-pixbuf-2.0-0 für WeasyPrint
# - fonts-dejavu für PDF-Rendering ohne ?-Boxen
# - tini als PID-1 für saubere Signal-Behandlung
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        libcairo2 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi8 \
        fonts-dejavu \
        tini && \
    rm -rf /var/lib/apt/lists/*

# venv + Code aus builder
COPY --from=builder /app /app

# Non-root user
RUN groupadd -r vaeren --gid=1000 && \
    useradd -r -g vaeren --uid=1000 --no-create-home --shell=/usr/sbin/nologin vaeren && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R vaeren:vaeren /app

USER vaeren

EXPOSE 8000

# Migrate-on-startup (Schema-aware via django-tenants), dann Daphne.
# Spec §11: Migrations müssen rückwärtskompatibel sein.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "python manage.py migrate_schemas --noinput && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 config.asgi:application"]
