"""Sprint 4 Task 2: Modell-Tests für Pflichtunterweisung."""

from __future__ import annotations

import pytest
from django.db import IntegrityError
from django_tenants.utils import schema_context

from pflichtunterweisung.models import (
    QuizAntwort,
    SchulungsTask,
    SchulungsWelleStatus,
)
from tests.factories import (
    AntwortOptionFactory,
    FrageFactory,
    KursFactory,
    KursModulFactory,
    MitarbeiterFactory,
    SchulungsTaskFactory,
    SchulungsWelleFactory,
    TenantDomainFactory,
    TenantFactory,
    UserFactory,
)


@pytest.fixture
def tenant_setup(db):
    import uuid

    from django.db import connection

    schema = f"pflichtm_{uuid.uuid4().hex[:8]}"
    tenant = TenantFactory(schema_name=schema, firma_name="Pflicht GmbH")
    TenantDomainFactory(tenant=tenant, domain=f"{schema.replace('_', '-')}.app.vaeren.local")
    yield tenant
    connection.set_schema_to_public()


def test_kurs_creates_with_defaults(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        kurs = KursFactory()
        assert kurs.aktiv is True
        assert kurs.gueltigkeit_monate == 12
        assert kurs.min_richtig_prozent == 80


def test_kursmodul_unique_reihenfolge_per_kurs(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        kurs = KursFactory()
        KursModulFactory(kurs=kurs, reihenfolge=0)
        with pytest.raises(IntegrityError):
            KursModulFactory(kurs=kurs, reihenfolge=0)


def test_frage_with_options(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        kurs = KursFactory()
        frage = FrageFactory(kurs=kurs)
        AntwortOptionFactory(frage=frage, ist_korrekt=True, reihenfolge=0)
        AntwortOptionFactory(frage=frage, ist_korrekt=False, reihenfolge=1)
        AntwortOptionFactory(frage=frage, ist_korrekt=False, reihenfolge=2)

        assert frage.optionen.count() == 3
        assert frage.optionen.filter(ist_korrekt=True).count() == 1


def test_schulungs_welle_starts_in_draft(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        user = UserFactory()
        welle = SchulungsWelleFactory(erstellt_von=user)
        assert welle.status == SchulungsWelleStatus.DRAFT
        assert welle.versendet_am is None


def test_schulungs_welle_mark_sent_transitions_state(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        user = UserFactory()
        welle = SchulungsWelleFactory(erstellt_von=user)
        welle.mark_sent()
        assert welle.status == SchulungsWelleStatus.SENT
        assert welle.versendet_am is not None


def test_schulungs_welle_mark_sent_fails_if_not_draft(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        user = UserFactory()
        welle = SchulungsWelleFactory(erstellt_von=user)
        welle.mark_sent()
        with pytest.raises(ValueError, match="nicht im Status DRAFT"):
            welle.mark_sent()


def test_schulungs_task_unique_per_mitarbeiter_in_welle(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        welle = SchulungsWelleFactory()
        mit = MitarbeiterFactory()
        SchulungsTaskFactory(welle=welle, mitarbeiter=mit)
        with pytest.raises(IntegrityError):
            SchulungsTaskFactory(welle=welle, mitarbeiter=mit)


def test_schulungs_task_is_polymorphic_compliance_task(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        task = SchulungsTaskFactory()
        # Polymorphic-Manager auf ComplianceTask sollte den Subtype zurückgeben
        from core.models import ComplianceTask

        loaded = ComplianceTask.objects.get(pk=task.pk)
        assert isinstance(loaded, SchulungsTask)


def test_quiz_antwort_unique_per_task_frage(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        kurs = KursFactory()
        frage = FrageFactory(kurs=kurs)
        opt = AntwortOptionFactory(frage=frage, ist_korrekt=True)
        welle = SchulungsWelleFactory(kurs=kurs)
        task = SchulungsTaskFactory(welle=welle)
        QuizAntwort.objects.create(task=task, frage=frage, gewaehlte_option=opt, war_korrekt=True)
        with pytest.raises(IntegrityError):
            QuizAntwort.objects.create(
                task=task, frage=frage, gewaehlte_option=opt, war_korrekt=True
            )


def test_kurs_str_returns_titel(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        kurs = KursFactory(titel="DSGVO-Grundlagen")
        assert str(kurs) == "DSGVO-Grundlagen"


def test_schulungs_welle_str_includes_status(tenant_setup):
    with schema_context(tenant_setup.schema_name):
        welle = SchulungsWelleFactory(titel="Q1-Schulung")
        s = str(welle)
        assert "Q1-Schulung" in s
        assert "Entwurf" in s
