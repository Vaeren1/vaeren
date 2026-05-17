"""Aggregator: NIS2 → Art. 21, ISO-27001-Familien."""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class NIS2Aggregator(BaseAggregator):
    slug = "nis2"
    norm_scopes = ("nis2", "iso_27001")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from nis2.models import (
                Asset,
                BetroffenheitsCheck,
                KontrollAntwort,
            )
        except ImportError:
            return

        records = []

        # BetroffenheitsCheck (Singleton)
        check = BetroffenheitsCheck.objects.first()
        if check and check.updated_at.date() <= period_to:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"BetroffenheitsCheck:{check.pk}",
                    titel="NIS2-Betroffenheits-Check",
                    beschreibung=(
                        f"Sektor: {check.sektor}; "
                        f"Klassifizierung: {check.get_klassifizierung_display()}; "
                        f"MA: {check.mitarbeiter_anzahl or 0}"
                    ),
                    erstellt_am=datetime.datetime.combine(
                        check.created_at.date(), datetime.time.min
                    ).replace(tzinfo=datetime.UTC)
                    if hasattr(check.created_at, "date")
                    else check.created_at,
                    status=check.klassifizierung,
                    oscal_control_ids=("nis2-art-21", "iso-27001-clause-4"),
                    raw_data={
                        "sektor": check.sektor,
                        "klassifizierung": check.klassifizierung,
                        "mitarbeiter_anzahl": check.mitarbeiter_anzahl,
                        "jahresumsatz_eur": check.jahresumsatz_eur,
                        "begruendung": check.begruendung,
                    },
                )
            )

        # Assets im Zeitraum
        qs_assets = Asset.objects.filter(
            created_at__date__gte=period_from,
            created_at__date__lte=period_to,
        )
        for asset in qs_assets:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Asset:{asset.pk}",
                    titel=f"Asset: {asset.name}",
                    beschreibung=asset.beschreibung or f"Typ: {asset.typ}",
                    erstellt_am=asset.created_at,
                    status="aktiv",
                    oscal_control_ids=("nis2-art-21-a", "iso-27001-a.5.9"),
                    raw_data={
                        "name": asset.name,
                        "typ": asset.typ,
                        "kritikalitaet": asset.kritikalitaet,
                        "eigentuemer": asset.eigentuemer,
                        "schutzziele": list(asset.schutzziele or []),
                    },
                )
            )

        # KontrollAntworten — Reife-Score-Belege
        qs_antworten = KontrollAntwort.objects.filter(
            updated_at__date__lte=period_to,
        )
        for ant in qs_antworten:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"KontrollAntwort:{ant.pk}",
                    titel=f"NIS2-Kontrolle: {ant.titel}",
                    beschreibung=(
                        f"Reife-Stufe: {ant.reife_stufe}/4; Nachweis: {ant.nachweis[:80]}"
                    ),
                    erstellt_am=ant.created_at,
                    status=f"reife_{ant.reife_stufe}",
                    oscal_control_ids=(f"nis2-art-21-{ant.frage_id}",),
                    raw_data={
                        "frage_id": ant.frage_id,
                        "titel": ant.titel,
                        "reife_stufe": ant.reife_stufe,
                        "nachweis": ant.nachweis,
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
            methods=["EXAMINE", "INTERVIEW"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(NIS2Aggregator())
