"""API-Smoke-Tests: GBU-Anlage, Freigabe-Endpoint."""

from __future__ import annotations

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Arbeitsbereich,
    ArbeitsbereichTyp,
    Gefaehrdungsbeurteilung,
    GbuStatus,
    Taetigkeit,
)


def test_api_arbeitsbereiche_list(authed_client, arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        Arbeitsbereich.objects.create(name="Halle 1", typ=ArbeitsbereichTyp.WERKSTATT)

    resp = authed_client.get("/api/arbeitsschutz/arbeitsbereiche/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1


def test_api_gbu_freigeben(authed_client, arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        b = Arbeitsbereich.objects.create(name="X", typ=ArbeitsbereichTyp.WERKSTATT)
        t = Taetigkeit.objects.create(arbeitsbereich=b, name="T")
        gbu = Gefaehrdungsbeurteilung.objects.create(taetigkeit=t, titel="X")
    resp = authed_client.post(f"/api/arbeitsschutz/gbu/{gbu.pk}/freigeben/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == GbuStatus.FREIGEGEBEN


def test_api_unfall_statistik(authed_client, arbsch_tenant):
    resp = authed_client.get("/api/arbeitsschutz/unfaelle/statistik/")
    assert resp.status_code == 200
    body = resp.json()
    assert "ytd_total" in body
    assert "ytd_meldepflichtig" in body
