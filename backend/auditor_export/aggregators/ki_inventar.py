"""Aggregator: KI-Inventar → AI-Act Anhang III + ISO-42001."""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import (
    BaseAggregator,
    EvidenceFileRef,
    EvidenceRecord,
    REGISTRY,
    stable_uuid_v5,
)


class KIInventarAggregator(BaseAggregator):
    slug = "ki_inventar"
    norm_scopes = ("ai_act", "iso_42001")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from ki_inventar.models import KITool
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        qs = KITool.objects.filter(
            created_at__gte=period_from_dt,
            created_at__lte=period_to_dt,
        )
        records = []
        for tool in qs:
            # RDG-Filter: risiko_vorschlag ohne finale `risiko`-Bestätigung blockieren
            llm_draft = bool(tool.risiko_vorschlag) and not tool.risiko
            verantwortlicher = ""

            record = EvidenceRecord(
                aggregator_slug=self.slug,
                record_id=f"KITool:{tool.pk}",
                titel=f"{tool.name} ({tool.anbieter})",
                beschreibung=tool.zweck or "",
                erstellt_am=tool.created_at,
                verantwortlicher_email=verantwortlicher or None,
                status=tool.status,
                evidence_files=(),
                oscal_control_ids=(
                    "ai-act-art-26",
                    f"ai-act-risiko-{tool.risiko or 'unbekannt'}",
                    "iso-42001-clause-6",
                ),
                raw_data={
                    "name": tool.name,
                    "anbieter": tool.anbieter,
                    "url": tool.url,
                    "kategorie": tool.kategorie,
                    "risiko": tool.risiko,
                    "risiko_vorschlag": tool.risiko_vorschlag,
                    "transparenz_information": tool.transparenz_information,
                    "menschliche_aufsicht": tool.menschliche_aufsicht,
                    "llm_draft": llm_draft,
                    "datenkategorie_sensibilitaet": tool.datenkategorie_sensibilitaet,
                },
            )
            records.append(record)
        yield from self.filter_records(records)

    def filter_rdg_safe(self, record: EvidenceRecord) -> bool:
        """Verfeinert Default: zusätzlich Tools ohne finale Risiko-Klassifizierung blockieren."""
        if not super().filter_rdg_safe(record):
            return False
        # Tools die nur einen LLM-Vorschlag, aber keine bestätigte Klassifizierung
        # haben, dürfen NICHT in den Export.
        risiko = record.raw_data.get("risiko") or ""
        if not risiko or risiko == "unbekannt":
            # In den Audit-Export gehen nur final klassifizierte Tools.
            return False
        return True

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=f"KI-Tool: {record.titel}",
            description=record.beschreibung,
            methods=["EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(KIInventarAggregator())
