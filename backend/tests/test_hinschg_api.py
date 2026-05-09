"""Sprint 5 API-Tests für HinSchG-Modul (public + intern)."""

from __future__ import annotations

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import ComplianceTaskStatus, TenantRole
from hinschg.models import (
    Bearbeitungsschritt,
    Meldung,
    MeldungsTaskTyp,
    MeldungStatus,
)
from tests.factories import TenantDomainFactory, TenantFactory, UserFactory


@pytest.fixture
def tenant_setup(db, settings):
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"hinapi_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="HinSchG-API GmbH")
    domain = TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant, domain
    connection.set_schema_to_public()


def _client(tenant, domain, role: TenantRole, email: str) -> tuple[Client, object]:
    """Erzeuge auth Client mit gegebener Rolle innerhalb Tenant-Schema."""
    with schema_context(tenant.schema_name):
        user = UserFactory(email=email, tenant_role=role, password="HinTest1234!")
        client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
        assert client.login(email=email, password="HinTest1234!")
    return client, user


# --- Public-Endpoints --------------------------------------------------


def test_public_meldung_submit_creates_encrypted_meldung_and_two_tasks(tenant_setup):
    tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.post(
        "/api/public/hinschg/meldung/",
        data={
            "titel": "Verdacht: Bestechung im Einkauf",
            "beschreibung": "Beobachtung am 2026-05-08 um 14:30 in Halle 3.",
            "anonym": True,
        },
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert "eingangs_token" in body
    assert body["status_url"].endswith(f"/hinweise/status/{body['eingangs_token']}")

    with schema_context(tenant.schema_name):
        m = Meldung.objects.get(eingangs_token=body["eingangs_token"])
        assert m.beschreibung_verschluesselt.startswith("Beobachtung")
        assert m.titel_verschluesselt == "Verdacht: Bestechung im Einkauf"
        assert m.anonym is True
        assert m.tasks.count() == 2
        typen = {t.pflicht_typ for t in m.tasks.all()}
        assert typen == {MeldungsTaskTyp.BESTAETIGUNG_7D, MeldungsTaskTyp.RUECKMELDUNG_3M}


def test_public_meldung_submit_persoenlich_stores_kontakt(tenant_setup):
    tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.post(
        "/api/public/hinschg/meldung/",
        data={
            "titel": "Mit Kontakt",
            "beschreibung": "Inhalt",
            "melder_kontakt": "max@example.com",
            "anonym": False,
        },
        content_type="application/json",
    )
    assert resp.status_code == 201
    token = resp.json()["eingangs_token"]
    with schema_context(tenant.schema_name):
        m = Meldung.objects.get(eingangs_token=token)
        assert m.anonym is False
        assert m.melder_kontakt_verschluesselt == "max@example.com"


def test_public_status_returns_sanitized_payload(tenant_setup):
    tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="geheim")
        # Bearbeitungsschritt mit sensiblem Inhalt
        Bearbeitungsschritt.objects.create(
            meldung=m,
            bearbeiter=None,
            aktion="klassifizierung",
            notiz_verschluesselt="INTERN: Geheimer Bewertungstext.",
        )
        token = m.eingangs_token

    resp = client.get(f"/api/public/hinschg/status/{token}/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == MeldungStatus.EINGEGANGEN.value
    # Sanitized: NUR aktion + timestamp, KEINE notiz, KEINE bearbeiter-Identität
    schritte = body["bearbeitungsschritte"]
    assert len(schritte) == 1
    assert "notiz" not in schritte[0]
    assert "bearbeiter" not in schritte[0]
    assert "geheim" not in resp.content.decode()
    assert "INTERN" not in resp.content.decode()


def test_public_status_404_unknown_token(tenant_setup):
    _, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/public/hinschg/status/unbekannt-1234/")
    assert resp.status_code == 404


def test_public_hinweisgeber_nachricht_creates_anonymous_step(tenant_setup):
    tenant, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")
        token = m.eingangs_token

    resp = client.post(
        f"/api/public/hinschg/status/{token}/nachricht/",
        data={"nachricht": "Nachgereichter Beleg: zwei Zeugen sind anwesend."},
        content_type="application/json",
    )
    assert resp.status_code == 201
    with schema_context(tenant.schema_name):
        m.refresh_from_db()
        s = m.bearbeitungsschritte.get(aktion="hinweisgeber_nachricht")
        assert s.bearbeiter is None
        assert s.notiz_verschluesselt.startswith("Nachgereichter Beleg")


# --- Internal: Permission-Matrix --------------------------------------


@pytest.mark.parametrize(
    "role,can_view,can_edit",
    [
        (TenantRole.GESCHAEFTSFUEHRER, True, False),
        (TenantRole.COMPLIANCE_BEAUFTRAGTER, True, True),
        (TenantRole.QM_LEITER, False, False),
        (TenantRole.IT_LEITER, False, False),
        (TenantRole.MITARBEITER_VIEW_ONLY, False, False),
    ],
)
def test_internal_permission_matrix(tenant_setup, role, can_view, can_edit):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, role, f"{role.value}@hin.de")
    with schema_context(tenant.schema_name):
        Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")

    list_resp = client.get("/api/hinschg/meldungen/")
    if can_view:
        assert list_resp.status_code == 200
    else:
        assert list_resp.status_code in (401, 403)

    # PATCH (edit) — versuche kategorie zu setzen
    with schema_context(tenant.schema_name):
        m = Meldung.objects.first()
    patch_resp = client.patch(
        f"/api/hinschg/meldungen/{m.id}/",
        data={"kategorie": "korruption"},
        content_type="application/json",
    )
    if can_edit:
        assert patch_resp.status_code == 200
    else:
        assert patch_resp.status_code in (401, 403)


