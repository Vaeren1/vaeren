"""Mapping-Tests: ≥30 Einträge gesamt, alle 6 Module abgedeckt."""

from __future__ import annotations

from iso27001 import mapping


def test_mapping_total_count_at_least_30():
    """Akzeptanzkriterium 4: mind. 30 Mappings."""
    assert mapping.total_mapping_count() >= 30


def test_all_six_modules_have_mappings():
    """Alle 6 Quell-Module liefern mindestens einen Control-Code."""
    expected_modules = {
        "ki_inventar",
        "nis2",
        "avv",
        "datenpannen",
        "hinschg",
        "pflichtunterweisung",
    }
    assert expected_modules.issubset(set(mapping.MODULE_TO_CONTROLS.keys()))
    for mod in expected_modules:
        assert len(mapping.MODULE_TO_CONTROLS[mod]) >= 1, f"{mod} hat 0 Mappings"


def test_all_mapped_codes_are_valid_annex_a_format():
    """Alle Mapping-Codes folgen dem Annex-A-Format A.5.x / A.6.x / A.7.x / A.8.x."""
    valid_prefixes = ("A.5.", "A.6.", "A.7.", "A.8.")
    for mod, codes in mapping.MODULE_TO_CONTROLS.items():
        for code in codes:
            assert code.startswith(valid_prefixes), f"{mod}: ungültiger Code {code}"
