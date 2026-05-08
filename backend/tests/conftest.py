"""Globale pytest-Fixtures. Erweitert in Task 5 mit Tenant-Fixtures."""
import pytest


@pytest.fixture(autouse=True)
def _silence_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sicherheitsnetz: blockiert versehentliche echte Outbound-HTTP-Calls.

    Tests müssen `responses` oder explizites Mocking nutzen. Wenn sie
    Network-Activity wollen, ist das ein Designfehler.
    """
    monkeypatch.setenv("PYTHONWARNINGS", "error::ResourceWarning")
