"""Audit + Findings + Maßnahmen-Lifecycle."""

from __future__ import annotations

import datetime

import pytest
from django.test import Client
from django_tenants.utils import schema_context

from core.models import TenantRole, User
from iso27001.models import (
    AuditFinding,
    FindingSchweregrad,
    InternesAudit,
    InternesAuditStatus,
    IsoTask,
)


@pytest.fixture
def authed_client(tenant_iso, settings):
    settings.ALLOWED_HOSTS = ["*"]
    with schema_context(tenant_iso.schema_name):
        u, _ = User.objects.get_or_create(
            email="cb@iso-a.de",
            defaults={
                "tenant_role": TenantRole.COMPLIANCE_BEAUFTRAGTER,
                "is_active": True,
            },
        )
        u.set_password("iso-a-1234!")
        u.save()
        client = Client(HTTP_HOST="iso-test.app.vaeren.local", enforce_csrf_checks=False)
        assert client.login(email="cb@iso-a.de", password="iso-a-1234!")
    return client


def test_audit_create_triggers_iso_task(tenant_iso, authed_client):
    today = datetime.date.today()
    resp = authed_client.post(
        "/api/iso27001/audits/",
        data={
            "titel": "Audit Q4",
            "auditzeitraum_von": (today + datetime.timedelta(days=30)).isoformat(),
            "auditzeitraum_bis": (today + datetime.timedelta(days=45)).isoformat(),
            "auditor": "Externe Auditorin",
            "status": "geplant",
        },
        content_type="application/json",
    )
    assert resp.status_code == 201
    audit_id = resp.json()["id"]
    with schema_context(tenant_iso.schema_name):
        # Auto-Task wurde via Signal angelegt
        assert IsoTask.objects.filter(audit_id=audit_id).exists()


def test_finding_gross_triggers_massnahme_task(tenant_iso, authed_client):
    today = datetime.date.today()
    with schema_context(tenant_iso.schema_name):
        audit = InternesAudit.objects.create(
            titel="Audit",
            auditzeitraum_von=today,
            auditzeitraum_bis=today + datetime.timedelta(days=7),
            auditor="X",
            status=InternesAuditStatus.LAUFEND,
        )

    resp = authed_client.post(
        "/api/iso27001/findings/",
        data={
            "audit": audit.id,
            "schweregrad": FindingSchweregrad.GROSS,
            "beschreibung": "Backup nicht getestet",
            "massnahme": "Test einplanen",
            "geplant_bis": (today + datetime.timedelta(days=30)).isoformat(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 201
    finding_id = resp.json()["id"]
    with schema_context(tenant_iso.schema_name):
        # Auto-Task via Signal
        assert IsoTask.objects.filter(finding_id=finding_id).exists()
