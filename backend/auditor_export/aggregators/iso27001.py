"""Aggregator: ISO-27001-Evidence-Sammler → ISO-27001 + NIS2.

Sammelt verifizierte Belege aus:
- ControlImplementation (verifiziert_am != NULL)
- IsmsRiskAssessment (akzeptiert_am != NULL)
- StatementOfApplicability (alle Versionen im Zeitraum)
- ManagementReview (durchgefuehrt_am != NULL)
- InternesAudit (status=abgeschlossen)
- AuditFinding (alle)

RDG: alle Records sind Human-bestätigt (verifiziert_von, akzeptiert_von, etc.).
LLM-Treatment-Vorschläge werden NICHT aus dem `entwurf`-Feld exportiert.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class ISO27001Aggregator(BaseAggregator):
    slug = "iso27001"
    norm_scopes = ("iso_27001", "nis2")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from iso27001.models import (
                AuditFinding,
                ControlImplementation,
                InternesAudit,
                IsmsRiskAssessment,
                ManagementReview,
                StatementOfApplicability,
            )
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        sub_filter = (filter_dict or {}).get(self.slug) or {}
        # only_kategorien: ["organizational", "technological", ...] → nur Controls dieser Kategorien
        only_kategorien = sub_filter.get("only_kategorien")
        # only_schweregrade: ["kritisch", "hoch"] → Findings dieser Schweregrade
        only_schweregrade = sub_filter.get("only_schweregrade")

        records: list[EvidenceRecord] = []

        # 1) Verifizierte Control-Implementationen
        impls = (
            ControlImplementation.objects.filter(
                verifiziert_am__gte=period_from_dt,
                verifiziert_am__lte=period_to_dt,
            )
            .exclude(verifiziert_von__isnull=True)
            .select_related("control", "verifiziert_von")
        )
        if only_kategorien:
            impls = impls.filter(control__kategorie__in=only_kategorien)
        for impl in impls:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"ControlImplementation:{impl.pk}",
                    titel=f"Control verifiziert: {impl.control.code} {impl.control.name}",
                    beschreibung=(impl.implementation_beschreibung or "")[:2000],
                    erstellt_am=impl.verifiziert_am,
                    verantwortlicher_email=(
                        impl.verifiziert_von.email if impl.verifiziert_von else None
                    ),
                    status=impl.status,
                    oscal_control_ids=(f"iso-27001-{impl.control.code.lower()}",),
                    raw_data={
                        "control_code": impl.control.code,
                        "control_name": impl.control.name,
                        "control_kategorie": impl.control.kategorie,
                        "applicable": impl.applicable,
                    },
                )
            )

        # 2) Akzeptierte Risiken (Treatment + Restrisiko-Akzeptanz dokumentiert)
        risiken = (
            IsmsRiskAssessment.objects.filter(
                akzeptiert_am__gte=period_from_dt,
                akzeptiert_am__lte=period_to_dt,
            )
            .exclude(akzeptiert_von__isnull=True)
            .select_related("asset", "akzeptiert_von")
        )
        for r in risiken:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"IsmsRiskAssessment:{r.pk}",
                    titel=f"Risikobehandlung dokumentiert: {r.titel}",
                    beschreibung=(
                        f"Behandlung: {r.treatment}; "
                        f"Brutto-Score: {r.risk_score_brutto}; "
                        f"Netto-Score: {r.risk_score_netto or '-'}"
                    ),
                    erstellt_am=r.akzeptiert_am,
                    verantwortlicher_email=(
                        r.akzeptiert_von.email if r.akzeptiert_von else None
                    ),
                    status=r.treatment,
                    oscal_control_ids=("iso-27001-clause-6.1",),
                    raw_data={
                        "treatment": r.treatment,
                        "risk_score_brutto": r.risk_score_brutto,
                        "risk_score_netto": r.risk_score_netto,
                    },
                )
            )

        # 3) Statement-of-Applicability — formales Bekenntnis
        for soa in StatementOfApplicability.objects.filter(
            erstellt_am__gte=period_from_dt,
            erstellt_am__lte=period_to_dt,
        ):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"StatementOfApplicability:{soa.pk}",
                    titel=f"Statement of Applicability v{soa.version}",
                    beschreibung=(soa.geltungsbereich or "")[:2000],
                    erstellt_am=soa.erstellt_am,
                    status="published",
                    oscal_control_ids=("iso-27001-clause-6.1.3-d",),
                    raw_data={
                        "version": soa.version,
                        "anzahl_controls": len(soa.snapshot_data or []),
                    },
                )
            )

        # 4) Management-Reviews
        for mr in ManagementReview.objects.filter(
            durchgefuehrt_am__gte=period_from,
            durchgefuehrt_am__lte=period_to,
        ).exclude(status="entwurf"):
            erstellt = datetime.datetime.combine(
                mr.durchgefuehrt_am, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            ergebnis = "\n\n".join(
                t for t in (
                    mr.outputs_verbesserungen,
                    mr.outputs_ressourcen_bedarf,
                    mr.outputs_zielanpassungen,
                ) if t
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"ManagementReview:{mr.pk}",
                    titel=f"Management-Review {mr.review_jahr}",
                    beschreibung=ergebnis[:2000],
                    erstellt_am=erstellt,
                    status=mr.status,
                    oscal_control_ids=("iso-27001-clause-9.3",),
                    raw_data={"review_jahr": mr.review_jahr},
                )
            )

        # 5) Abgeschlossene interne Audits
        for audit in InternesAudit.objects.filter(
            auditzeitraum_bis__gte=period_from,
            auditzeitraum_bis__lte=period_to,
            status="abgeschlossen",
        ):
            erstellt = datetime.datetime.combine(
                audit.auditzeitraum_bis or period_to, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"InternesAudit:{audit.pk}",
                    titel=f"Internes Audit: {audit.titel}",
                    beschreibung=f"Auditor: {audit.auditor}",
                    erstellt_am=erstellt,
                    status=audit.status,
                    oscal_control_ids=("iso-27001-clause-9.2",),
                    raw_data={
                        "auditzeitraum_von": str(audit.auditzeitraum_von),
                        "auditzeitraum_bis": str(audit.auditzeitraum_bis),
                        "auditor": audit.auditor,
                    },
                )
            )

        # 6) Findings — alle (auch offene) für Audit-Transparenz
        findings_qs = AuditFinding.objects.filter(
            created_at__gte=period_from_dt,
            created_at__lte=period_to_dt,
        ).select_related("audit")
        if only_schweregrade:
            findings_qs = findings_qs.filter(schweregrad__in=only_schweregrade)
        for f in findings_qs:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AuditFinding:{f.pk}",
                    titel=f"Finding ({f.schweregrad}): {f.titel}",
                    beschreibung=(f.beschreibung or "")[:2000],
                    erstellt_am=f.created_at,
                    status="erledigt" if f.erledigt_am else "offen",
                    oscal_control_ids=("iso-27001-clause-10.1",),
                    raw_data={
                        "schweregrad": f.schweregrad,
                        "audit_id": f.audit_id,
                    },
                )
            )

        yield from self.filter_records(records)

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=record.titel,
            description=record.beschreibung,
            methods=["EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": c} for c in record.oscal_control_ids],
        )


REGISTRY.register(ISO27001Aggregator())
