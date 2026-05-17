"""Aggregator: AVV → DSGVO Art. 28, ISO-27001.A.5.20."""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class AVVAggregator(BaseAggregator):
    slug = "auftragsverarbeitung"
    norm_scopes = ("avv", "dsgvo", "iso_27001")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from auftragsverarbeitung.models import Auftragsverarbeiter
        except ImportError:
            return

        # AVV-Verträge sind langlebig — Filter nach created_at OR avv_abgeschlossen_am
        qs = Auftragsverarbeiter.objects.filter(
            created_at__date__lte=period_to,
        ).prefetch_related("schritte")
        records = []
        for avv in qs:
            record = EvidenceRecord(
                aggregator_slug=self.slug,
                record_id=f"Auftragsverarbeiter:{avv.pk}",
                titel=f"AVV: {avv.name}",
                beschreibung=(
                    f"Rechtssitz: {avv.rechtssitz_land}; "
                    f"Drittland: {avv.get_drittland_display()}; "
                    f"Status: {avv.get_status_display()}"
                ),
                erstellt_am=avv.created_at,
                verantwortlicher_email=None,
                status=avv.status,
                evidence_files=(),
                oscal_control_ids=(
                    "dsgvo-art-28",
                    "iso-27001-a.5.20",
                ),
                raw_data={
                    "name": avv.name,
                    "rechtssitz_land": avv.rechtssitz_land,
                    "drittland": avv.drittland,
                    "status": avv.status,
                    "avv_abgeschlossen_am": (
                        str(avv.avv_abgeschlossen_am)
                        if avv.avv_abgeschlossen_am
                        else None
                    ),
                    "avv_endet_am": (
                        str(avv.avv_endet_am) if avv.avv_endet_am else None
                    ),
                    "verarbeitungsschritte": [
                        {
                            "zweck": s.zweck,
                            "datenkategorien": list(s.datenkategorien or []),
                            "betroffene_kategorien": list(s.betroffene_kategorien or []),
                        }
                        for s in avv.schritte.all()
                    ],
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
            methods=["EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(AVVAggregator())