def test_internal_detail_returns_decrypted_content(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, TenantRole.COMPLIANCE_BEAUFTRAGTER, "compl@hin.de")
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(
            titel_verschluesselt="Geheimtitel",
            beschreibung_verschluesselt="Geheim-Inhalt-XYZ",
        )

    resp = client.get(f"/api/hinschg/meldungen/{m.id}/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["titel_verschluesselt"] == "Geheimtitel"
    assert body["beschreibung_verschluesselt"] == "Geheim-Inhalt-XYZ"
    assert len(body["tasks"]) == 2


def test_internal_bestaetigen_closes_7d_task(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, TenantRole.COMPLIANCE_BEAUFTRAGTER, "c@hin.de")
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")

    resp = client.post(f"/api/hinschg/meldungen/{m.id}/bestaetigen/")
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        m.refresh_from_db()
        assert m.bestaetigung_versandt_am is not None
        assert m.status == MeldungStatus.BESTAETIGT
        bestaetigung_task = m.tasks.get(pflicht_typ=MeldungsTaskTyp.BESTAETIGUNG_7D)
        assert bestaetigung_task.status == ComplianceTaskStatus.ERLEDIGT
        rueck = m.tasks.get(pflicht_typ=MeldungsTaskTyp.RUECKMELDUNG_3M)
        assert rueck.status == ComplianceTaskStatus.OFFEN


def test_internal_abschliessen_sets_archiv_loeschdatum(tenant_setup):
    tenant, domain = tenant_setup
    client, _ = _client(tenant, domain, TenantRole.COMPLIANCE_BEAUFTRAGTER, "c2@hin.de")
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")

    resp = client.post(f"/api/hinschg/meldungen/{m.id}/abschliessen/")
    assert resp.status_code == 200
    with schema_context(tenant.schema_name):
        m.refresh_from_db()
        assert m.status == MeldungStatus.ABGESCHLOSSEN
        assert m.abgeschlossen_am is not None
        assert m.archiv_loeschdatum is not None
        # ~3 Jahre = 365*3 Tage
        days = (m.archiv_loeschdatum - m.abgeschlossen_am.date()).days
        assert 1090 <= days <= 1100
        # Alle Tasks ERLEDIGT
        assert all(t.status == ComplianceTaskStatus.ERLEDIGT for t in m.tasks.all())


def test_internal_bearbeitungsschritt_creation_audited(tenant_setup):
    tenant, domain = tenant_setup
    client, user = _client(tenant, domain, TenantRole.COMPLIANCE_BEAUFTRAGTER, "c3@hin.de")
    with schema_context(tenant.schema_name):
        m = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")

    resp = client.post(
        f"/api/hinschg/meldungen/{m.id}/bearbeitungsschritte/",
        data={
            "aktion": "klassifizierung",
            "notiz_verschluesselt": "Schweregrad MITTEL nach Erstprüfung.",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201
    with schema_context(tenant.schema_name):
        from core.models import AuditLog

        m.refresh_from_db()
        s = m.bearbeitungsschritte.get(aktion="klassifizierung")
        assert s.bearbeiter == user
        assert s.notiz_verschluesselt.startswith("Schweregrad")
        # AuditLog enthält Schritt-Erstellung
        assert AuditLog.objects.filter(
            actor=user, aktion="create", aenderung_diff__aktion="klassifizierung"
        ).exists()


@pytest.mark.tenant_isolation
def test_internal_meldungen_isolated_across_tenants(db, settings):
    """Compliance-Beauftragter A sieht NIE Meldungen von Tenant B."""
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    a = TenantFactory(schema_name=f"iso_a_{uuid.uuid4().hex[:6]}")
    a_dom = TenantDomainFactory(
        tenant=a, domain=f"{a.schema_name.replace('_', '-')}.app.vaeren.local"
    )
    b = TenantFactory(schema_name=f"iso_b_{uuid.uuid4().hex[:6]}")
    b_dom = TenantDomainFactory(
        tenant=b, domain=f"{b.schema_name.replace('_', '-')}.app.vaeren.local"
    )

    with schema_context(a.schema_name):
        UserFactory(
            email="a@compl.de",
            tenant_role=TenantRole.COMPLIANCE_BEAUFTRAGTER,
            password="P@ssw0rd!12",
        )
        Meldung.objects.create(
            titel_verschluesselt="A-only", beschreibung_verschluesselt="A-secret"
        )
    with schema_context(b.schema_name):
        UserFactory(
            email="b@compl.de",
            tenant_role=TenantRole.COMPLIANCE_BEAUFTRAGTER,
            password="P@ssw0rd!12",
        )
        Meldung.objects.create(
            titel_verschluesselt="B-only", beschreibung_verschluesselt="B-secret"
        )

    client_a = Client(HTTP_HOST=a_dom.domain, enforce_csrf_checks=False)
    with schema_context(a.schema_name):
        assert client_a.login(email="a@compl.de", password="P@ssw0rd!12")
    list_a = client_a.get("/api/hinschg/meldungen/").json()
    assert len(list_a) == 1
    assert list_a[0]["titel"] == "A-only"

    client_b = Client(HTTP_HOST=b_dom.domain, enforce_csrf_checks=False)
    with schema_context(b.schema_name):
        assert client_b.login(email="b@compl.de", password="P@ssw0rd!12")
    list_b = client_b.get("/api/hinschg/meldungen/").json()
    assert len(list_b) == 1
    assert list_b[0]["titel"] == "B-only"

    # HTTP-Aufrufe via Test-Client switchen schema; teardown auf public.
    connection.set_schema_to_public()
