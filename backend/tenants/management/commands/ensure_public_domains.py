"""Stellt sicher, dass die public-Schema-TenantDomains konfiguriert sind.

Diese Domains zeigen auf das Public-Schema und liefern u.a.:
- `hinweise.app.vaeren.de` → HinSchG-Public-Formular
- `api.vaeren.de`          → Marketing-Site-API (NewsPost, Korrekturen)
- `localhost`, `127.0.0.1` → Dev-Einstieg

Idempotent. Sicher gegen mehrfaches Ausführen.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django_tenants.utils import get_public_schema_name, schema_context

from tenants.models import Tenant, TenantDomain

PUBLIC_DOMAINS = [
    # Marketing-API (NewsPost, Korrekturen, Notbremse)
    "api.vaeren.de",
    # Marketing-Site (Caddy file_server, kein Backend-Routing, aber DRF
    # braucht Host-Header-Match für ALLOWED_HOSTS)
    "vaeren.de",
    "www.vaeren.de",
    # Container-Hostname für interne SSG-Builds (Marketing-Site-Build
    # läuft im docker-Netzwerk und fetcht direkt gegen vaeren-django:8000)
    "vaeren-django",
    # Dev:
    "localhost",
    "127.0.0.1",
]

# WICHTIG: hinweise.app.vaeren.de NICHT hier rein — gehört zum demo-Tenant
# (oder einem anderen tenant-spezifischen Schema), weil der HinSchG-Public-
# Endpoint in urls_tenant.py registriert ist (path "public/hinschg/...").
# Diese Liste ist ausschließlich für Domains, die das PUBLIC_SCHEMA_URLCONF
# bedienen sollen.


class Command(BaseCommand):
    help = "Registriert public-Schema-TenantDomains (idempotent)."

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        public_schema = get_public_schema_name()
        with schema_context(public_schema):
            public_tenant, created = Tenant.objects.get_or_create(
                schema_name=public_schema,
                defaults={"firma_name": "Public", "plan": "professional"},
            )
            if created:
                self.stdout.write(
                    self.style.WARNING(
                        f"Public-Tenant neu angelegt: pk={public_tenant.pk}"
                    )
                )
            for domain in PUBLIC_DOMAINS:
                _, td_created = TenantDomain.objects.update_or_create(
                    domain=domain,
                    defaults={"tenant": public_tenant, "is_primary": False},
                )
                state = "neu" if td_created else "bestätigt"
                self.stdout.write(f"  {domain} — {state}")
        self.stdout.write(self.style.SUCCESS("ensure_public_domains: fertig"))
