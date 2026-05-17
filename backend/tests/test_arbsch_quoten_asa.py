"""Tests Beauftragten-Quoten + ASA-Auto-Scheduling."""

from __future__ import annotations

import datetime

from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    AsaKonfig,
    AsaSitzung,
    AsaSitzungStatus,
    AsaSitzungTask,
    Beauftragter,
    BeauftragtenTyp,
)
from arbeitsschutz.services import asa_scheduling, quoten
from core.models import Mitarbeiter


def _erzeuge_mitarbeiter(n: int, abteilung: str = "Produktion") -> list:
    out = []
    for i in range(n):
        m = Mitarbeiter.objects.create(
            vorname=f"V{i}",
            nachname=f"N{i}",
            email=f"u{i}@x.de",
            abteilung=abteilung,
            rolle="MA",
            eintritt=datetime.date(2024, 1, 1),
        )
        out.append(m)
    return out


def test_sibe_quote_unter_21_ma_keine_pflicht(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _erzeuge_mitarbeiter(15)
        r = quoten.berechne(BeauftragtenTyp.SIBE)
        assert r.soll == 0
        assert r.pflicht_seit is None
        assert r.erfuellt is True


def test_sibe_quote_ab_21_ma_pflicht(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _erzeuge_mitarbeiter(25)
        r = quoten.berechne(BeauftragtenTyp.SIBE)
        assert r.soll >= 1
        assert r.pflicht_seit is not None
        assert r.erfuellt is False


def test_quoten_warnings_wenn_unterschritten(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _erzeuge_mitarbeiter(30)
        msgs = quoten.warnings()
        assert any("SiBe" in m or "Sicherheits" in m for m in msgs)


def test_quoten_refresh_alle_persistiert_check(arbsch_tenant):
    from arbeitsschutz.models import BeauftragtenQuoteCheck

    with schema_context(arbsch_tenant.schema_name):
        _erzeuge_mitarbeiter(25)
        quoten.refresh_alle()
        assert BeauftragtenQuoteCheck.objects.filter(
            typ=BeauftragtenTyp.SIBE
        ).exists()


def test_asa_jahres_termine_generierung_idempotent(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        AsaKonfig.objects.create(default_ort="Besprechungsraum", aktiv=True)
        termine = asa_scheduling.generiere_jahres_termine(2026)
        assert len(termine) == 4
        # Idempotent: zweiter Aufruf erzeugt nichts neues
        termine2 = asa_scheduling.generiere_jahres_termine(2026)
        assert len(termine2) == 0


def test_asa_sitzung_creation_triggert_task(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        from django.utils import timezone

        sitzung = AsaSitzung.objects.create(
            titel="Q1",
            geplant_am=timezone.now() + datetime.timedelta(days=30),
            quartal="2026-Q1",
        )
        assert AsaSitzungTask.objects.filter(sitzung=sitzung).count() == 1
        task = AsaSitzungTask.objects.get(sitzung=sitzung)
        assert task.frist == (sitzung.geplant_am.date() - datetime.timedelta(days=14))


def test_asa_inaktive_konfig_keine_termine(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        AsaKonfig.objects.create(aktiv=False)
        termine = asa_scheduling.generiere_jahres_termine(2026)
        assert termine == []
