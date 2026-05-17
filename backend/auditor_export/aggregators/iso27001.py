"""Stub-Aggregator: ISO-27001-eigenständig.

Parallel-Slice (Phase-3-ISO-27001) baut Module wie `iso27001.ISMSControl`,
`iso27001.RisikoBewertung` etc. Sobald die existieren, wird dieser Aggregator
erweitert. Bis dahin: leerer Iterator — verhindert Merge-Schmerz.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class ISO27001Aggregator(BaseAggregator):
    slug = "iso27001"
    norm_scopes = ("iso_27001",)

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            # ruff: noqa: F401
            from iso27001.models import ISMSControl  # type: ignore[import-not-found]
        except ImportError:
            # Modul noch nicht deployed → leerer Stream
            return
            yield  # pragma: no cover — generator-Markierung

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
            ],
        )


REGISTRY.register(ISO27001Aggregator())
