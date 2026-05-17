"""DRF-API-Tests: Risiko-Register CRUD + Treatment-Vorschlag + Akzeptanz."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import Mitarbeiter, TenantRole, User
from iso27001.models import AssetTyp, IsmsAsset, IsmsRiskAssessment, Klassifizierung


@pytest.fixture
def authed_client(tenant_iso, settings):
    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_iso.schema_name):
        u, _ = User.objects.get_or_create(
            email="cb@iso-r.de",
            defaults={
                "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                "is_active": True,
            },
        )
        u.set_password("iso-r-1234!")
        u.save()
        client = Client(HTTP_HOST="iso-test.app.vaeren.local", enforce_csrf_checks=False)
        assert client.login(email="cb@iso-r.de", password="iso-r-1234!")
    return client


def test_risk_crud_via_api(tenant_iso, authed_client):
    with schema_context(tenant_iso.schema_name):
        asset = IsmsAsset.objects.create(
            name="App-Server",
            asset_typ=AssetTyp.SYSTEM,
            klassifizierung=Klassifizierung.VERTRAULICH,
        )

    resp = authed_client.post(
        "/api/iso27001/risiken/",
        data={
            "asset": asset.id,
            "titel": "DoS-Angriff",
            "threat": "Externer Angreifer",
            "vulnerability": "Keine Rate-Limits",
            "likelihood": 3,
            "impact": 4,
            "treatment": "reduzieren",
            "treatment_plan": "Rate-Limit + WAF",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data["risk_score_brutto"] == 12


def test_treatment_vorschlag_endpoint(tenant_iso, authed_client):
    with schema_context(tenant_iso.schema_name):
        asset = IsmsAsset.objects.create(name="A", asset_typ=AssetTyp.SYSTEM)
        risk = IsmsRiskAssessment.objects.create(
            asset=asset,
            titel="X",
            threat="A",
            vulnerability="B",
            likelihood=3,
            impact=3,
        )

    from iso27001.llm import TreatmentVorschlag

    fake = TreatmentVorschlag(entwurf="Entwurf: Reduzieren.", quelle="llm")
    with patch("iso27001.views.entwurf_treatment_plan", return_value=fake):
        resp = authed_client.post(
            f"/api/iso27001/risiken/{risk.id}/treatment-vorschlag/"
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "entwurf" in data
    assert "rdg_disclaimer" in data

    with schema_context(tenant_iso.schema_name):
        risk.refresh_from_db()
        assert risk.treatment_vorschlag == "Entwurf: Reduzieren."


def test_akzeptieren_endpoint_setzt_mitarbeiter(tenant_iso, settings):
    """Restrisiko-Akzeptanz nur durch GESCHAEFTSFUEHRER-User.

    Der Default-`authed_client` ist Compliance-Beauftragter → würde 403
    bekommen. Wir bauen hier einen GF-Client.
    """
    import datetime

    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_iso.schema_name):
        gf_user, _ = User.objects.get_or_create(
            email="gf@iso-r.de",
            defaults={
                "tenant_role": TenantRole.GESCHAEFTSFUEHRER,
                "is_active": True,
            },
        )
        gf_user.tenant_role = TenantRole.GESCHAEFTSFUEHRER
        gf_user.set_password("iso-r-gf-1234!")
        gf_user.save()

        asset = IsmsAsset.objects.create(name="A", asset_typ=AssetTyp.SYSTEM)
        risk = IsmsRiskAssessment.objects.create(
            asset=asset,
            titel="X",
            threat="A",
            vulnerability="B",
            likelihood=3,
            impact=3,
            treatment="akzeptieren",
            restrisiko_likelihood=2,
            restrisiko_impact=2,
        )
        gf_ma = Mitarbeiter.objects.create(
            vorname="GF",
            nachname="Chef",
            abteilung="GF",
            rolle="Geschäftsführung",
            eintritt=datetime.date(2020, 1, 1),
        )

        gf_client = Client(
            HTTP_HOST="iso-test.app.vaeren.local", enforce_csrf_checks=False
        )
        assert gf_client.login(email="gf@iso-r.de", password="iso-r-gf-1234!")

    resp = gf_client.post(
        f"/api/iso27001/risiken/{risk.id}/akzeptieren/",
        data={"mitarbeiter_id": gf_ma.id},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    with schema_context(tenant_iso.schema_name):
        risk.refresh_from_db()
        assert risk.akzeptiert_von_id == gf_ma.id
        assert risk.akzeptiert_am is not None


def test_akzeptieren_endpoint_blocks_non_gf(tenant_iso, authed_client):
    """Compliance-Beauftragter (kein GF) bekommt 403 beim Akzeptieren."""
    import datetime

    with schema_context(tenant_iso.schema_name):
        asset = IsmsAsset.objects.create(name="A", asset_typ=AssetTyp.SYSTEM)
        risk = IsmsRiskAssessment.objects.create(
            asset=asset,
            titel="X",
            threat="A",
            vulnerability="B",
            likelihood=3,
            impact=3,
            treatment="akzeptieren",
            restrisiko_likelihood=2,
            restrisiko_impact=2,
        )
        ma = Mitarbeiter.objects.create(
            vorname="CB",
            nachname="Test",
            abteilung="C",
            rolle="Compliance",
            eintritt=datetime.date(2020, 1, 1),
        )

    resp = authed_client.post(
        f"/api/iso27001/risiken/{risk.id}/akzeptieren/",
        data={"mitarbeiter_id": ma.id},
        content_type="application/json",
    )
    assert resp.status_code == 403
