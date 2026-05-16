"""Tests für die internen Redaktions-Endpoints unter /api/redaktion/.

Konzeptionell tricky: Endpoints leben auf tenant-Domain, switchen aber
intern ins public-Schema für NewsPost-Queries. Tests müssen das simulieren.
"""

from __future__ import annotations

import pytest
from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework.test import APIClient

from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus, NewsSource
from tests.factories import TenantDomainFactory, TenantFactory, UserFactory


@pytest.fixture
def tenant(db):
    return TenantFactory(schema_name="test_internal")


@pytest.fixture
def tenant_domain(tenant):
    return TenantDomainFactory(tenant=tenant, domain="test-internal.app.vaeren.local")


@pytest.fixture
def superuser(tenant):
    """Superuser im Tenant-Schema (analog konrad@vaeren.de im demo)."""
    with schema_context(tenant.schema_name):
        return UserFactory(
            email="admin@test.example",
            is_superuser=True,
            is_staff=True,
            password="adminpass-12345",
        )


@pytest.fixture
def regular_user(tenant):
    with schema_context(tenant.schema_name):
        return UserFactory(
            email="user@test.example",
            is_superuser=False,
            is_staff=False,
            password="userpass-12345",
        )


@pytest.fixture
def public_newspost(db):
    """NewsPost im public-Schema (tenant-shared)."""
    with schema_context(get_public_schema_name()):
        src = NewsSource.objects.create(
            key="test-src",
            name="Test Source",
            base_url="https://example.com",
            parser_key="x",
        )
        cand = NewsCandidate.objects.create(
            source=src,
            quell_url="https://example.com/1",
            titel_raw="Test",
            excerpt_raw="",
        )
        post = NewsPost.objects.create(
            candidate=cand,
            slug="test-internal-slug",
            titel="Test Internal",
            lead="Lead",
            body_html="<p>Body</p>",
            kategorie="datenschutz",
            geo="EU",
            type="leitlinie",
            relevanz="hoch",
        )
        post.publish()
        return post


@pytest.mark.django_db
class TestRedaktionInternalAuth:
    """Authentifizierungs-Gate auf /api/redaktion/newsposts/."""

    def test_anonymous_gets_403(self, tenant_domain, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        resp = client.get("/api/redaktion/newsposts/")
        assert resp.status_code in (401, 403)

    def test_regular_user_gets_403(self, tenant_domain, regular_user, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(regular_user)
        resp = client.get("/api/redaktion/newsposts/")
        assert resp.status_code == 403

    def test_superuser_sees_posts(self, tenant_domain, superuser, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(superuser)
        resp = client.get("/api/redaktion/newsposts/")
        assert resp.status_code == 200
        data = resp.json()
        results = data["results"] if isinstance(data, dict) else data
        slugs = [p["slug"] for p in results]
        assert "test-internal-slug" in slugs


@pytest.mark.django_db
class TestRedaktionInternalActions:
    def test_unpublish_action(self, tenant_domain, superuser, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(superuser)
        assert public_newspost.status == NewsPostStatus.PUBLISHED

        resp = client.post(
            f"/api/redaktion/newsposts/{public_newspost.slug}/unpublish/"
        )
        assert resp.status_code == 200
        with schema_context(get_public_schema_name()):
            public_newspost.refresh_from_db()
        assert public_newspost.status == NewsPostStatus.UNPUBLISHED

    def test_publish_action(self, tenant_domain, superuser, public_newspost):
        # erst auf unpublished setzen
        with schema_context(get_public_schema_name()):
            public_newspost.unpublish()

        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(superuser)
        resp = client.post(
            f"/api/redaktion/newsposts/{public_newspost.slug}/publish/"
        )
        assert resp.status_code == 200
        with schema_context(get_public_schema_name()):
            public_newspost.refresh_from_db()
        assert public_newspost.status == NewsPostStatus.PUBLISHED

    def test_toggle_pin(self, tenant_domain, superuser, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(superuser)

        assert public_newspost.pinned is False
        resp = client.post(
            f"/api/redaktion/newsposts/{public_newspost.slug}/toggle_pin/"
        )
        assert resp.status_code == 200
        with schema_context(get_public_schema_name()):
            public_newspost.refresh_from_db()
        assert public_newspost.pinned is True

    def test_patch_titel_and_lead(self, tenant_domain, superuser, public_newspost):
        client = APIClient(HTTP_HOST=tenant_domain.domain)
        client.force_login(superuser)
        resp = client.patch(
            f"/api/redaktion/newsposts/{public_newspost.slug}/",
            data={"titel": "Bearbeiteter Titel", "lead": "Neuer Lead"},
            format="json",
        )
        assert resp.status_code == 200
        with schema_context(get_public_schema_name()):
            public_newspost.refresh_from_db()
        assert public_newspost.titel == "Bearbeiteter Titel"
        assert public_newspost.lead == "Neuer Lead"
