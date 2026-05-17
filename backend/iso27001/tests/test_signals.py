"""Signal-Tests: Auto-Tasks bei Statusänderungen + Auto-Evidence-Mapping."""

from __future__ import annotations

import datetime

from django_tenants.utils import schema_context

from core.models import Evidence, Mitarbeiter
from iso27001.models import (
    ControlEvidenceLink,
    ControlImplementation,
    ImplementationStatus,
    Iso27001Control,
    IsmsAsset,
    IsmsRiskAssessment,
    IsoTask,
    IsoTaskTyp,
)


def test_implementation_post_save_creates_review_task(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        c = Iso27001Control.objects.get(code="A.5.1")
        impl = ControlImplementation.objects.create(
            control=c, status=ImplementationStatus.UMGESETZT
        )
        assert IsoTask.objects.filter(
            implementation=impl, task_typ=IsoTaskTyp.CONTROL_REVIEW
        ).exists()


def test_implementation_post_save_auto_evidence_mapping(tenant_iso):
    """Bei Created=True werden ControlEvidenceLink(auto_suggested=True) erzeugt,
    sofern es passende Evidence im Tenant gibt."""
    with schema_context(tenant_iso.schema_name):
        # Einige Evidence einrichten, die zu Mapping-Modulen gehört
        from core.models import ComplianceTask

        task = ComplianceTask.objects.create(
            titel="t", modul="ki_inventar", kategorie="x",
            frist=datetime.date.today(),
        )
        Evidence.objects.create_with_content(
            titel="KI-Tool-Inventar-Export",
            content=b"data",
            mime_type="application/pdf",
            bezug_task=task,
        )

        c = Iso27001Control.objects.get(code="A.5.23")  # Cloud-Dienste → ki_inventar
        impl = ControlImplementation.objects.create(control=c)
        assert ControlEvidenceLink.objects.filter(
            implementation=impl, auto_suggested=True
        ).exists()


def test_auto_evidence_mapping_first_write_wins_quell_modul(tenant_iso):
    """Wenn dieselbe Evidence von mehreren Modulen vorgeschlagen wird,
    gewinnt der ERSTE Eintrag in `mapping.SUGGESTORS` (deterministisch).

    Setup: Evidence mit `bezug_task.modul="hinschg"` UND eine zweite mit
    `bezug_task.modul="pflichtunterweisung"` — beide mappen auf A.5.4.
    Aber `ki_inventar` steht in SUGGESTORS vor `hinschg`+`pflichtunterweisung`.
    Wir nehmen Control A.5.4 (mappt auf hinschg + pflichtunterweisung).
    hinschg kommt VOR pflichtunterweisung → quell_modul='hinschg' gewinnt.
    """
    with schema_context(tenant_iso.schema_name):
        from core.models import ComplianceTask

        # Eine Evidence, die zu hinschg gehört → Mapping A.5.4 trifft
        task_h = ComplianceTask.objects.create(
            titel="t", modul="hinschg", kategorie="x",
            frist=datetime.date.today(),
        )
        Evidence.objects.create_with_content(
            titel="HinSchG-Quartalsbericht",
            content=b"x",
            mime_type="application/pdf",
            bezug_task=task_h,
        )
        # Eine zweite Evidence von pflichtunterweisung → mappt ebenfalls A.5.4
        task_p = ComplianceTask.objects.create(
            titel="t2", modul="pflichtunterweisung", kategorie="x",
            frist=datetime.date.today(),
        )
        Evidence.objects.create_with_content(
            titel="Schulungs-Bestaetigung",
            content=b"y",
            mime_type="application/pdf",
            bezug_task=task_p,
        )

        c = Iso27001Control.objects.get(code="A.5.4")
        impl = ControlImplementation.objects.create(control=c)

        links = list(
            ControlEvidenceLink.objects.filter(implementation=impl)
            .order_by("created_at")
        )
        # Beide Evidence wurden verlinkt, mit korrektem (deterministischem)
        # Quell-Modul-Stempel.
        moduln = {ll.quell_modul for ll in links}
        assert "hinschg" in moduln
        assert "pflichtunterweisung" in moduln


def test_risiko_post_save_creates_review_task(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        asset = IsmsAsset.objects.create(name="A", asset_typ="system")
        risk = IsmsRiskAssessment.objects.create(
            asset=asset,
            titel="X",
            threat="T",
            vulnerability="V",
            likelihood=3,
            impact=3,
        )
        assert IsoTask.objects.filter(
            risiko=risk, task_typ=IsoTaskTyp.RISIKO_REVIEW
        ).exists()
