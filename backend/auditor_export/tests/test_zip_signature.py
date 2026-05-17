"""Tests: ZIP-Manifest + HMAC-Signatur + Roundtrip-Verify."""

from __future__ import annotations

import datetime
import secrets

from auditor_export.zipbundle.builder import (
    ZipFileEntry,
    _canonical_json,
    sign_manifest,
    verify_signature,
)


def _example_manifest() -> dict:
    return {
        "mappe_id": "VAE-2026-0517-AAAA",
        "generated_at": "2026-05-17T18:00:00+00:00",
        "tenant": "demo",
        "tenant_firma": "Demo GmbH",
        "vaeren_version": "1.4.0",
        "profile": {"name": "Test", "norm_scope": ["iso_27001"]},
        "files": [{"path": "a.pdf", "sha256": "ff" * 32, "size": 100}],
        "audit_log_chain_head": "00" * 32,
        "evidence_count": 0,
    }


def test_canonical_json_is_deterministic():
    a = _canonical_json({"b": 1, "a": 2})
    b = _canonical_json({"a": 2, "b": 1})
    assert a == b  # sorted-keys


def test_sign_and_verify_roundtrip():
    key = secrets.token_bytes(32)
    manifest = _example_manifest()
    signed = sign_manifest(manifest, key)
    assert "signature" in signed
    assert signed["signature"]["algorithm"] == "HMAC-SHA256"
    assert len(signed["signature"]["value"]) == 64  # SHA-256 hex
    assert verify_signature(signed, key) is True


def test_verify_rejects_tampered_files():
    key = secrets.token_bytes(32)
    manifest = _example_manifest()
    signed = sign_manifest(manifest, key)
    # File-Entry manipulieren
    signed["files"][0]["sha256"] = "00" * 32
    assert verify_signature(signed, key) is False


def test_verify_rejects_wrong_key():
    key = secrets.token_bytes(32)
    signed = sign_manifest(_example_manifest(), key)
    wrong_key = secrets.token_bytes(32)
    assert verify_signature(signed, wrong_key) is False


def test_verify_rejects_unknown_algorithm():
    key = secrets.token_bytes(32)
    signed = sign_manifest(_example_manifest(), key)
    signed["signature"]["algorithm"] = "RSA-PSS"
    assert verify_signature(signed, key) is False
