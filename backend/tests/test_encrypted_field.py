"""Tests für `core.fields.EncryptedTextField` + `Tenant.encryption_key`.

Multi-Tenant-Isolation ist HIER kritisch: Bytes von Tenant A dürfen mit
Key von Tenant B niemals entschlüsselbar sein. Cross-Tenant-Decrypt-Attacks
müssen `InvalidToken` raisen.
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from django.db import connection
from django_tenants.utils import schema_context

from core.fields import EncryptedFieldError, EncryptedTextField


@pytest.fixture
def two_tenants(db):
    from tests.factories import TenantFactory

    a = TenantFactory(schema_name="enc_a", firma_name="Enc A GmbH")
    b = TenantFactory(schema_name="enc_b", firma_name="Enc B GmbH")
    yield a, b


def test_tenant_auto_generates_unique_encryption_key(two_tenants):
    a, b = two_tenants
    assert a.encryption_key
    assert b.encryption_key
    assert bytes(a.encryption_key) != bytes(b.encryption_key)
    # Schlüssel ist ein gültiger Fernet-Key (32 url-safe Base64-encoded Bytes)
    Fernet(bytes(a.encryption_key))
    Fernet(bytes(b.encryption_key))


def test_tenant_keeps_existing_key_on_resave(two_tenants):
    a, _b = two_tenants
    original = bytes(a.encryption_key)
    a.firma_name = "Renamed AG"
    a.save()
    a.refresh_from_db()
    assert bytes(a.encryption_key) == original


def test_get_prep_value_without_tenant_raises(db):
    field = EncryptedTextField()
    # connection.tenant kann None sein wenn kein schema_context aktiv
    # In Tests setzt django-tenants standardmäßig public-tenant → wir simulieren
    # explizit None via patch.
    if hasattr(connection, "tenant"):
        original = connection.tenant
    else:
        original = "<unset>"
    try:
        connection.tenant = None  # type: ignore[attr-defined]
        with pytest.raises(EncryptedFieldError):
            field.get_prep_value("hallo")
    finally:
        if original == "<unset>":
            del connection.tenant
        else:
            connection.tenant = original  # type: ignore[attr-defined]


def test_roundtrip_within_same_tenant(two_tenants):
    a, _b = two_tenants
    field = EncryptedTextField()

    with schema_context(a.schema_name):
        ciphertext = field.get_prep_value("Whistleblower-Inhalt: streng geheim")
        assert isinstance(ciphertext, bytes)
        plaintext = field.from_db_value(ciphertext, None, None)
        assert plaintext == "Whistleblower-Inhalt: streng geheim"


def test_cross_tenant_decryption_fails(two_tenants):
    """Spec §10 + Sprint-5-Plan §5: Bytes von Tenant A mit Key B → InvalidToken."""
    a, b = two_tenants
    field = EncryptedTextField()

    # In Tenant A verschlüsseln
    with schema_context(a.schema_name):
        ciphertext = field.get_prep_value("Tenant-A-Geheimnis")

    # In Tenant B versuchen zu entschlüsseln
    with schema_context(b.schema_name):
        with pytest.raises(EncryptedFieldError):
            field.from_db_value(ciphertext, None, None)


def test_empty_string_roundtrip(two_tenants):
    a, _b = two_tenants
    field = EncryptedTextField()
    with schema_context(a.schema_name):
        prepped = field.get_prep_value("")
        assert prepped == b""
        assert field.from_db_value(b"", None, None) == ""


def test_none_roundtrip(two_tenants):
    a, _b = two_tenants
    field = EncryptedTextField()
    with schema_context(a.schema_name):
        assert field.get_prep_value(None) is None
        assert field.from_db_value(None, None, None) is None


def test_each_encrypt_gives_different_ciphertext(two_tenants):
    """Fernet hat random IV → gleicher Klartext = unterschiedlicher Ciphertext.

    Schützt gegen Frequenz-/Pattern-Analyse.
    """
    a, _b = two_tenants
    field = EncryptedTextField()
    with schema_context(a.schema_name):
        c1 = field.get_prep_value("identical text")
        c2 = field.get_prep_value("identical text")
        assert c1 != c2
        assert field.from_db_value(c1, None, None) == "identical text"
        assert field.from_db_value(c2, None, None) == "identical text"
