"""Tests für `core.scoring.calculate_compliance_score` und Dashboard-API."""

from __future__ import annotations

import datetime

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import ComplianceTaskStatus, TenantRole
from core.scoring import calculate_compliance_score, score_to_level
from tests.factories import (
    ComplianceTaskFactory,
    MitarbeiterFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db, settings):
    import uuid

    from django.db import connection

    settings.ALLOWED_HOSTS = ["*"]
    schema = f"score_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema)
    domain = TenantDomainFactory(
        tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local"
    )
    yield tenant, domain
    connection.set_schema_to_public()


def test_score_empty_tenant_is_100(tenant_setup):
    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        score = calculate_compliance_score()
        assert score.master == 100
        assert score.level == "green"
        assert score.total_active_tasks == 0


def test_score_drops_with_overdue_tasks(tenant_setup):
    tenant, _ = tenant_setup
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    with schema_context(tenant.schema_name):
        # 4 Tasks, davon 2 überfällig
        ComplianceTaskFactory.create_batch(2, frist=yesterday, status=ComplianceTaskStatus.OFFEN)
        ComplianceTaskFactory.create_batch(
            2,
            frist=datetime.date.today() + datetime.timedelta(days=30),
            status=ComplianceTaskStatus.OFFEN,
        )
        score = calculate_compliance_score()
        # 50% überfällig → score_pflichten = 50
        assert score.score_pflichten == 50
        assert score.overdue_count == 2
        assert score.total_active_tasks == 4


def test_score_module_pflichtunterweisung_coverage(tenant_setup):
    """3 Mitarbeiter, 1 mit gültigem Zertifikat → 33 %."""
    from pflichtunterweisung.models import SchulungsTask

    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        ma_with_cert, _ma2, _ma3 = MitarbeiterFactory.create_batch(3)
        from tests.factories import KursFactory, SchulungsWelleFactory

        kurs = KursFactory()
        welle = SchulungsWelleFactory(kurs=kurs)
        SchulungsTask.objects.create(
            welle=welle,
            mitarbeiter=ma_with_cert,
            titel="t",
            modul="pflichtunterweisung",
            kategorie="schulung",
            frist=datetime.date.today() + datetime.timedelta(days=30),
            status=ComplianceTaskStatus.ERLEDIGT,
            bestanden=True,
            ablauf_datum=datetime.date.today() + datetime.timedelta(days=300),
        )
        score = calculate_compliance_score()
        pflicht_module = next(m for m in score.modules if m.modul == "pflichtunterweisung")
        assert pflicht_module.score == 33  # 1/3 ≈ 33%
        assert pflicht_module.level == "red"


def test_score_module_hinschg_drops_with_alte_offene(tenant_setup):
    """2 Meldungen > 30 d alt → score = 100 - 5*2 = 90."""
    from django.utils import timezone

    from hinschg.models import Meldung

    tenant, _ = tenant_setup
    with schema_context(tenant.schema_name):
        old = timezone.now() - datetime.timedelta(days=40)
        for _ in range(2):
            m = Meldung.objects.create(
                titel_verschluesselt="alt", beschreibung_verschluesselt="alt"
            )
            # eingegangen_am ist auto_now_add — manuell zurückdatieren via update
            Meldung.objects.filter(pk=m.pk).update(eingegangen_am=old)

        score = calculate_compliance_score()
        hinschg_module = next(m for m in score.modules if m.modul == "hinschg")
        assert hinschg_module.score == 90


def test_score_to_level_thresholds():
    assert score_to_level(95) == "green"
    assert score_to_level(90) == "green"
    assert score_to_level(89) == "yellow"
    assert score_to_level(70) == "yellow"
    assert score_to_level(69) == "red"
    assert score_to_level(0) == "red"


# --- Dashboard-API ----------------------------------------------------


def _client(tenant, domain, role: TenantRole, email: str) -> Client:
    with schema_context(tenant.schema_name):
        UserFactory(email=email, tenant_role=role, password="DashTest12!")
        client = Client(HTTP_HOST=domain.domain, enforce_csrf_checks=False)
        assert client.login(email=email, password="DashTest12!")
    return client


def test_dashboard_requires_auth(tenant_setup):
    _, domain = tenant_setup
    client = Client(HTTP_HOST=domain.domain)
    resp = client.get("/api/dashboard/")
    assert resp.status_code in (401, 403)


def test_dashboard_returns_score_and_lists(tenant_setup):
    tenant, domain = tenant_setup
    client = _client(tenant, domain, TenantRole.GESCHAEFTSFUEHRER, "gf@dash.de")
    today = datetime.date.today()
    with schema_context(tenant.schema_name):
        ComplianceTaskFactory(frist=today + datetime.timedelta(days=2))
        ComplianceTaskFactory(frist=today - datetime.timedelta(days=3))

    resp = client.get("/api/dashboard/")
    assert resp.status_code == 200
    body = resp.json()
    assert "score" in body
    assert "master" in body["score"]
    assert "level" in body["score"]
    assert "modules" in body["score"]
    assert len(body["this_week_tasks"]) == 1
    assert len(body["overdue_tasks"]) == 1
    assert "recent_activity" in body
    assert "module_summary" in body


def test_dashboard_module_summary_counts_correctly(tenant_setup):
    """Schulungen + HinSchG-Meldung in Summary."""
    from hinschg.models import Meldung
    from pflichtunterweisung.models import SchulungsWelle, SchulungsWelleStatus
    from tests.factories import KursFactory, UserFactory

    tenant, domain = tenant_setup
    client = _client(tenant, domain, TenantRole.QM_LEITER, "qm@dash.de")
    with schema_context(tenant.schema_name):
        kurs = KursFactory()
        creator = UserFactory(email="creator@dash.de")
        SchulungsWelle.objects.create(
            kurs=kurs,
            titel="W",
            deadline=datetime.date.today() + datetime.timedelta(days=30),
            erstellt_von=creator,
            status=SchulungsWelleStatus.DRAFT,
        )
        Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")

    resp = client.get("/api/dashboard/")
    body = resp.json()
    assert body["module_summary"]["pflichtunterweisung"]["aktive_wellen"] == 1
    assert body["module_summary"]["hinschg"]["offene_meldungen"] == 1
