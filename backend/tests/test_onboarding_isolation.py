"""Multi-Tenant-Isolation für den Onboarding-Wizard (Vaeren-Kernregel).

UnternehmensProfil aus Tenant A darf in Tenant B NICHT sichtbar sein.
Kritischer CI-Gate (Spec §2 / Architektur-Regel 2).
"""

from __future__ import annotations

import pytest
from django_tenants.utils import schema_context

from onboarding_wizard.models import UnternehmensProfil


@pytest.mark.django_db
def test_profil_ist_tenant_isoliert(two_tenants):
    t1, t2 = two_tenants

    with schema_context(t1.schema_name):
        UnternehmensProfil.objects.create(firmenname="A GmbH")
        assert UnternehmensProfil.objects.count() == 1

    with schema_context(t2.schema_name):
        assert UnternehmensProfil.objects.count() == 0

    # Gegenprobe: Profil in t2 anlegen ändert t1 nicht.
    with schema_context(t2.schema_name):
        UnternehmensProfil.objects.create(firmenname="B GmbH")
        assert UnternehmensProfil.objects.count() == 1
        assert UnternehmensProfil.objects.first().firmenname == "B GmbH"

    with schema_context(t1.schema_name):
        assert UnternehmensProfil.objects.count() == 1
        assert UnternehmensProfil.objects.first().firmenname == "A GmbH"
