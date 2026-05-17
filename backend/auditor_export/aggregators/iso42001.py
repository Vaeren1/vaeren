"""Stub-Aggregator: ISO-42001-eigenständig (für KI-Managementsystem)."""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class ISO42001Aggregator(BaseAggregator):
    slug = "iso42001"
    norm_scopes = ("iso_42001",)

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from iso42001.models import AIMSControl  # type: ignore[import-not-found]
        except ImportError:
            return
            yield  # pragma: no cover

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=record.titel,
            description=record.beschreibung,
            methods=["EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[],
        )


REGISTRY.register(ISO42001Aggregator())
