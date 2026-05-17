"""Aggregator: ISO-42001 (KI-Management-System) → ISO-42001-Norm-Mappe.

Sammelt verifizierte Belege aus:
- ControlImplementation (status=abgeschlossen, mit last_reviewed_at)
- AiPolicy (aktiv=True, ratified_at != NULL)
- AiSystemRegistration (alle im Zeitraum erstellt)
- AiImpactAssessment (status=freigegeben, approved_at)
- AiIncident (abgeschlossen_am != NULL)
- AimsManagementReview (durchgefuehrt_am)

RDG: AIIAs in `entwurf`/`bewertung` werden ausgefiltert (default-Filter).
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class ISO42001Aggregator(BaseAggregator):
    slug = "iso42001"
    norm_scopes = ("iso_42001", "ai_act")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from iso42001.models import (
                AiImpactAssessment,
                AiIncident,
                AiPolicy,
                AiSystemRegistration,
                AimsManagementReview,
                ControlImplementation,
            )
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        records: list[EvidenceRecord] = []

        # 1) Abgeschlossene Control-Implementations
        for impl in ControlImplementation.objects.filter(
            status="abgeschlossen",
            last_reviewed_at__gte=period_from_dt,
            last_reviewed_at__lte=period_to_dt,
        ).select_related("verantwortlicher"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AIMSControl:{impl.pk}",
                    titel=f"AIMS-Control {impl.control_code} abgeschlossen",
                    beschreibung=(impl.beschreibung or "")[:2000],
                    erstellt_am=impl.last_reviewed_at,
                    verantwortlicher_email=(
                        impl.verantwortlicher.email if impl.verantwortlicher else None
                    ),
                    status=impl.status,
                    oscal_control_ids=(f"iso-42001-{impl.control_code.lower()}",),
                    raw_data={
                        "control_code": impl.control_code,
                        "anwendbar": impl.anwendbar,
                    },
                )
            )

        # 2) Ratifizierte Policies
        for policy in AiPolicy.objects.filter(
            aktiv=True,
            ratified_at__gte=period_from,
            ratified_at__lte=period_to,
        ).select_related("ratified_by"):
            erstellt = datetime.datetime.combine(
                policy.ratified_at, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AiPolicy:{policy.pk}",
                    titel=f"KI-Policy ratifiziert: {policy.titel} v{policy.version}",
                    beschreibung=policy.inhalt_markdown[:2000],
                    erstellt_am=erstellt,
                    verantwortlicher_email=(
                        policy.ratified_by.email if policy.ratified_by else None
                    ),
                    status="aktiv",
                    oscal_control_ids=("iso-42001-clause-5.2",),
                    raw_data={
                        "geltungsbereich": policy.geltungsbereich,
                        "version": policy.version,
                    },
                )
            )

        # 3) AI-System-Registrierungen
        for reg in AiSystemRegistration.objects.filter(
            in_aims_scope=True,
            created_at__gte=period_from_dt,
            created_at__lte=period_to_dt,
        ).select_related("ki_tool", "verantwortliche_rolle"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AiSystemRegistration:{reg.pk}",
                    titel=f"KI-System im AIMS: {reg.ki_tool.name}",
                    beschreibung=(
                        f"Risiko-AIMS: {reg.risiko_aims}; "
                        f"Bias-Tests: {'ja' if reg.bias_tests_durchgefuehrt else 'nein'}; "
                        f"Monitoring: {(reg.monitoring_plan or '-')[:200]}"
                    ),
                    erstellt_am=reg.created_at,
                    verantwortlicher_email=(
                        reg.verantwortliche_rolle.email
                        if reg.verantwortliche_rolle
                        else None
                    ),
                    status="registriert",
                    oscal_control_ids=("iso-42001-a.3.2",),
                    raw_data={
                        "ki_tool_id": reg.ki_tool_id,
                        "risiko_aims": reg.risiko_aims,
                        "bias_tests": reg.bias_tests_durchgefuehrt,
                    },
                )
            )

        # 4) Freigegebene AIIAs (4-Augen!)
        for aiia in AiImpactAssessment.objects.filter(
            status="freigegeben",
            approved_at__gte=period_from_dt,
            approved_at__lte=period_to_dt,
        ).select_related("ai_system__ki_tool", "approver"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AiImpactAssessment:{aiia.pk}",
                    titel=f"AIIA freigegeben: {aiia.titel} v{aiia.version}",
                    beschreibung=(
                        f"Zweck: {aiia.zweck_beschreibung[:500]}\n\n"
                        f"Mitigationen: {(aiia.mitigationen or '')[:500]}\n\n"
                        f"Restrisiko: {(aiia.restrisiko or '')[:500]}"
                    ),
                    erstellt_am=aiia.approved_at,
                    verantwortlicher_email=(
                        aiia.approver.email if aiia.approver else None
                    ),
                    status="freigegeben",
                    oscal_control_ids=("iso-42001-a.5.2",),
                    raw_data={
                        "ai_system_id": aiia.ai_system_id,
                        "auswirkungs_kategorien": aiia.auswirkungs_kategorien,
                        "restrisiko_akzeptabel": aiia.restrisiko_akzeptabel,
                        "version": aiia.version,
                    },
                )
            )

        # 5) Abgeschlossene Incidents
        for inc in AiIncident.objects.filter(
            abgeschlossen_am__gte=period_from,
            abgeschlossen_am__lte=period_to,
        ).select_related("erfasser"):
            erstellt = datetime.datetime.combine(
                inc.abgeschlossen_am, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AiIncident:{inc.pk}",
                    titel=f"KI-Incident: {inc.titel}",
                    beschreibung=(
                        f"Typ: {inc.typ}; Schweregrad: {inc.schweregrad}\n"
                        f"Sofort: {(inc.sofortmassnahme or '-')[:400]}\n"
                        f"Korrektur: {(inc.korrekturmassnahme or '-')[:400]}"
                    ),
                    erstellt_am=erstellt,
                    status="abgeschlossen",
                    oscal_control_ids=("iso-42001-a.9.2",),
                    raw_data={
                        "typ": inc.typ,
                        "schweregrad": inc.schweregrad,
                        "gemeldet_an_bnetza": inc.gemeldet_an_bnetza,
                    },
                )
            )

        # 6) Management-Reviews
        for mr in AimsManagementReview.objects.filter(
            durchgefuehrt_am__gte=period_from,
            durchgefuehrt_am__lte=period_to,
        ).select_related("freigegeben_von"):
            erstellt = datetime.datetime.combine(
                mr.durchgefuehrt_am, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AimsManagementReview:{mr.pk}",
                    titel=f"AIMS Management-Review {mr.durchgefuehrt_am.year}",
                    beschreibung=(mr.entscheidungen or "")[:2000],
                    erstellt_am=erstellt,
                    verantwortlicher_email=(
                        mr.freigegeben_von.email if mr.freigegeben_von else None
                    ),
                    status="durchgefuehrt",
                    oscal_control_ids=("iso-42001-clause-9.3",),
                    raw_data={
                        "naechste_review": str(mr.naechste_review_faellig_am),
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


REGISTRY.register(ISO42001Aggregator())
