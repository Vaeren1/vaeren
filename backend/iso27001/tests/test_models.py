"""Model-Smoke + Constraint-Tests für ISO-27001."""

from __future__ import annotations

import datetime

import pytest
from django.db import IntegrityError
from django_tenants.utils import schema_context

from iso27001.models import (
    AuditFinding,
    ControlImplementation,
    FindingSchweregrad,
    ImplementationStatus,
    InternesAudit,
    InternesAuditStatus,
    Iso27001Control,
    IsmsAsset,
    IsmsRiskAssessment,
    Klassifizierung,
    AssetTyp,
    ManagementReview,
    RiskTreatment,
)


def test_implementation_unique_per_control(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        c = Iso27001Control.objects.get(code="A.5.1")
        ControlImplementation.objects.create(control=c)
        with pytest.raises(IntegrityError):
            ControlImplementation.objects.create(control=c)


def test_risk_score_auto_berechnung(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        asset = IsmsAsset.objects.create(
            name="Server",
            asset_typ=AssetTyp.SYSTEM,
            klassifizierung=Klassifizierung.VERTRAULICH,
        )
        risk = IsmsRiskAssessment.objects.create(
            asset=asset,
            titel="Ausfall",
            threat="Hardware-Defekt",
            vulnerability="keine Redundanz",
            likelihood=4,
            impact=5,
            treatment=RiskTreatment.REDUZIEREN,
        )
        assert risk.risk_score_brutto == 20
        assert risk.risk_score_netto is None

        risk.restrisiko_likelihood = 2
        risk.restrisiko_impact = 3
        risk.save()
        assert risk.risk_score_netto == 6


def test_mgt_review_unique_per_jahr(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        ManagementReview.objects.create(review_jahr=2026)
        with pytest.raises(IntegrityError):
            ManagementReview.objects.create(review_jahr=2026)


def test_implementation_defaults(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        c = Iso27001Control.objects.get(code="A.6.3")
        impl = ControlImplementation.objects.create(control=c)
        assert impl.status == ImplementationStatus.NICHT_BEWERTET
        assert impl.anwendbar is True
        assert impl.implementation_vorschlag == ""


def test_audit_with_finding(tenant_iso):
    with schema_context(tenant_iso.schema_name):
        today = datetime.date.today()
        audit = InternesAudit.objects.create(
            titel="Q1-Audit",
            auditzeitraum_von=today,
            auditzeitraum_bis=today + datetime.timedelta(days=14),
            auditor="Frau Müller",
            status=InternesAuditStatus.LAUFEND,
        )
        finding = AuditFinding.objects.create(
            audit=audit,
            schweregrad=FindingSchweregrad.GROSS,
            beschreibung="Backup-Test fehlt seit 18 Monaten",
            geplant_bis=today + datetime.timedelta(days=30),
        )
        assert finding.audit == audit
        assert audit.findings.count() == 1
