"""Eigene pydantic-Models für OSCAL-1.1.2-Subset.

Spec §6.1 Entscheidung 1: KEIN oscal-pydantic-Dependency, sondern eigene Models —
~200 Zeilen, kontrolliert von Vaeren. Wir validieren generierte JSON-Files
gegen die offiziellen NIST-JSON-Schemas in den Tests.

Wir nutzen pydantic-2 mit camelCase-Aliases, weil OSCAL-Spec snake_case + camelCase
mischt — Json-Output respektiert das. populate_by_name=True erlaubt beides beim
Konstruieren.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# OSCAL nutzt fast nur Hyphenation für Top-Level-Field-Namen, daher
# benutzen wir BaseModel mit alias_generator zur Konvertierung.
def _to_oscal_alias(name: str) -> str:
    """snake_case → kebab-case Konvertierung für OSCAL-Field-Namen."""
    return name.replace("_", "-")


class OscalBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_oscal_alias,
        populate_by_name=True,
        extra="allow",
    )


class OscalProp(OscalBase):
    """Generische Property nach OSCAL-Spec."""

    name: str
    value: str
    ns: str | None = None
    class_: str | None = Field(default=None, alias="class")


class OscalLink(OscalBase):
    href: str
    rel: str | None = None
    text: str | None = None


class OscalRole(OscalBase):
    id: str
    title: str
    short_name: str | None = None
    description: str | None = None


class OscalMetadata(OscalBase):
    title: str
    published: str | None = None
    last_modified: str
    version: str
    oscal_version: str = "1.1.2"
    roles: list[OscalRole] = Field(default_factory=list)
    props: list[OscalProp] = Field(default_factory=list)
    remarks: str | None = None


class OscalSubject(OscalBase):
    """Subject einer Observation (z. B. Component, System, User)."""

    subject_uuid: str
    type: str  # "component" | "system-id" | "user" | "party" | "resource"
    title: str | None = None
    description: str | None = None
    props: list[OscalProp] = Field(default_factory=list)


class OscalEvidence(OscalBase):
    """Beleg-Referenz innerhalb einer Observation."""

    href: str
    description: str | None = None
    props: list[OscalProp] = Field(default_factory=list)


class OscalObservation(OscalBase):
    """Ein konkreter Audit-Befund (Spec §6.3)."""

    uuid: str
    title: str | None = None
    description: str
    methods: list[str] = Field(default_factory=list)  # EXAMINE, INTERVIEW, TEST
    types: list[str] = Field(default_factory=list)  # finding, evidence, ...
    subjects: list[OscalSubject] = Field(default_factory=list)
    relevant_evidence: list[OscalEvidence] = Field(default_factory=list)
    collected: str
    expires: str | None = None
    props: list[OscalProp] = Field(default_factory=list)


class OscalFinding(OscalBase):
    """Findings = bewertete Observationen (Mängel/Lücken/Compliance-Status)."""

    uuid: str
    title: str
    description: str
    target: dict[str, Any] = Field(default_factory=dict)
    related_observations: list[dict[str, str]] = Field(default_factory=list)
    props: list[OscalProp] = Field(default_factory=list)


class OscalControlImplementation(OscalBase):
    """Implementierung eines spezifischen Norm-Controls durch eine Component."""

    uuid: str
    source: str  # Catalog-Slug oder URN
    description: str
    implemented_requirements: list[dict[str, Any]] = Field(default_factory=list)


class OscalComponent(OscalBase):
    """Vaeren-Komponente (= ein Modul) als System-Implementierung."""

    uuid: str
    type: str = "software"
    title: str
    description: str
    purpose: str | None = None
    props: list[OscalProp] = Field(default_factory=list)
    status: dict[str, str] = Field(default_factory=lambda: {"state": "operational"})


class OscalResult(OscalBase):
    """Pro Norm-Catalog ein Result mit Observations + Findings."""

    uuid: str
    title: str
    description: str
    start: str
    end: str | None = None
    local_definitions: dict[str, Any] = Field(default_factory=dict)
    observations: list[OscalObservation] = Field(default_factory=list)
    findings: list[OscalFinding] = Field(default_factory=list)


class OscalSystemCharacteristics(OscalBase):
    system_ids: list[dict[str, str]] = Field(default_factory=list)
    system_name: str
    description: str
    security_sensitivity_level: str = "moderate"
    system_information: dict[str, Any] = Field(default_factory=dict)
    security_impact_level: dict[str, str] = Field(
        default_factory=lambda: {
            "security-objective-confidentiality": "moderate",
            "security-objective-integrity": "moderate",
            "security-objective-availability": "moderate",
        }
    )
    status: dict[str, str] = Field(default_factory=lambda: {"state": "operational"})


class OscalSystemImplementation(OscalBase):
    users: list[dict[str, Any]] = Field(default_factory=list)
    components: list[OscalComponent] = Field(default_factory=list)


class OscalSystemSecurityPlan(OscalBase):
    """OSCAL System-Security-Plan (SSP) — beschreibt unser System (=Tenant)."""

    uuid: str
    metadata: OscalMetadata
    import_profile: dict[str, str] = Field(default_factory=dict)
    system_characteristics: OscalSystemCharacteristics
    system_implementation: OscalSystemImplementation
    control_implementation: dict[str, Any] = Field(default_factory=dict)


class OscalAssessmentResults(OscalBase):
    """OSCAL Assessment-Results — beschreibt einen Audit-Lauf."""

    uuid: str
    metadata: OscalMetadata
    import_ap: dict[str, str] = Field(default_factory=dict)
    results: list[OscalResult] = Field(default_factory=list)


# Convenience-Wrapper-Document
class OscalDocument(OscalBase):
    """Root-Container für entweder SSP oder AR."""

    system_security_plan: OscalSystemSecurityPlan | None = None
    assessment_results: OscalAssessmentResults | None = None
