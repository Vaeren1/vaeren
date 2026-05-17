"""Aggregator: Datenpannen → DSGVO Art. 33, ISO-27001.A.5.24.

RDG-Filter: `risiko_vorschlag` (LLM) ohne bestätigte `risiko` blockiert.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class DatenpannenAggregator(BaseAggregator):
    slug = "datenpannen"
    norm_scopes = ("datenpannen", "dsgvo", "iso_27001", "nis2")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from datenpannen.models import Datenpanne
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        qs = Datenpanne.objects.filter(
            entdeckt_am__gte=period_from_dt,
            entdeckt_am__lte=period_to_dt,
        )
        records = []
        for panne in qs:
            # RDG-Pflicht: LLM-Vorschlag ohne menschliche Bestätigung blockieren.
            llm_draft = bool(panne.risiko_vorschlag) and not panne.risiko

            record = EvidenceRecord(
                aggregator_slug=self.slug,
                record_id=f"Datenpanne:{panne.pk}",
                titel=f"Datenpanne: {panne.titel}",
                beschreibung=(
                    f"Art: {panne.art}; "
                    f"Status: {panne.get_status_display()}; "
                    f"Frist: {panne.frist_meldung_behoerde:%Y-%m-%d %H:%M}"
                ),
                erstellt_am=panne.entdeckt_am,
                verantwortlicher_email=(
                    panne.verantwortlicher_user.email
                    if panne.verantwortlicher_user
                    else None
                ),
                status=panne.status,
                evidence_files=(),
                oscal_control_ids=(
                    "dsgvo-art-33",
                    "iso-27001-a.5.24",
                ),
                raw_data={
                    "titel": panne.titel,
                    "art": panne.art,
                    "risiko": panne.risiko,
                    "risiko_vorschlag": panne.risiko_vorschlag,
                    "anzahl_betroffene_geschaetzt": panne.anzahl_betroffene_geschaetzt,
                    "datenkategorien": list(panne.datenkategorien or []),
                    "behoerde_gemeldet_am": (
                        panne.behoerde_gemeldet_am.isoformat()
                        if panne.behoerde_gemeldet_am
                        else None
                    ),
                    "abgeschlossen_am": (
                        panne.abgeschlossen_am.isoformat()
                        if panne.abgeschlossen_am
                        else None
                    ),
                    "llm_draft": llm_draft,
                },
            )
            records.append(record)
        yield from self.filter_records(records)

    def filter_rdg_safe(self, record: EvidenceRecord) -> bool:
        if not super().filter_rdg_safe(record):
            return False
        # Wenn nur LLM-Vorschlag vorhanden aber keine bestätigte risiko-Klasse:
        # NICHT exportieren (RDG-Layer-3-Test im Plan §10.4).
        risiko = record.raw_data.get("risiko") or ""
        risiko_vorschlag = record.raw_data.get("risiko_vorschlag") or ""
        if risiko_vorschlag and not risiko:
            return False
        return True

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
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(DatenpannenAggregator())
