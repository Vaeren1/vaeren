"""Tests für Evidence-Modell + Immutability. Spec §5/§6."""

import datetime
import hashlib
import uuid

import pytest
from django.core.exceptions import ValidationError
from django_tenants.utils import schema_context

from tests.factories import TenantFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(
        schema_name=f"ev_{uuid.uuid4().hex[:12]}",
        firma_name="EV-Test",
    )


def test_evidence_basic_creation_computes_sha256(tenant):
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Schulungs-Zertifikat Anna",
            content=b"DUMMY-CERTIFICATE-CONTENT",
            mime_type="application/pdf",
        )
        expected = hashlib.sha256(b"DUMMY-CERTIFICATE-CONTENT").hexdigest()
        assert ev.sha256 == expected
        assert ev.groesse_bytes == len(b"DUMMY-CERTIFICATE-CONTENT")
        assert ev.immutable is True


def test_evidence_update_raises_validation_error(tenant):
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Original",
            content=b"X",
            mime_type="text/plain",
        )
        ev.titel = "Versuch zu ändern"
        with pytest.raises(ValidationError) as exc:
            ev.save()
        assert "immutable" in str(exc.value).lower()


def test_evidence_delete_is_blocked(tenant):
    """Soft-delete via deleted_at; physisches Delete ist verboten."""
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Test", content=b"X", mime_type="text/plain"
        )
        with pytest.raises(ValidationError) as exc:
            ev.delete()
        assert "immutable" in str(exc.value).lower()


def test_evidence_aufbewahrung_default(tenant):
    """Default-Aufbewahrung 10 Jahre nach created_at."""
    from core.models import Evidence

    with schema_context(tenant.schema_name):
        ev = Evidence.objects.create_with_content(
            titel="Test", content=b"X", mime_type="text/plain"
        )
        delta = ev.aufbewahrung_bis - ev.created_at.date()
        # >= 10 Jahre - 2 Tage (Schaltjahre + Datumsgrenze)
        assert delta >= datetime.timedelta(days=365 * 10 - 2)
