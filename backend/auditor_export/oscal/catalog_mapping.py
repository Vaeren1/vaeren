"""Statische Mapping-Tabellen Vaeren-Modul → OSCAL-Control-IDs.

Wird in S7 durch echte YAML-Catalogs ersetzt; bis dahin liefern wir
minimal-Mappings, damit Tests + Schema-Konformität laufen.
"""

from __future__ import annotations


# Aggregator-Slug → Vaeren-Component-UUID (stabil)
COMPONENT_UUIDS: dict[str, str] = {
    "ki_inventar": "vaeren-comp-ki-inventar",
    "hinschg": "vaeren-comp-hinschg",
    "datenpannen": "vaeren-comp-datenpannen",
    "auftragsverarbeitung": "vaeren-comp-avv",
    "nis2": "vaeren-comp-nis2",
    "transparenzregister": "vaeren-comp-tr",
    "pflichtunterweisung": "vaeren-comp-pflichtunterweisung",
    "iso27001": "vaeren-comp-iso27001",
    "iso42001": "vaeren-comp-iso42001",
    "arbeitsschutz": "vaeren-comp-arbeitsschutz",
}

# NormScope → Catalog-Source-URI für OSCAL-control-implementation.source
NORM_TO_CATALOG_SOURCE: dict[str, str] = {
    "iso_27001": "urn:vaeren:catalog:iso-27001-annex-a-2022",
    "iso_42001": "urn:vaeren:catalog:iso-42001-2023",
    "nis2": "urn:vaeren:catalog:nis2-art-21-2024",
    "dsgvo": "urn:vaeren:catalog:dsgvo-2016",
    "ai_act": "urn:vaeren:catalog:ai-act-annex-iii-2024",
    "arbeitsschutz": "urn:vaeren:catalog:dguv-v1",
    "pflichtunterweisung": "urn:vaeren:catalog:dguv-v1",
    "hinschg": "urn:vaeren:catalog:hinschg-2023",
    "avv": "urn:vaeren:catalog:dsgvo-art-28",
    "datenpannen": "urn:vaeren:catalog:dsgvo-art-33",
    "transparenzregister": "urn:vaeren:catalog:gwg-2017",
}


# Norm-Coverage-Mapping: welche Aggregator-Records liefern Beleg für welche Controls?
# In S7 wird das durch Catalog-YAML-Files erweitert; das ist die Mindest-Mapping-Basis.
NORM_TO_AGGREGATORS: dict[str, list[str]] = {
    "iso_27001": [
        "hinschg",
        "datenpannen",
        "auftragsverarbeitung",
        "nis2",
        "pflichtunterweisung",
        "iso27001",
    ],
    "iso_42001": ["ki_inventar", "iso42001"],
    "nis2": ["nis2", "datenpannen"],
    "dsgvo": ["datenpannen", "auftragsverarbeitung"],
    "ai_act": ["ki_inventar"],
    "arbeitsschutz": ["pflichtunterweisung", "arbeitsschutz"],
    "pflichtunterweisung": ["pflichtunterweisung"],
    "hinschg": ["hinschg"],
    "avv": ["auftragsverarbeitung"],
    "datenpannen": ["datenpannen"],
    "transparenzregister": ["transparenzregister"],
}
