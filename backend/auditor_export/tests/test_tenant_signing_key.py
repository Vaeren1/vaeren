"""Tests: Tenant.audit_signing_key wird auto-generiert + idempotent."""

from __future__ import annotations

import secrets

import pytest
from django.db import connection

from tests.factories import TenantFactory


def _unique_schema(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(3)}"


def test_audit_signing_key_auto_generated_on_save(db):
    """Phase-3-Migration-Safety: jeder neue Tenant bekommt einen Key."""
    connection.set_schema_to_public()
    t = TenantFactory(schema_name=_unique_schema("signa"), firma_name="A")
    assert t.audit_signing_key, "audit_signing_key wurde nicht generiert"
    assert len(bytes(t.audit_signing_key)) == 32, "HMAC-Key muss 32 Bytes lang sein"


def test_audit_signing_key_separate_from_encryption_key(db):
    """Krypto-Hygiene: zwei verschiedene Keys."""
    connection.set_schema_to_public()
    t = TenantFactory(schema_name=_unique_schema("signb"), firma_name="B")
    assert bytes(t.audit_signing_key) != bytes(t.encryption_key)


def test_audit_signing_key_persistent_across_saves(db):
    """Bestehende Tenants behalten ihren Key (Rotation darf NICHT versehentlich passieren)."""
    connection.set_schema_to_public()
    t = TenantFactory(schema_name=_unique_schema("signc"), firma_name="C")
    key_initial = bytes(t.audit_signing_key)
    t.firma_name = "C-renamed"
    t.save()
    t.refresh_from_db()
    assert bytes(t.audit_signing_key) == key_initial
