"""Aggregator-Framework — Spec §5.

Modul-agnostische DTOs + BaseAggregator-ABC + RDG-Filter-Pflicht.
"""

from __future__ import annotations

import abc
import dataclasses
import datetime
import uuid
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from auditor_export.oscal.schemas import OscalObservation


# UUID-v5-Namespace für Vaeren-OSCAL-Objekte (fixiert, niemals ändern).
VAEREN_NAMESPACE_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")


def stable_uuid_v5(name: str) -> uuid.UUID:
    """Erzeugt deterministische UUID-v5 aus String. Voraussetzung für
    Snapshot-Tests + Bit-Reproducibility der OSCAL-Outputs."""
    return uuid.uuid5(VAEREN_NAMESPACE_UUID, name)


@dataclasses.dataclass(frozen=True)
class EvidenceFileRef:
    """Referenz auf eine konkrete Beleg-Datei (Original-Upload, Zertifikat-PDF, ...)."""

    filename: str
    sha256: str
    mime_type: str
    size_bytes: int
    absolute_path: str | None = None  # None wenn nur DB-Reference (kein File)
    encrypted: bool = False  # True für HinSchG-Bodies (Fernet)
    inline_bytes: bytes | None = None  # Optional: Bytes direkt im RAM


@dataclasses.dataclass(frozen=True)
class EvidenceRecord:
    """DTO: Modul-agnostische Repräsentation eines Audit-Beleg-Eintrags.

    Spec §5.1. Jeder Aggregator yieldet diese Records.
    """

    aggregator_slug: str
    record_id: str  # eindeutig im Aggregator, z. B. "KITool:42"
    titel: str
    beschreibung: str
    erstellt_am: datetime.datetime
    verantwortlicher_email: str | None = None
    status: str = ""
    evidence_files: tuple[EvidenceFileRef, ...] = ()
    oscal_control_ids: tuple[str, ...] = ()
    raw_data: dict[str, Any] = dataclasses.field(default_factory=dict)


class BaseAggregator(abc.ABC):
    """ABC für Modul-Aggregatoren. Spec §5.1.

    Jede Implementierung MUSS:
    - `collect()` implementieren — yieldet EvidenceRecords im Zeitraum
    - `map_to_oscal()` implementieren — mapped Record auf OSCAL-Observation
    - `filter_rdg_safe()` standardgemäß (oder verfeinert) Draft-Records ausfiltern

    RDG-Pflicht (CLAUDE.md §Architektur-Regeln-1):
    Records mit nicht-bestätigten LLM-Outputs DÜRFEN NICHT in den Export.
    """

    slug: str = ""  # z. B. "ki_inventar"
    norm_scopes: tuple[str, ...] = ()  # NormScope-Strings für die dieser Aggregator liefert

    @abc.abstractmethod
    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        """Yieldet EvidenceRecords für den Zeitraum.

        Implementierung MUSS via `filter_rdg_safe()` Draft/LLM-only-Records ausfiltern!
        """

    @abc.abstractmethod
    def map_to_oscal(self, record: EvidenceRecord) -> OscalObservation:  # type: ignore[name-defined]
        """Mappt einen EvidenceRecord auf eine OSCAL-Observation."""

    def filter_rdg_safe(self, record: EvidenceRecord) -> bool:
        """RDG-Schutz: True wenn Record human-bestätigt, False bei LLM-only-Draft.

        Default-Impl: blockt jeden Record, dessen raw_data `llm_draft=True` hat
        ODER dessen `status='draft'` ist. Sub-Klassen können verfeinern.
        """
        if record.raw_data.get("llm_draft", False):
            return False
        if record.status in {"draft", "entwurf", "vorschlag"}:
            return False
        return True

    def filter_records(self, records: Iterable[EvidenceRecord]) -> Iterator[EvidenceRecord]:
        """Wrapper: yieldet nur RDG-konforme Records."""
        for r in records:
            if self.filter_rdg_safe(r):
                yield r


class AggregatorRegistry:
    """Plugin-Registry analog `panels/_base.py` aus paywise-dashboard."""

    def __init__(self) -> None:
        self._aggregators: dict[str, BaseAggregator] = {}

    def register(self, aggregator: BaseAggregator) -> None:
        if not aggregator.slug:
            raise ValueError(f"Aggregator {aggregator!r} hat keinen slug")
        self._aggregators[aggregator.slug] = aggregator

    def get(self, slug: str) -> BaseAggregator | None:
        return self._aggregators.get(slug)

    def all(self) -> list[BaseAggregator]:
        return list(self._aggregators.values())

    def for_norm_scopes(self, norm_scopes: list[str]) -> list[BaseAggregator]:
        """Liefert Aggregatoren, deren `norm_scopes` mit der Auswahl überlappen."""
        scope_set = set(norm_scopes)
        return [a for a in self._aggregators.values() if set(a.norm_scopes) & scope_set]


# Singleton-Registry — wird in aggregators/__init__.py befüllt.
REGISTRY = AggregatorRegistry()
