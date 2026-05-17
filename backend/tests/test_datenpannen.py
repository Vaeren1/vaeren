"""Tests für Datenpannen-Register (DSGVO Art. 33/34)."""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from core.models import ComplianceTaskStatus, TenantRole, User
from datenpannen.models import (
    Datenpanne,
    DatenpannenTask,
    DatenpannenTaskTyp,
    Massnahme,
    MassnahmeTyp,
    PannenArt,
    PannenStatus,
    RisikoStufe,
)
from tenants.models import Tenant, TenantDomain


@pytest.fixture
def tenant_demo(db):
    from django.db import connection

    connection.set_schema_to_public()
    with schema_context("public"):
        t, _ = Tenant.objects.get_or_create(
            schema_name="demo_dp", defaults={"firma_name": "Demo Datenpannen GmbH"}
        )
        TenantDomain.objects.get_or_create(
            tenant=t, domain="demo-dp.app.vaeren.local", defaults={"is_primary": True}
        )
    yield t
    connection.set_schema_to_public()
    with schema_context("public"):
        Tenant.objects.filter(schema_name="demo_dp").first().delete(force_drop=True)


@pytest.fixture
def authed_client(tenant_demo, settings):
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_demo.schema_name):
        u, _ = User.objects.get_or_create(
            email="gf@demo-dp.de",
            defaults={"tenant_role": TenantRole.GESCHAEFTSFUEHRER, "is_active": True},
        )
        u.set_password("dp-test-1234!")
        u.save()
        client = Client(HTTP_HOST="demo-dp.app.vaeren.local", enforce_csrf_checks=False)
        assert client.login(email="gf@demo-dp.de", password="dp-test-1234!")
    return client


# --- Modell-Tests ----------------------------------------------------------


def test_datenpanne_setzt_72h_frist_automatisch(tenant_demo):
    with schema_context(tenant_demo.schema_name):
        now = timezone.now()
        panne = Datenpanne.objects.create(
            titel="USB-Stick verloren",
            art=PannenArt.VERLUST_GERAET,
            beschreibung_verschluesselt="Stick mit Kundendaten in der Bahn",
            entdeckt_am=now,
        )
        delta = panne.frist_meldung_behoerde - now
        # Default ist 72h ab _frist_meldung_behoerde() (jetzt) — Differenz <= 2 Sek
        assert 71 * 3600 < delta.total_seconds() < 73 * 3600


def test_datenpanne_meldepflichtig_property(tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
            risiko=RisikoStufe.HOCH,
        )
        assert panne.meldepflichtig is True
        panne.risiko = RisikoStufe.KEIN_RISIKO
        assert panne.meldepflichtig is False


def test_datenpanne_create_erzeugt_compliance_task_meldung_behoerde(tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="Fehlversand",
            art=PannenArt.FEHLVERSAND,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
        )
        tasks = list(panne.tasks.all())
        assert len(tasks) == 1
        assert tasks[0].task_typ == DatenpannenTaskTyp.MELDUNG_BEHOERDE
        assert tasks[0].modul == "datenpannen"
        assert tasks[0].status == ComplianceTaskStatus.OFFEN


def test_datenpanne_hochrisiko_erzeugt_benachrichtigung_task(tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="Ransomware",
            art=PannenArt.RANSOMWARE,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
            risiko=RisikoStufe.HOCH,
        )
        # signals.create_compliance_tasks läuft 2× — Initial + Risiko-Update
        typen = set(panne.tasks.values_list("task_typ", flat=True))
        assert DatenpannenTaskTyp.MELDUNG_BEHOERDE in typen
        assert DatenpannenTaskTyp.BENACHRICHTIGUNG_BETROFFENE in typen


def test_datenpanne_abschluss_erzeugt_abschlussdoku_task(tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
        )
        # Initial: 1 Task
        assert panne.tasks.count() == 1
        panne.status = PannenStatus.ABGESCHLOSSEN
        panne.save()
        typen = set(panne.tasks.values_list("task_typ", flat=True))
        assert DatenpannenTaskTyp.ABSCHLUSSDOKU in typen


def test_beschreibung_at_rest_verschluesselt(tenant_demo):
    """Verschlüsselung-Smoke: DB enthält nicht den Klartext."""
    from django.db import connection

    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="Test",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="GEHEIMER-INHALT-12345",
            entdeckt_am=timezone.now(),
        )
        with connection.cursor() as c:
            c.execute(
                "SELECT beschreibung_verschluesselt FROM datenpannen_datenpanne WHERE id=%s",
                [panne.id],
            )
            raw = c.fetchone()[0]
        assert "GEHEIMER-INHALT-12345" not in str(raw)
        # Re-Read durch Manager liefert Klartext
        assert (
            Datenpanne.objects.get(id=panne.id).beschreibung_verschluesselt
            == "GEHEIMER-INHALT-12345"
        )


# --- API-Tests -------------------------------------------------------------


