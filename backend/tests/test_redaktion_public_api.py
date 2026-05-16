"""Tests für /api/public/news/ und /api/public/korrekturen/."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from redaktion.models import Korrektur, NewsCandidate, NewsPost, NewsSource


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def source(db):
    return NewsSource.objects.create(
        key="bfdi",
        name="BfDI",
        base_url="https://bfdi.bund.de",
        parser_key="x",
    )


@pytest.fixture
def candidate(source):
    return NewsCandidate.objects.create(
        source=source,
        quell_url="https://bfdi.bund.de/foo",
        titel_raw="X",
        excerpt_raw="",
    )


@pytest.fixture
def published_post(candidate):
    p = NewsPost.objects.create(
        candidate=candidate,
        slug="test-post",
        titel="Test",
        lead="Lead",
        body_html="<p>Body</p>",
        kategorie="datenschutz",
        geo="DE",
        type="leitlinie",
        relevanz="hoch",
        source_links=[{"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}],
    )
    p.publish()
    return p


@pytest.mark.django_db
class TestNewsPostPublicSerializer:
    def test_serializer_omits_internal_fields(self, published_post):
        from redaktion.serializers import NewsPostPublicSerializer

        data = NewsPostPublicSerializer(published_post).data
        # Public-Felder
        assert data["slug"] == "test-post"
        assert data["titel"] == "Test"
        assert data["lead"] == "Lead"
        assert data["body_html"] == "<p>Body</p>"
        assert data["kategorie"] == "datenschutz"
        assert data["source_links"] == [
            {"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}
        ]
        # Interne Felder NICHT da
        assert "unpublish_token" not in data
        assert "verifier_confidence" not in data
        assert "verifier_issues" not in data
        assert "candidate" not in data


@pytest.mark.django_db
class TestNewsListEndpoint:
    def test_list_returns_only_published_visible_posts(
        self, api_client, source, candidate, published_post
    ):
        cand2 = NewsCandidate.objects.create(
            source=source,
            quell_url="https://x.example/2",
            titel_raw="Y",
            excerpt_raw="",
        )
        NewsPost.objects.create(
            candidate=cand2,
            slug="hidden",
            titel="Hidden",
            lead="L",
            body_html="",
            kategorie="datenschutz",
            geo="DE",
            type="leitlinie",
            relevanz="hoch",
        )

        resp = api_client.get("/api/public/news/")
        assert resp.status_code == 200
        slugs = [item["slug"] for item in resp.json()["results"]]
        assert "test-post" in slugs
        assert "hidden" not in slugs

    def test_list_filter_by_kategorie(self, api_client, source, published_post):
        cand2 = NewsCandidate.objects.create(
            source=source,
            quell_url="https://x.example/3",
            titel_raw="X",
            excerpt_raw="",
        )
        p2 = NewsPost.objects.create(
            candidate=cand2,
            slug="ai-post",
            titel="AI",
            lead="L",
            body_html="",
            kategorie="ai_act",
            geo="EU",
            type="gesetzgebung",
            relevanz="hoch",
        )
        p2.publish()

        resp = api_client.get("/api/public/news/?kategorie=ai_act")
        slugs = [item["slug"] for item in resp.json()["results"]]
        assert slugs == ["ai-post"]

    def test_list_filter_by_geo(self, api_client, source, published_post):
        cand2 = NewsCandidate.objects.create(
            source=source,
            quell_url="https://x.example/4",
            titel_raw="X",
            excerpt_raw="",
        )
        p2 = NewsPost.objects.create(
            candidate=cand2,
            slug="eu-post",
            titel="EU",
            lead="L",
            body_html="",
            kategorie="datenschutz",
            geo="EU",
            type="leitlinie",
            relevanz="hoch",
        )
        p2.publish()

        resp = api_client.get("/api/public/news/?geo=DE")
        slugs = [i["slug"] for i in resp.json()["results"]]
        assert "test-post" in slugs
        assert "eu-post" not in slugs


@pytest.mark.django_db
class TestNewsDetailEndpoint:
    def test_detail_returns_full_body(self, api_client, published_post):
        resp = api_client.get(f"/api/public/news/{published_post.slug}/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["body_html"] == "<p>Body</p>"
        assert body["source_links"] == [
            {"titel": "BfDI", "url": "https://bfdi.bund.de/foo"}
        ]

    def test_detail_404_for_unpublished(self, api_client, candidate):
        p = NewsPost.objects.create(
            candidate=candidate,
            slug="hidden2",
            titel="X",
            lead="L",
            body_html="",
            kategorie="datenschutz",
            geo="DE",
            type="leitlinie",
            relevanz="hoch",
        )
        resp = api_client.get(f"/api/public/news/{p.slug}/")
        assert resp.status_code == 404


@pytest.mark.django_db
class TestKorrekturenEndpoint:
    def test_lists_public_korrekturen(self, api_client, published_post):
        Korrektur.objects.create(
            post=published_post,
            was_geaendert="Aktenzeichen korrigiert",
            grund="Tippfehler",
        )
        resp = api_client.get("/api/public/korrekturen/")
        assert resp.status_code == 200
        items = resp.json()["results"]
        assert len(items) == 1
        assert items[0]["was_geaendert"] == "Aktenzeichen korrigiert"
        assert items[0]["post_slug"] == "test-post"
