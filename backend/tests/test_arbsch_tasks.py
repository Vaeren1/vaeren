"""Tests Celery-Tasks `task_ba_review_check` + `task_beauftragter_ablauf_check`.

Beide werden direkt synchron aufgerufen (kein Eager-Modus nötig), weil sie
keine Sub-Tasks aufrufen.
"""

from __future__ import annotations

import datetime

from django.utils import timezone
from django_tenants.utils import schema_context

from arbeitsschutz.models import (
    Beauftragter,
    BeauftragtenTyp,
    Betriebsanweisung,
    BetriebsanweisungReviewTask,
    BetriebsanweisungTyp,
    BetriebsanweisungVersion,
    BeauftragterAblaufTask,
)
from arbeitsschutz.tasks import (
    task_ba_review_check,
    task_beauftragter_ablauf_check,
)
from core.models import (
    ComplianceTaskStatus,
    Mitarbeiter,
    User,
)


def _erzeuge_user_und_person():
    user, _ = User.objects.get_or_create(
        email="ba@test.de", defaults={"tenant_role": "geschaeftsfuehrer"}
    )
    person = Mitarbeiter.objects.create(
        vorname="Max",
        nachname="Mustermann",
        email="max@test.de",
        abteilung="Produktion",
        rolle="MA",
        eintritt=datetime.date(2024, 1, 1),
    )
    return user, person


# --- BA-Review-Check ----------------------------------------------------


def test_ba_review_check_legt_task_bei_alter_version_an(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        user, _ = _erzeuge_user_und_person()
        ba = Betriebsanweisung.objects.create(
            titel="Schweißplatz", typ=BetriebsanweisungTyp.MASCHINE
        )
        version = BetriebsanweisungVersion.objects.create(
            betriebsanweisung=ba,
            version=1,
            inhalt_md="...",
            erstellt_von=user,
        )
        # Backdate auf 25 Monate alt
        old = timezone.now() - datetime.timedelta(days=25 * 30)
        BetriebsanweisungVersion.objects.filter(pk=version.pk).update(
            erstellt_am=old
        )
        ba.aktuelle_version = version
        ba.save(update_fields=["aktuelle_version"])

        erzeugt = task_ba_review_check()
        assert erzeugt == 1
        assert BetriebsanweisungReviewTask.objects.filter(
            betriebsanweisung=ba, status=ComplianceTaskStatus.OFFEN
        ).count() == 1


def test_ba_review_check_idempotent(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        user, _ = _erzeuge_user_und_person()
        ba = Betriebsanweisung.objects.create(
            titel="B", typ=BetriebsanweisungTyp.PSA
        )
        version = BetriebsanweisungVersion.objects.create(
            betriebsanweisung=ba, version=1, inhalt_md="x", erstellt_von=user
        )
        BetriebsanweisungVersion.objects.filter(pk=version.pk).update(
            erstellt_am=timezone.now() - datetime.timedelta(days=800)
        )
        ba.aktuelle_version = version
        ba.save(update_fields=["aktuelle_version"])

        assert task_ba_review_check() == 1
        # Zweiter Aufruf: kein neuer Task, weil schon ein offener existiert
        assert task_ba_review_check() == 0
        assert BetriebsanweisungReviewTask.objects.filter(
            betriebsanweisung=ba
        ).count() == 1


def test_ba_review_check_skipt_junge_version(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        user, _ = _erzeuge_user_und_person()
        ba = Betriebsanweisung.objects.create(
            titel="Neu", typ=BetriebsanweisungTyp.TAETIGKEIT
        )
        version = BetriebsanweisungVersion.objects.create(
            betriebsanweisung=ba, version=1, inhalt_md="x", erstellt_von=user
        )
        ba.aktuelle_version = version
        ba.save(update_fields=["aktuelle_version"])

        # erstellt_am ist gerade jetzt — nicht überfällig
        erzeugt = task_ba_review_check()
        assert erzeugt == 0
        assert BetriebsanweisungReviewTask.objects.filter(
            betriebsanweisung=ba
        ).count() == 0


# --- Beauftragten-Ablauf-Check -----------------------------------------


def test_beauftragter_ablauf_check_legt_task_an(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _, person = _erzeuge_user_und_person()
        # bestellt_bis in 30 Tagen → innerhalb 60-Tage-Schwelle
        b = Beauftragter.objects.create(
            typ=BeauftragtenTyp.SIBE,
            person=person,
            bestellt_am=datetime.date.today() - datetime.timedelta(days=365),
            bestellt_bis=datetime.date.today() + datetime.timedelta(days=30),
        )

        erzeugt = task_beauftragter_ablauf_check()
        assert erzeugt == 1
        assert BeauftragterAblaufTask.objects.filter(
            beauftragter=b, status=ComplianceTaskStatus.OFFEN
        ).count() == 1


def test_beauftragter_ablauf_check_idempotent(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _, person = _erzeuge_user_und_person()
        Beauftragter.objects.create(
            typ=BeauftragtenTyp.BRANDSCHUTZ,
            person=person,
            bestellt_am=datetime.date.today() - datetime.timedelta(days=100),
            bestellt_bis=datetime.date.today() + datetime.timedelta(days=20),
        )

        assert task_beauftragter_ablauf_check() == 1
        assert task_beauftragter_ablauf_check() == 0


def test_beauftragter_ablauf_check_ignoriert_unbefristet(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _, person = _erzeuge_user_und_person()
        Beauftragter.objects.create(
            typ=BeauftragtenTyp.ERSTHELFER,
            person=person,
            bestellt_am=datetime.date.today(),
            bestellt_bis=None,
        )
        assert task_beauftragter_ablauf_check() == 0


def test_beauftragter_ablauf_check_ignoriert_weit_in_zukunft(arbsch_tenant):
    with schema_context(arbsch_tenant.schema_name):
        _, person = _erzeuge_user_und_person()
        # >60 Tage in Zukunft → noch nicht aktionspflichtig
        Beauftragter.objects.create(
            typ=BeauftragtenTyp.ERSTHELFER,
            person=person,
            bestellt_am=datetime.date.today(),
            bestellt_bis=datetime.date.today() + datetime.timedelta(days=120),
        )
        assert task_beauftragter_ablauf_check() == 0
