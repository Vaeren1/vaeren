"""Aggregator: Pflichtunterweisung → DGUV-V1 + ISO-27001.A.6.3."""

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


class PflichtunterweisungAggregator(BaseAggregator):
    slug = "pflichtunterweisung"
    norm_scopes = ("pflichtunterweisung", "arbeitsschutz", "iso_27001")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from pflichtunterweisung.models import SchulungsTask
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        sub_filter = (filter_dict or {}).get(self.slug) or {}
        qs = SchulungsTask.objects.filter(
            abgeschlossen_am__gte=period_from_dt,
            abgeschlossen_am__lte=period_to_dt,
        ).select_related("welle", "welle__kurs", "mitarbeiter")

        # Default: nur bestandene. Override via filter_json={"pflichtunterweisung": {"only_bestanden": false}}.
        if sub_filter.get("only_bestanden", True):
            qs = qs.filter(bestanden=True)
        # Optionaler Min-Score-Filter (Integer-Prozent)
        min_score = sub_filter.get("min_richtig_prozent")
        if isinstance(min_score, int) and min_score > 0:
            qs = qs.filter(richtig_prozent__gte=min_score)
        records = []
        for task in qs:
            record = EvidenceRecord(
                aggregator_slug=self.slug,
                record_id=f"SchulungsTask:{task.pk}",
                titel=f"Zertifikat: {task.welle.kurs.titel} → {task.mitarbeiter}",
                beschreibung=(
                    f"Welle: {task.welle.titel}; "
                    f"Richtig: {task.richtig_prozent or 0}%; "
                    f"Zertifikat-ID: {task.zertifikat_id}"
                ),
                erstellt_am=task.abgeschlossen_am,
                verantwortlicher_email=task.mitarbeiter.email or None,
                status="bestanden",
                evidence_files=(),  # PDF wird optional vom ZIP-Builder beigelegt
                oscal_control_ids=(
                    "dguv-v1",
                    "iso-27001-a.6.3",
                ),
                raw_data={
                    "kurs_titel": task.welle.kurs.titel,
                    "welle_titel": task.welle.titel,
                    "mitarbeiter_id": task.mitarbeiter.pk,
                    "mitarbeiter_name": str(task.mitarbeiter),
                    "richtig_prozent": task.richtig_prozent,
                    "zertifikat_id": task.zertifikat_id,
                    "ablauf_datum": str(task.ablauf_datum) if task.ablauf_datum else None,
                },
            )
            records.append(record)
        yield from self.filter_records(records)

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=record.titel,
            description=record.beschreibung,
            methods=["EXAMINE", "TEST"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(PflichtunterweisungAggregator())
