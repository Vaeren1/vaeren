"""Test: Akzeptieren-Endpoint behandelt unbekannte Codes konsistent.

Fix N5: Wenn ein LLM-Vorschlag Codes enthält, die nicht im
Gefährdungs-Katalog existieren, wurden sie früher stillschweigend
übersprungen. Jetzt erscheinen sie in `skipped_unknown_codes` der
Response.
"""

from __future__ import annotations

import json

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Gefaehrdung,
    GefaehrdungKategorie,
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    GbuGefaehrdungVorschlag,
)


def test_akzeptieren_meldet_unknown_codes(authed_client, basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    domain = tenant.domains.first().domain
    with schema_context(tenant.schema_name):
        Gefaehrdung.objects.create(
            code="KNOWN-001",
            name="Bekannt",
            kategorie=GefaehrdungKategorie.MECHANISCH,
        )
        gbu = Gefaehrdungsbeurteilung.objects.create(
            taetigkeit=taetigkeit, titel="Bewertung"
        )
        vorschlag = GbuGefaehrdungVorschlag.objects.create(
            taetigkeit=taetigkeit,
            gbu=gbu,
            vorgeschlagene_codes=[
                {"code": "KNOWN-001", "b": "ok"},
                {"code": "UNBEKANNT-X", "b": "fake"},
                {"code": "UNBEKANNT-Y", "b": "fake"},
            ],
            status=GbuGefaehrdungVorschlag.Status.OFFEN,
        )

    resp = authed_client.post(
        f"/api/arbeitsschutz/gbu-vorschlaege/{vorschlag.pk}/akzeptieren/",
        data=json.dumps({}),
        content_type="application/json",
        HTTP_HOST=domain,
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["created"] == 1
    assert sorted(body["skipped_unknown_codes"]) == ["UNBEKANNT-X", "UNBEKANNT-Y"]
    assert "unbekannte" in body["detail"].lower()
    with schema_context(tenant.schema_name):
        assert GbuGefaehrdung.objects.filter(gbu=gbu).count() == 1


def test_akzeptieren_ohne_unknown_codes(authed_client, basis_stammdaten):
    tenant, _, taetigkeit = basis_stammdaten
    domain = tenant.domains.first().domain
    with schema_context(tenant.schema_name):
        Gefaehrdung.objects.create(
            code="KNOWN-A",
            name="A",
            kategorie=GefaehrdungKategorie.MECHANISCH,
        )
        gbu = Gefaehrdungsbeurteilung.objects.create(
            taetigkeit=taetigkeit, titel="X"
        )
        vorschlag = GbuGefaehrdungVorschlag.objects.create(
            taetigkeit=taetigkeit,
            gbu=gbu,
            vorgeschlagene_codes=[{"code": "KNOWN-A"}],
            status=GbuGefaehrdungVorschlag.Status.OFFEN,
        )

    resp = authed_client.post(
        f"/api/arbeitsschutz/gbu-vorschlaege/{vorschlag.pk}/akzeptieren/",
        data=json.dumps({}),
        content_type="application/json",
        HTTP_HOST=domain,
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["skipped_unknown_codes"] == []
    assert body["created"] == 1