def test_api_datenpanne_create(authed_client, tenant_demo):
    payload = {
        "titel": "USB-Stick im Zug",
        "art": PannenArt.VERLUST_GERAET,
        "beschreibung": "Stick mit ca. 200 Kundendaten",
        "entdeckt_am": timezone.now().isoformat(),
        "anzahl_betroffene_geschaetzt": 200,
        "datenkategorien": ["kontaktdaten", "vertragsdaten"],
    }
    resp = authed_client.post(
        "/api/datenpannen/", payload, content_type="application/json"
    )
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data["titel"] == "USB-Stick im Zug"
    assert data["status"] == PannenStatus.ENTDECKT
    assert data["meldepflichtig"] is False  # Risiko noch leer
    with schema_context(tenant_demo.schema_name):
        assert Datenpanne.objects.filter(titel="USB-Stick im Zug").exists()


def test_api_datenpanne_list_returns_compact(authed_client, tenant_demo):
    with schema_context(tenant_demo.schema_name):
        Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
        )
    resp = authed_client.get("/api/datenpannen/")
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["count"] >= 1


def test_api_behoerde_melden_setzt_status_und_datum(authed_client, tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
            risiko=RisikoStufe.GERING,
        )
        pid = panne.id
    resp = authed_client.post(
        f"/api/datenpannen/{pid}/behoerde-melden/",
        {"aktenzeichen": "BfDI-2026-0042"},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    with schema_context(tenant_demo.schema_name):
        p = Datenpanne.objects.get(id=pid)
        assert p.status == PannenStatus.GEMELDET
        assert p.behoerde_gemeldet_am is not None
        assert p.behoerde_aktenzeichen == "BfDI-2026-0042"


def test_api_behoerde_melden_zweimal_409(authed_client, tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
            risiko=RisikoStufe.GERING,
            behoerde_gemeldet_am=timezone.now(),
        )
        pid = panne.id
    resp = authed_client.post(
        f"/api/datenpannen/{pid}/behoerde-melden/", {}, content_type="application/json"
    )
    assert resp.status_code == 409


def test_api_risiko_vorschlag_liefert_disclaimer(authed_client):
    """LLM-Endpoint muss IMMER den RDG-Disclaimer + Vorschlagssprache liefern."""
    payload = {
        "art": PannenArt.RANSOMWARE,
        "beschreibung": "Server wurde verschlüsselt, Backup ist vorhanden, ca. 5000 betroffene Datensätze.",
        "anzahl_betroffene": 5000,
        "datenkategorien": ["kontaktdaten", "kontodaten"],
    }
    # LLM-Call mocken — kein echter Netz-Call in Tests
    with patch("datenpannen.llm.generate") as mock_gen:
        mock_gen.return_value = type(
            "LR",
            (),
            {
                "text": '{"risiko": "hoch", "begruendung": "Vorschlag: Hoch wegen Umfang und Kontodaten."}',
                "quelle": "llm",
                "model": "test",
            },
        )()
        resp = authed_client.post(
            "/api/datenpannen/risiko-vorschlag/",
            payload,
            content_type="application/json",
        )
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["risiko_vorschlag"] == RisikoStufe.HOCH
    assert "Vorschlag:" in data["begruendung"]
    assert "KEIN juristischer Rat" in data["rdg_disclaimer"]


def test_api_risiko_vorschlag_invalid_llm_fallback_gering(authed_client):
    """LLM liefert garbage → Code defaultet auf GERING."""
    payload = {
        "art": PannenArt.PHISHING,
        "beschreibung": "Phishing-Mail an 3 Mitarbeitende",
    }
    with patch("datenpannen.llm.generate") as mock_gen:
        mock_gen.return_value = type(
            "LR",
            (),
            {"text": "totally not JSON", "quelle": "llm", "model": "test"},
        )()
        resp = authed_client.post(
            "/api/datenpannen/risiko-vorschlag/",
            payload,
            content_type="application/json",
        )
    assert resp.status_code == 200
    assert resp.json()["risiko_vorschlag"] == RisikoStufe.GERING


def test_api_unauth_blocked(tenant_demo, settings):
    """Ohne Login: 403 (RulesPermission scheitert)."""
    from django.test import Client

    settings.ALLOWED_HOSTS = ["*"]
    client = Client(HTTP_HOST="demo-dp.app.vaeren.local")
    resp = client.get("/api/datenpannen/")
    assert resp.status_code in (401, 403)


def test_api_create_massnahme(authed_client, tenant_demo):
    with schema_context(tenant_demo.schema_name):
        panne = Datenpanne.objects.create(
            titel="X",
            art=PannenArt.PHISHING,
            beschreibung_verschluesselt="…",
            entdeckt_am=timezone.now(),
        )
        pid = panne.id
    resp = authed_client.post(
        "/api/datenpannen-massnahmen/",
        {
            "datenpanne": pid,
            "typ": MassnahmeTyp.SOFORT,
            "beschreibung": "Passwörter zurückgesetzt für alle betroffenen Accounts.",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    with schema_context(tenant_demo.schema_name):
        assert Massnahme.objects.filter(datenpanne_id=pid).count() == 1
