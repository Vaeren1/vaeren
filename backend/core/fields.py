"""Custom Django Model-Fields. Sprint 5: Encryption für HinSchG-Inhalte.

`EncryptedTextField` verschlüsselt Klartext mit Fernet (AES-128-CBC + HMAC-SHA256).
Schlüssel kommt aus dem aktuell aktiven Tenant (`connection.tenant.encryption_key`),
gesetzt durch `django_tenants.middleware.TenantMainMiddleware` oder
`schema_context()`-Manager.

Nicht-Ziele:
- Volltextsuche, Sortierung, Indizes über verschlüsselten Inhalt (technisch unmöglich
  bei AEAD ohne deterministisches IV — bewusst nicht-deterministisch hier).
- Key-Rotation (Phase 2).

Multi-Tenant-Garantie: Bytes von Tenant A können mit Key von Tenant B nicht
entschlüsselt werden — Fernet wirft `InvalidToken`. Test in `tests/test_encrypted_field.py`.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken
from django.db import connection, models


class EncryptedFieldError(RuntimeError):
    """Erhoben, wenn Encryption ohne aktiven Tenant versucht wird."""


def _get_fernet() -> Fernet:
    """Liefert Fernet-Instanz für den aktuell aktiven Tenant.

    `django-tenants` setzt `connection.tenant` per Middleware (`tenant_context`/
    `set_tenant`) oder `schema_context` (mit `FakeTenant` ohne Felder). Bei
    `FakeTenant` wird der echte Tenant per Schema-Name aus dem Public-Schema
    nachgeladen, damit `encryption_key` verfügbar ist.

    Public-Schema (`schema_name == public`) hat keine Encryption — Aufruf wirft
    `EncryptedFieldError`.
    """
    tenant = getattr(connection, "tenant", None)
    if tenant is None:
        raise EncryptedFieldError(
            "EncryptedTextField braucht aktiven Tenant. "
            "Aufruf nur innerhalb von tenant_context()/schema_context() "
            "oder hinter TenantMainMiddleware."
        )
    key = getattr(tenant, "encryption_key", b"") or b""
    if isinstance(key, memoryview):
        key = bytes(key)
    if not key:
        # FakeTenant aus schema_context() — echten Tenant aus Public laden.
        from django_tenants.utils import get_public_schema_name

        from tenants.models import Tenant

        schema_name = getattr(tenant, "schema_name", None)
        if not schema_name or schema_name == get_public_schema_name():
            raise EncryptedFieldError("EncryptedTextField nicht im public-Schema verfügbar.")
        try:
            real = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist as exc:
            raise EncryptedFieldError(
                f"Tenant {schema_name!r} nicht im Public-Schema gefunden."
            ) from exc
        key = bytes(real.encryption_key) if real.encryption_key else b""
        if not key:
            raise EncryptedFieldError(f"Tenant {schema_name!r} hat keinen encryption_key gesetzt.")
    return Fernet(key)


class EncryptedTextField(models.TextField):
    """TextField mit transparenter Fernet-Encryption.

    DB-Repräsentation: bytes (Postgres `bytea`). Python: `str`.
    Read: bytes → decrypt → str. Write: str → encrypt → bytes.
    """

    description = "Fernet-encrypted Text (per-Tenant-Key)"

    def get_internal_type(self) -> str:
        return "BinaryField"

    def from_db_value(self, value, expression, connection_):
        if value is None:
            return None
        if isinstance(value, memoryview):
            value = bytes(value)
        if not value:
            return ""
        try:
            return _get_fernet().decrypt(value).decode("utf-8")
        except InvalidToken as exc:
            raise EncryptedFieldError(
                "Decryption failed — Tenant-Schlüssel passt nicht zum Ciphertext "
                "(potentieller Cross-Tenant-Leak oder Key-Rotation ohne Migration)."
            ) from exc

    def to_python(self, value):
        # to_python wird nur in Form-Validation und Manuel-Loads genutzt; from_db_value
        # macht das bei DB-Reads. Hier akzeptieren wir str unverändert.
        if value is None or isinstance(value, str):
            return value
        if isinstance(value, memoryview):
            value = bytes(value)
        if isinstance(value, bytes):
            if not value:
                return ""
            try:
                return _get_fernet().decrypt(value).decode("utf-8")
            except InvalidToken as exc:
                raise EncryptedFieldError("Decryption failed.") from exc
        return value

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, bytes):
            # Bereits encrypted (z. B. raw-DB-Aufruf) — durchreichen.
            return value
        if not isinstance(value, str):
            value = str(value)
        if value == "":
            return b""
        return _get_fernet().encrypt(value.encode("utf-8"))
