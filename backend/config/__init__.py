"""Django config-Paket. Sprint 8: Celery-app eager-import damit @shared_task funktioniert."""

from __future__ import annotations

# Best-effort Celery-Import — wenn celery nicht installiert ist (Dev ohne Worker),
# einfach skippen.
try:
    from .celery import app as celery_app  # noqa: F401
except ImportError:
    pass
