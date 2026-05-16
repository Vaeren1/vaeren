"""Notbremse-URL: GET /api/public/redaktion/unpublish/<token>/

Bewusste API-Wahl: GET (nicht POST), damit der Link aus der Tagesmail
ohne JS funktioniert (Klick → sofort wirksam).
"""

import pytest
from rest_framework.test import APIClient

from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus, NewsSource


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def post(db):
    src = NewsSource.objects.create(
        key="x",
        name="X",
        base_url="https://x.example",
        parser_key="x",
    )
    cand = NewsCandidate.objects.create(
        source=src,
        quell_url="https://x.example/1",
        titel_raw="X",
        excerpt_raw="",
    )
    p = NewsPost.objects.create(
        candidate=cand,
        slug="x-1",
        titel="X",
        lead="L",
        body_html="",
        kategorie="datenschutz",
        geo="DE",
        type="leitlinie",
        relevanz="hoch",
    )
    p.publish()
    return p


@pytest.mark.django_db
def test_valid_token_unpublishes_post(api_client, post):
    assert post.status == NewsPostStatus.PUBLISHED
    resp = api_client.get(
        f"/api/public/redaktion/unpublish/{post.unpublish_token}/"
    )
    assert resp.status_code == 200
    post.refresh_from_db()
    assert post.status == NewsPostStatus.UNPUBLISHED


@pytest.mark.django_db
def test_invalid_token_returns_404(api_client, post):
    resp = api_client.get(
        "/api/public/redaktion/unpublish/totally-wrong-token-12345/"
    )
    assert resp.status_code == 404
    post.refresh_from_db()
    assert post.status == NewsPostStatus.PUBLISHED


@pytest.mark.django_db
def test_response_contains_confirmation_text(api_client, post):
    resp = api_client.get(
        f"/api/public/redaktion/unpublish/{post.unpublish_token}/"
    )
    msg = resp.json().get("message", "").lower()
    assert "zurückgezogen" in msg or "unpublish" in msg
