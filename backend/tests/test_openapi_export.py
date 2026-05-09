"""Smoke-Test: OpenAPI-Schema-Generierung produziert valides JSON ohne Errors.

Schicht 2 (Spec §10): wenn das Schema bricht, scheitert dieser Test in CI
und der Frontend-Type-Sync rückt ins Blickfeld.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "backend" / "scripts" / "export-openapi.sh"


@pytest.mark.django_db
def test_export_openapi_script_produces_valid_json(tmp_path):
    """Script läuft erfolgreich und schreibt valides JSON-Schema."""
    assert SCRIPT.exists(), f"Script fehlt: {SCRIPT}"
    out = tmp_path / "openapi.json"
    result = subprocess.run(
        ["uv", "run", "python", "manage.py", "spectacular", "--file", str(out), "--format",
         "openapi-json", "--validate"],
        cwd=REPO_ROOT / "backend",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"spectacular failed: {result.stderr}"
    schema = json.loads(out.read_text())
    assert schema["openapi"].startswith("3.")
    assert "paths" in schema
    # Sanity: ein paar wichtige Endpoints müssen drin sein
    expected_paths = ["/api/mitarbeiter/", "/api/auth/csrf/", "/api/auth/mfa/totp/setup/"]
    for path in expected_paths:
        assert path in schema["paths"], f"Endpoint fehlt im Schema: {path}"
