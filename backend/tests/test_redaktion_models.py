"""Tests für redaktion-Models."""

from __future__ import annotations

import hashlib
from datetime import timedelta

import pytest
from django.utils import timezone

from redaktion.models import (
    Korrektur,
    NewsCandidate,
    NewsPost,
    NewsPostGeo,
    NewsPostKategorie,
    NewsPostRelevanz,
    NewsPostStatus,
    NewsPostType,
    NewsSource,
    RedaktionRun,
)


@pytest.mark.django_db
class TestNewsSource:
    def test_creates_with_required_fields(self):
        src = NewsSource.objects.create(
            key="eur_lex",
            name="EUR-Lex",
            base_url="https://eur-lex.europa.eu",
            parser_key="redaktion.sources.eur_lex.EurLexParser",
        )
        assert src.active is True
        assert src.last_crawled_at is None

    def test_key_is_unique(self):
        NewsSource.objects.create(
            key="eur_lex",
            name="EUR-Lex",
            base_url="https://eur-lex.europa.eu",
            parser_key="x",
        )
        with pytest.raises(Exception):
            NewsSource.objects.create(
                key="eur_lex",
                name="dup",
                base_url="https://x.example",
                parser_key="x",
            )

    def test_str_returns_name(self):
        src = NewsSource.objects.create(
            key="bfdi",
            name="BfDI",
            base_url="https://bfdi.bund.de",
            parser_key="x",
        )
        assert str(src) == "BfDI"


@pytest.mark.django_db
class TestNewsCandidate:
    @pytest.fixture
    def source(self):
        return NewsSource.objects.create(
            key="eur_lex",
            name="EUR-Lex",
            base_url="https://eur-lex.europa.eu",
            parser_key="x",
        )

    def test_url_hash_auto_computed(self, source):
        url = "https://eur-lex.europa.eu/foo/bar"
        cand = NewsCandidate.objects.create(
            source=source,
            quell_url=url,
            titel_raw="X",
            excerpt_raw="Y",
        )
        assert cand.quell_url_hash == hashlib.sha256(url.encode()).hexdigest()

    def test_dedup_by_url_hash(self, source):
        url = "https://eur-lex.europa.eu/foo/bar"
        NewsCandidate.objects.create(
            source=source, quell_url=url, titel_raw="A", excerpt_raw=""
        )
        with pytest.raises(Exception):
            NewsCandidate.objects.create(
                source=source, quell_url=url, titel_raw="B", excerpt_raw=""
            )

    def test_status_helpers(self, source):
        cand = NewsCandidate.objects.create(
            source=source,
            quell_url="https://x.example/1",
            titel_raw="X",
            excerpt_raw="",
        )
        assert cand.is_pending
        assert not cand.is_selected


@pytest.fixture
def post_source(db):
    return NewsSource.objects.create(
        key="curia",
        name="EuGH",
        base_url="https://curia.europa.eu",
        parser_key="x",
    )


@pytest.fixture
def post_candidate(post_source):
    return NewsCandidate.objects.create(
        source=post_source,
        quell_url="https://curia.europa.eu/case/123",
        titel_raw="EuGH-Urteil",
        excerpt_raw="",
    )


@pytest.mark.django_db
class TestNewsPost:
    def test_creates_with_pending_verify_default(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="eugh-art-15-auskunft-2026",
            titel="EuGH stärkt Auskunftsanspruch",
            lead="Lead",
            body_html="<p>Body</p>",
            kategorie=NewsPostKategorie.DATENSCHUTZ,
            geo=NewsPostGeo.EU,
            type=NewsPostType.URTEIL,
            relevanz=NewsPostRelevanz.HOCH,
        )
        assert post.status == NewsPostStatus.PENDING_VERIFY
        assert post.unpublish_token
        assert len(post.unpublish_token) >= 40
        assert post.published_at is None

    def test_publish_sets_expiry_from_relevanz_hoch(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.AI_ACT,
            geo=NewsPostGeo.EU,
            type=NewsPostType.GESETZGEBUNG,
            relevanz=NewsPostRelevanz.HOCH,
        )
        post.publish()
        assert post.status == NewsPostStatus.PUBLISHED
        assert post.published_at is not None
        assert post.expires_at is not None
        delta_days = (post.expires_at - post.published_at).days
        assert 89 <= delta_days <= 91

    def test_publish_mittel_30_days(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.HINSCHG,
            geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE,
            relevanz=NewsPostRelevanz.MITTEL,
        )
        post.publish()
        delta = (post.expires_at - post.published_at).days
        assert 29 <= delta <= 31

    def test_publish_niedrig_7_days(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.HINSCHG,
            geo=NewsPostGeo.DE,
            type=NewsPostType.FRIST,
            relevanz=NewsPostRelevanz.NIEDRIG,
        )
        post.publish()
        delta = (post.expires_at - post.published_at).days
        assert 6 <= delta <= 8

    def test_unpublish_via_token(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.HINSCHG,
            geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE,
            relevanz=NewsPostRelevanz.MITTEL,
        )
        post.publish()
        post.unpublish()
        assert post.status == NewsPostStatus.UNPUBLISHED

    def test_is_visible_when_published_and_not_expired(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.HINSCHG,
            geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE,
            relevanz=NewsPostRelevanz.HOCH,
        )
        post.publish()
        assert post.is_visible

        post.expires_at = timezone.now() - timedelta(days=1)
        post.save()
        assert not post.is_visible

    def test_pinned_overrides_expiry(self, post_candidate):
        post = NewsPost.objects.create(
            candidate=post_candidate,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie=NewsPostKategorie.HINSCHG,
            geo=NewsPostGeo.DE,
            type=NewsPostType.LEITLINIE,
            relevanz=NewsPostRelevanz.NIEDRIG,
            pinned=True,
        )
        post.publish()
        post.expires_at = timezone.now() - timedelta(days=10)
        post.save()
        assert post.is_visible  # pinned überholt Expiry


@pytest.mark.django_db
class TestRedaktionRun:
    def test_default_counts_zero(self):
        run = RedaktionRun.objects.create()
        assert run.crawler_items_in == 0
        assert run.published == 0
        assert run.finished_at is None
        assert run.cost_eur == 0


@pytest.mark.django_db
class TestKorrektur:
    @pytest.fixture
    def post(self):
        src = NewsSource.objects.create(
            key="curia",
            name="EuGH",
            base_url="https://curia.europa.eu",
            parser_key="x",
        )
        cand = NewsCandidate.objects.create(
            source=src,
            quell_url="https://x.example/1",
            titel_raw="X",
            excerpt_raw="",
        )
        return NewsPost.objects.create(
            candidate=cand,
            slug="x",
            titel="X",
            lead="X",
            body_html="",
            kategorie="datenschutz",
            geo="EU",
            type="urteil",
            relevanz="hoch",
        )

    def test_creates_with_visible_default(self, post):
        k = Korrektur.objects.create(
            post=post,
            was_geaendert="Aktenzeichen korrigiert",
            grund="Tippfehler",
        )
        assert k.korrigiert_am is not None
        assert k.post == post
