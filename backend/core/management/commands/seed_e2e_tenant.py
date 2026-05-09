"""Seed-Command für Playwright-E2E-Tests (Sprint 7).

Idempotent: löscht und re-erstellt einen `e2e`-Tenant mit bekanntem
GF-Login + Demo-Mitarbeiterin. Wird vom Playwright-CI-Job aufgerufen
bevor die Specs laufen.

Aufruf:
    uv run python manage.py seed_e2e_tenant
"""

from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from tenants.models import Tenant, TenantDomain

E2E_SCHEMA = "e2e"
E2E_DOMAIN = "e2e.app.vaeren.local"
E2E_GF_EMAIL = "gf@e2e.de"
E2E_GF_PASSWORD = "E2E-test-1234!"
E2E_CB_EMAIL = "compl@e2e.de"
E2E_CB_PASSWORD = "E2E-test-1234!"


class Command(BaseCommand):
    help = "Erstellt/Resettet den E2E-Tenant für Playwright-Tests."

    def handle(self, *args, **options):
        from core.models import Mitarbeiter, TenantRole, User

        # Drop existing
        Tenant.objects.filter(schema_name=E2E_SCHEMA).delete()

        tenant = Tenant.objects.create(
            schema_name=E2E_SCHEMA,
            firma_name="E2E Test GmbH",
            plan="professional",
            pilot=True,
            mfa_required=False,
            locale="de-DE",
        )
        TenantDomain.objects.create(tenant=tenant, domain=E2E_DOMAIN, is_primary=True)

        with schema_context(E2E_SCHEMA):
            # `auto_drop_schema=True` sollte die Tabellen löschen, aber im Test-
            # mode bleiben sie ggf. erhalten. Daher robust per get_or_create
            # mit explizitem Passwort-Reset.
            gf, _ = User.objects.get_or_create(
                email=E2E_GF_EMAIL,
                defaults={
                    "tenant_role": TenantRole.GESCHAEFTSFUEHRER,
                    "is_active": True,
                },
            )
            gf.set_password(E2E_GF_PASSWORD)
            gf.save()
            cb, _ = User.objects.get_or_create(
                email=E2E_CB_EMAIL,
                defaults={
                    "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                    "is_active": True,
                },
            )
            cb.set_password(E2E_CB_PASSWORD)
            cb.save()
            Mitarbeiter.objects.get_or_create(
                email="anna@e2e.de",
                defaults={
                    "vorname": "Anna",
                    "nachname": "Test",
                    "abteilung": "Produktion",
                    "rolle": "Maschinenführerin",
                    "eintritt": datetime.date(2024, 1, 1),
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"E2E tenant ready: schema={E2E_SCHEMA} domain={E2E_DOMAIN} "
                f"gf={E2E_GF_EMAIL} cb={E2E_CB_EMAIL}"
            )
        )
