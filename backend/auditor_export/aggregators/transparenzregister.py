"""Aggregator: Transparenzregister → GwG §3."""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class TransparenzregisterAggregator(BaseAggregator):
    slug = "transparenzregister"
    norm_scopes = ("transparenzregister",)

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from transparenzregister.models import (
                Unternehmensstammblatt,
                WirtschaftlichBerechtigter,
            )
        except ImportError:
            return

        records = []
        stammblatt = Unternehmensstammblatt.objects.first()
        if stammblatt:
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Unternehmensstammblatt:{stammblatt.pk}",
                    titel=f"Stammblatt: {stammblatt.firma_name}",
                    beschreibung=(
                        f"Rechtsform: {stammblatt.get_rechtsform_display()}; "
                        f"HRB: {stammblatt.handelsregister_nummer}; "
                        f"GwG: {stammblatt.get_gwg_pflicht_display()}"
                    ),
                    erstellt_am=stammblatt.created_at,
                    status=stammblatt.gwg_pflicht,
                    oscal_control_ids=("gwg-§3",),
                    raw_data={
                        "firma_name": stammblatt.firma_name,
                        "rechtsform": stammblatt.rechtsform,
                        "handelsregister_nummer": stammblatt.handelsregister_nummer,
                        "transparenzregister_id": stammblatt.transparenzregister_id,
                        "gwg_pflicht": stammblatt.gwg_pflicht,
                    },
                )
            )

            for wb in stammblatt.berechtigte.all():
                records.append(
                    EvidenceRecord(
                        aggregator_slug=self.slug,
                        record_id=f"WirtschaftlichBerechtigter:{wb.pk}",
                        titel=f"Wirtschaftlich Berechtigter: {wb}",
                        beschreibung=wb.art_des_interesses or "",
                        erstellt_am=wb.created_at,
                        status="aktiv",
                        oscal_control_ids=("gwg-§3",),
                        raw_data={
                            "vorname": wb.vorname,
                            "nachname": wb.nachname,
                            "anteil_prozent": (
                                float(wb.anteil_prozent) if wb.anteil_prozent else None
                            ),
                            "wohnort_land": wb.wohnort_land,
                            "meldung_an_transparenzregister_am": (
                                str(wb.meldung_an_transparenzregister_am)
                                if wb.meldung_an_transparenzregister_am
                                else None
                            ),
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
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(TransparenzregisterAggregator())
