"""OSCAL-Generator: aggregierte EvidenceRecords → OSCAL-JSON (SSP + AR).

Spec §6.2. Output bit-deterministisch dank UUID-v5 (Spec §6.4).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

from auditor_export.aggregators import REGISTRY, stable_uuid_v5

from .catalog_mapping import (
    COMPONENT_UUIDS,
    NORM_TO_AGGREGATORS,
    NORM_TO_CATALOG_SOURCE,
)
from .schemas import (
    OscalAssessmentResults,
    OscalComponent,
    OscalMetadata,
    OscalObservation,
    OscalResult,
    OscalSystemCharacteristics,
    OscalSystemImplementation,
    OscalSystemSecurityPlan,
)

if TYPE_CHECKING:
    from auditor_export.aggregators import EvidenceRecord
    from auditor_export.models import AuditExportRun


# Vaeren-Version (statisch — kann später aus pkg-info gezogen werden)
VAEREN_VERSION = "1.4.0"


class OSCALGenerator:
    """Erzeugt OSCAL-JSON-Dokumente aus aggregierten EvidenceRecords."""

    def __init__(
        self,
        *,
        run: AuditExportRun,
        tenant_schema: str,
        tenant_firma: str,
        records: list[EvidenceRecord],
    ) -> None:
        self.run = run
        self.tenant_schema = tenant_schema
        self.tenant_firma = tenant_firma
        self.records = records
        # Stabile Zeitstempel: nicht datetime.now(), sondern run.started_at
        # damit Snapshot-Tests reproduzierbar bleiben.
        self.generated_at = (
            run.started_at if run.started_at else datetime.datetime.now(datetime.UTC)
        )

    # ---------- Metadata -----------------------------------------------

    def _metadata(self, title: str) -> OscalMetadata:
        return OscalMetadata(
            title=title,
            published=self.generated_at.isoformat(),
            last_modified=self.generated_at.isoformat(),
            version=VAEREN_VERSION,
            oscal_version="1.1.2",
            props=[
                {"name": "vaeren-mappe-id", "value": self.run.mappe_id},
                {"name": "vaeren-tenant", "value": self.tenant_schema},
            ],
        )

    # ---------- System-Security-Plan (SSP) -----------------------------

    def _components(self) -> list[OscalComponent]:
        """Eine Component pro aktivem Aggregator-Slug (für die wir Records haben)."""
        seen = sorted({r.aggregator_slug for r in self.records})
        components = []
        for slug in seen:
            uuid = COMPONENT_UUIDS.get(slug, str(stable_uuid_v5(f"vaeren.component.{slug}")))
            components.append(
                OscalComponent(
                    uuid=str(stable_uuid_v5(uuid)),
                    type="software",
                    title=f"Vaeren-Modul: {slug}",
                    description=f"Compliance-Modul {slug} in Vaeren-Tenant {self.tenant_schema}",
                )
            )
        return components

    def generate_ssp(self) -> OscalSystemSecurityPlan:
        meta = self._metadata(title=f"Vaeren System Security Plan — {self.tenant_firma}")
        return OscalSystemSecurityPlan(
            uuid=str(stable_uuid_v5(f"vaeren.ssp.{self.tenant_schema}.{self.run.mappe_id}")),
            metadata=meta,
            system_characteristics=OscalSystemCharacteristics(
                system_ids=[{"id": self.tenant_schema, "identifier-type": "vaeren-tenant"}],
                system_name=f"Vaeren Compliance Platform — {self.tenant_firma}",
                description=(
                    "Multi-Tenant SaaS-Plattform für Compliance-Pflichten "
                    "(HinSchG, AVV, NIS2, AI-Act, DSGVO, Pflichtunterweisung)."
                ),
            ),
            system_implementation=OscalSystemImplementation(
                components=self._components(),
            ),
        )

    # ---------- Assessment-Results (AR) --------------------------------

    def _observations(self) -> list[OscalObservation]:
        """Für jeden Record das jeweilige Aggregator-Mapping rufen."""
        observations = []
        for record in self.records:
            agg = REGISTRY.get(record.aggregator_slug)
            if not agg:
                continue
            observations.append(agg.map_to_oscal(record))
        return observations

    def _result_per_norm(self, norm_scopes: list[str]) -> list[OscalResult]:
        """Eine Result-Section pro Norm-Scope."""
        results = []
        period_start = (
            datetime.datetime.combine(
                self.run.profile.zeitraum_von, datetime.time.min
            ).replace(tzinfo=datetime.UTC)
            if self.run and self.run.profile
            else self.generated_at
        )
        period_end = (
            datetime.datetime.combine(
                self.run.profile.zeitraum_bis, datetime.time.max
            ).replace(tzinfo=datetime.UTC)
            if self.run and self.run.profile
            else self.generated_at
        )

        all_obs = self._observations()
        for norm in sorted(norm_scopes):
            aggregator_slugs = NORM_TO_AGGREGATORS.get(norm, [])
            # Nur Observations, deren Aggregator zur Norm gehört:
            relevant_obs = [
                o
                for o in all_obs
                if any(
                    p.name == "vaeren-aggregator" and p.value in aggregator_slugs
                    for p in (o.props or [])
                )
            ]
            results.append(
                OscalResult(
                    uuid=str(stable_uuid_v5(f"vaeren.result.{self.run.mappe_id}.{norm}")),
                    title=f"Audit-Ergebnis: {norm}",
                    description=f"Aggregierte Audit-Belege für Norm-Scope {norm}",
                    start=period_start.isoformat(),
                    end=period_end.isoformat(),
                    observations=relevant_obs,
                )
            )
        return results

    def generate_assessment_results(self) -> OscalAssessmentResults:
        meta = self._metadata(title=f"Vaeren Assessment Results — {self.run.mappe_id}")
        norm_scopes = list(self.run.profile.norm_scope or []) if self.run.profile else []
        # OSCAL-1.1.2 verlangt für AssessmentResults ein import-ap (Assessment Plan).
        # Wir haben (noch) keinen vollwertigen AP; verwenden eine stabile Stub-URL,
        # damit NIST-Validatoren nicht meckern. Slug = primärer Norm-Scope (oder "default").
        primary_norm = norm_scopes[0] if norm_scopes else "default"
        return OscalAssessmentResults(
            uuid=str(stable_uuid_v5(f"vaeren.ar.{self.run.mappe_id}")),
            metadata=meta,
            import_ap={"href": f"https://vaeren.de/oscal/profiles/{primary_norm}"},
            results=self._result_per_norm(norm_scopes),
        )

    # ---------- JSON-Dumps ---------------------------------------------

    def ssp_to_json_dict(self) -> dict[str, Any]:
        return {
            "system-security-plan": self.generate_ssp().model_dump(
                by_alias=True, exclude_none=True
            )
        }

    def ar_to_json_dict(self) -> dict[str, Any]:
        return {
            "assessment-results": self.generate_assessment_results().model_dump(
                by_alias=True, exclude_none=True
            )
        }
