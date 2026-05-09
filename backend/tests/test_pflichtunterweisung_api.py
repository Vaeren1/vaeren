"""Sprint 4 Tasks 3+4+6+7+8: API-Tests für pflichtunterweisung-Modul."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.test import Client
from django_tenants.utils import (
    schema_context,
)

from core.models import ComplianceTaskStatus, TenantRole
from pflichtunterweisung.models import (
    SchulungsTask,
    SchulungsWelle,
    SchulungsWelleStatus,
)
from pflichtunterweisung.tokens import make_token, parse_token
from tests.factories import (
    AntwortOptionFactory,
    FrageFactory,
    KursFactory,
    KursModulFactory,
    MitarbeiterFactory,
    SchulungsWelleFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db, settings):
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"pflapi_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="Pflicht-API GmbH")
    domain = TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant, domain
    # Connection auf public zurück, damit nächste Fixture wieder public-Modelle anlegen kann
    connection.set_schema_to_public()


def _qm_client(tenant, domain) -> tuple[Client, object]:
    """Erzeuge Client + QM-User. Login muss innerhalb des Tenant-Schemas geschehen,
    weil Django.Client.login() den User direkt per ORM-Query lädt (kein
    HTTP-Round-Trip → keine django-tenants-Middleware).
    """
    with schema_context(tenant.schema_name):
        user = UserFactory(
            email="qm@pflapi.de",
            tenant_role=TenantRole.QM_LEITER,
            password="QmPass1234!",
        )
        client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
        ok = client.login(email="qm@pflapi.de", password="QmPass1234!")
        assert ok
    return client, user


# --- Kurs-CRUD ---------------------------------------------------------


def test_kurs_list_requires_auth(tenant_setup):
    _tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/kurse/")
    assert resp.status_code in (401, 403)


def test_qm_can_create_kurs(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    resp = client.post(
        "/api/kurse/",
        {"titel": "DSGVO 2026", "beschreibung": "Pflicht", "min_richtig_prozent": 75},
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["titel"] == "DSGVO 2026"
    assert body["min_richtig_prozent"] == 75


def test_qm_kurs_list_returns_data(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        KursFactory(titel="A")
        KursFactory(titel="B")
    resp = client.get("/api/kurse/")
    assert resp.status_code == 200
    body = resp.json()
    rows = body["results"] if isinstance(body, dict) else body
    titles = [r["titel"] for r in rows]
    assert "A" in titles and "B" in titles


def test_view_only_role_cannot_edit_kurs(tenant_setup):
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        UserFactory(
            email="vo@pflapi.de",
            tenant_role=TenantRole.MITARBEITER_VIEW_ONLY,
            password="VoPass1234!",
        )
        client = Client(HTTP_HOST=domain.domain)
        assert client.login(email="vo@pflapi.de", password="VoPass1234!")
    resp = client.post(
        "/api/kurse/",
        {"titel": "X"},
        content_type="application/json",
    )
    assert resp.status_code == 403


# --- SchulungsWelle ----------------------------------------------------


def test_create_welle_sets_erstellt_von_to_request_user(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory()
    resp = client.post(
        "/api/schulungswellen/",
        {
            "kurs": kurs.pk,
            "titel": "Q2-Welle",
            "deadline": (date.today() + timedelta(days=14)).isoformat(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    welle_id = resp.json()["id"]
    with schema_context(tenant.schema_name):
        welle = SchulungsWelle.objects.get(pk=welle_id)
        assert welle.erstellt_von_id == user.pk
        assert welle.status == SchulungsWelleStatus.DRAFT


def test_zuweisen_creates_schulungs_tasks(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        kurs = KursFactory()
        welle = SchulungsWelleFactory(kurs=kurs, erstellt_von=user)
        m1 = MitarbeiterFactory()
        m2 = MitarbeiterFactory()
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/zuweisen/",
        {"mitarbeiter_ids": [m1.pk, m2.pk]},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["zugewiesen"] == 2
    with schema_context(tenant.schema_name):
        assert welle.tasks.count() == 2


def test_zuweisen_idempotent_when_called_twice(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
        m = MitarbeiterFactory()
    client.post(
        f"/api/schulungswellen/{welle.pk}/zuweisen/",
        {"mitarbeiter_ids": [m.pk]},
        content_type="application/json",
    )
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/zuweisen/",
        {"mitarbeiter_ids": [m.pk]},
        content_type="application/json",
    )
    body = resp.json()
    assert body["zugewiesen"] == 0
    assert body["bereits_zugewiesen"] == 1


def test_zuweisen_blocked_when_welle_not_draft(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
        welle.status = SchulungsWelleStatus.SENT
        welle.save()
        m = MitarbeiterFactory()
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/zuweisen/",
        {"mitarbeiter_ids": [m.pk]},
        content_type="application/json",
    )
    assert resp.status_code == 409


def test_personalisieren_returns_static_fallback_without_api_key(tenant_setup, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/personalisieren/",
        {"kontext": "Q2-Refresh"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["quelle"] == "static"
    assert body["vorschlag"].startswith("Vorschlag:")


def test_personalisieren_uses_llm_when_key_set(tenant_setup, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
    with patch(
        "core.llm_client._call_openrouter",
        return_value="Vorschlag: Hallo Team, kurze Schulung. Bitte prüfen.",
    ):
        resp = client.post(
            f"/api/schulungswellen/{welle.pk}/personalisieren/",
            {"kontext": ""},
            content_type="application/json",
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["quelle"] == "llm"


def test_versenden_transitions_state_and_sends_mail(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
        m = MitarbeiterFactory()
    client.post(
        f"/api/schulungswellen/{welle.pk}/zuweisen/",
        {"mitarbeiter_ids": [m.pk]},
        content_type="application/json",
    )
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/versenden/",
        {},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["versendet_an"] == 1
    assert body["welle_status"] == SchulungsWelleStatus.SENT
    with schema_context(tenant.schema_name):
        welle.refresh_from_db()
        assert welle.status == SchulungsWelleStatus.SENT
        assert welle.versendet_am is not None


def test_versenden_blocked_without_tasks(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _qm_client(tenant, domain)
    with schema_context(tenant.schema_name):
        welle = SchulungsWelleFactory(erstellt_von=user)
    resp = client.post(
        f"/api/schulungswellen/{welle.pk}/versenden/", {}, content_type="application/json"
    )
    assert resp.status_code == 400


# --- Token-Helper ------------------------------------------------------


def test_token_round_trip():
    tok = make_token(123)
    assert parse_token(tok) == 123


def test_invalid_token_returns_none():
    assert parse_token("totaler-Quatsch") is None


# --- Public Schulungs-Endpoints ----------------------------------------


@pytest.fixture
def public_quiz_setup(tenant_setup):
    tenant, domain = tenant_setup
    with schema_context(tenant.schema_name):
        kurs = KursFactory(min_richtig_prozent=50)
        KursModulFactory(kurs=kurs, titel="Modul 1", reihenfolge=0)
        f1 = FrageFactory(kurs=kurs, reihenfolge=0)
        AntwortOptionFactory(frage=f1, ist_korrekt=True, reihenfolge=0)
        AntwortOptionFactory(frage=f1, ist_korrekt=False, reihenfolge=1)
        f2 = FrageFactory(kurs=kurs, reihenfolge=1)
        AntwortOptionFactory(frage=f2, ist_korrekt=True, reihenfolge=0)
        AntwortOptionFactory(frage=f2, ist_korrekt=False, reihenfolge=1)
        u = UserFactory(email="creator@pflapi.de")
        welle = SchulungsWelleFactory(kurs=kurs, erstellt_von=u)
        m = MitarbeiterFactory()
        task = SchulungsTask.objects.create(
            welle=welle,
            mitarbeiter=m,
            titel="Schulung",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=welle.deadline,
            status=ComplianceTaskStatus.OFFEN,
        )
        token = make_token(task.pk)
    return tenant, domain, task, token


def test_public_resolve_returns_kurs_module_fragen(public_quiz_setup):
    _tenant, domain, task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get(f"/api/public/schulung/{token}/")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["task_id"] == task.pk
    assert len(body["fragen"]) == 2
    # Kein ist_korrekt-Leak im public-Output
    for frage in body["fragen"]:
        for opt in frage["optionen"]:
            assert "ist_korrekt" not in opt


def test_public_resolve_invalid_token_404(tenant_setup):
    _tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/public/schulung/garbage-token/")
    assert resp.status_code == 404


def test_public_start_transitions_status(public_quiz_setup):
    tenant, domain, task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.post(
        f"/api/public/schulung/{token}/start/", "{}", content_type="application/json"
    )
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        task.refresh_from_db()
        assert task.status == ComplianceTaskStatus.IN_BEARBEITUNG


def test_public_full_quiz_flow_passes(public_quiz_setup):
    tenant, domain, _task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)

    # Resolve um Fragen zu lesen
    resp = client.get(f"/api/public/schulung/{token}/")
    fragen = resp.json()["fragen"]

    # Beide korrekte Antworten klicken
    with schema_context(tenant.schema_name):
        for frage_data in fragen:
            from pflichtunterweisung.models import Frage

            f = Frage.objects.get(pk=frage_data["id"])
            korrekt_opt = f.optionen.get(ist_korrekt=True)
            korrekte_id = korrekt_opt.pk
            client.post(
                f"/api/public/schulung/{token}/antwort/",
                {"frage_id": f.pk, "option_id": korrekte_id},
                content_type="application/json",
            )

    resp = client.post(
        f"/api/public/schulung/{token}/abschliessen/", "{}", content_type="application/json"
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["bestanden"] is True
    assert body["richtig_prozent"] == 100
    assert body["zertifikat_id"]


def test_public_quiz_below_threshold_fails(public_quiz_setup):
    tenant, domain, _task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)

    # Nur eine falsche Antwort
    with schema_context(tenant.schema_name):
        from pflichtunterweisung.models import Frage

        for f in Frage.objects.all():
            falsch_opt = f.optionen.filter(ist_korrekt=False).first()
            client.post(
                f"/api/public/schulung/{token}/antwort/",
                {"frage_id": f.pk, "option_id": falsch_opt.pk},
                content_type="application/json",
            )
    resp = client.post(
        f"/api/public/schulung/{token}/abschliessen/", "{}", content_type="application/json"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["bestanden"] is False
    assert body["zertifikat_id"] is None


def test_public_abschliessen_requires_all_fragen(public_quiz_setup):
    _tenant, domain, _task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)
    # Keine Antworten gesetzt
    resp = client.post(
        f"/api/public/schulung/{token}/abschliessen/", "{}", content_type="application/json"
    )
    assert resp.status_code == 400


def test_public_zertifikat_returns_html_when_passed(public_quiz_setup):
    tenant, domain, task, token = public_quiz_setup
    # Forciere bestanden
    with schema_context(tenant.schema_name):
        task.bestanden = True
        task.zertifikat_id = "test-cert-id"
        task.richtig_prozent = 100
        from datetime import datetime

        task.abgeschlossen_am = datetime(2026, 5, 1, 12, 0)
        task.ablauf_datum = date(2027, 5, 1)
        task.save()
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get(f"/api/public/schulung/{token}/zertifikat/")
    assert resp.status_code == 200
    # Egal ob HTML-Fallback oder PDF — Content sollte nicht-leer sein
    assert len(resp.content) > 100
    ct = resp["Content-Type"]
    assert "pdf" in ct or "html" in ct


def test_public_zertifikat_blocked_when_not_passed(public_quiz_setup):
    _tenant, domain, _task, token = public_quiz_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get(f"/api/public/schulung/{token}/zertifikat/")
    assert resp.status_code == 403
