"""Aggregator-Plugins. Import jeder Aggregator-Datei registriert ihn im REGISTRY."""

from .base import (
    AggregatorRegistry,
    BaseAggregator,
    EvidenceFileRef,
    EvidenceRecord,
    REGISTRY,
    VAEREN_NAMESPACE_UUID,
    stable_uuid_v5,
)

# Konkrete Aggregatoren registrieren sich beim Import.
from . import (  # noqa: F401, E402
    arbeitsschutz,
    auftragsverarbeitung,
    datenpannen,
    hinschg,
    iso27001,
    iso42001,
    ki_inventar,
    nis2,
    pflichtunterweisung,
    transparenzregister,
)

__all__ = [
    "AggregatorRegistry",
    "BaseAggregator",
    "EvidenceFileRef",
    "EvidenceRecord",
    "REGISTRY",
    "VAEREN_NAMESPACE_UUID",
    "stable_uuid_v5",
]
