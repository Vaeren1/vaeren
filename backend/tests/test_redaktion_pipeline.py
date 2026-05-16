"""Tests für die Redaktions-Pipeline.

Echte LLM- und HTTP-Calls werden gemockt. Die End-to-End-Smoke-Tests gehen
durch den Curator → Writer → Verifier → Publisher Flow ohne Netz.
"""

from __future__ import annotations

from unittest import mock

import pytest

from redaktion.models import (
    NewsCandidate,
    NewsPost,
    NewsPostStatus,
    NewsSource,
)


@pytest.fixture
def source(db):
    return NewsSource.objects.create(
        key="bfdi",
        name="BfDI",
        base_url="https://bfdi.bund.de",
        parser_key="redaktion.sources.bfdi.BfdiParser",
    )


@pytest.fixture
def candidate(source):
    return NewsCandidate.objects.create(
        source=source,
        quell_url="https://bfdi.bund.de/test-pressemitteilung",
        titel_raw="BfDI veröffentlicht neue Leitlinie zur Pseudonymisierung",
        excerpt_raw="Der BfDI hat eine Leitlinie zur Pseudonymisierung veröffentlicht.",
    )


# -- LLM-Helper-Tests ----------------------------------------------------


class TestExtractJson:
    def test_plain_json(self):
        from redaktion.pipeline.llm import _extract_json

        assert _extract_json('{"a": 1}') == {"a": 1}

    def test_markdown_codefence(self):
        from redaktion.pipeline.llm import _extract_json

        raw = "Hier mein Ergebnis:\n```json\n{\"a\": 1, \"b\": 2}\n```\nViel Erfolg!"
        assert _extract_json(raw) == {"a": 1, "b": 2}

    def test_extract_first_brace_block(self):
        from redaktion.pipeline.llm import _extract_json

        raw = "Vorab: hier ist die Antwort. {\"selected\": []}. Das wars."
        assert _extract_json(raw) == {"selected": []}

    def test_invalid_returns_none(self):
        from redaktion.pipeline.llm import _extract_json

        assert _extract_json("kein JSON hier") is None
        assert _extract_json("{nicht valides JSON") is None
        assert _extract_json("") is None


# -- Curator-Tests -------------------------------------------------------


@pytest.mark.django_db
class TestCurator:
    def test_curator_selects_candidates(self, candidate):
        fake_response = {
            "selected": [
                {
                    "candidate_id": candidate.pk,
                    "kategorie": "datenschutz",
                    "geo": "DE",
                    "type": "leitlinie",
                    "relevanz": "hoch",
                    "begruendung": "Praxisrelevant für Datenschutz-Beauftragte.",
                }
            ]
        }
        with mock.patch("redaktion.pipeline.curator.call_json", return_value=fake_response):
            from redaktion.pipeline.curator import curate_pending

            result = curate_pending()

        assert len(result) == 1
        candidate.refresh_from_db()
        assert candidate.selected_at is not None
        assert "Praxisrelevant" in candidate.curator_begruendung

    def test_curator_discards_non_selected(self, source, candidate):
        # zweiter, nicht-selektierter Candidate
        other = NewsCandidate.objects.create(
            source=source,
            quell_url="https://bfdi.bund.de/anderes",
            titel_raw="Werbeveranstaltung",
        )
        fake_response = {
            "selected": [
                {
                    "candidate_id": candidate.pk,
                    "kategorie": "datenschutz",
                    "geo": "DE",
                    "type": "leitlinie",
                    "relevanz": "mittel",
                    "begruendung": "ok",
                }
            ]
        }
        with mock.patch("redaktion.pipeline.curator.call_json", return_value=fake_response):
            from redaktion.pipeline.curator import curate_pending

            curate_pending()

        other.refresh_from_db()
        assert other.discarded_at is not None
        assert other.selected_at is None

    def test_curator_no_response_returns_empty(self, candidate):
        with mock.patch("redaktion.pipeline.curator.call_json", return_value=None):
            from redaktion.pipeline.curator import curate_pending

            assert curate_pending() == []


# -- Writer-Tests --------------------------------------------------------


@pytest.mark.django_db
class TestWriter:
    def test_writer_creates_post(self, candidate):
        fake_response = {
            "titel": "BfDI-Leitlinie zur Pseudonymisierung",
            "lead": "Der BfDI hat eine Leitlinie veröffentlicht.",
            "body_html": "<p>Inhalt mit <a href='https://bfdi.bund.de/test-pressemitteilung'>Quelle</a>.</p>",
        }
        with mock.patch("redaktion.pipeline.writer.call_json", return_value=fake_response):
            from redaktion.pipeline.writer import write_post_from_candidate

            post = write_post_from_candidate(
                candidate,
                {"kategorie": "datenschutz", "geo": "DE", "type": "leitlinie", "relevanz": "hoch"},
            )

        assert post is not None
        assert post.status == NewsPostStatus.PENDING_VERIFY
        assert post.candidate == candidate
        assert post.slug.startswith("bfdi-leitlinie")

    def test_writer_cleans_dashes(self, candidate):
        fake_response = {
            "titel": "Titel — mit Gedankenstrich",
            "lead": "Lead – auch mit Strich.",
            "body_html": "<p>Body – mit Strich.</p>",
        }
        with mock.patch("redaktion.pipeline.writer.call_json", return_value=fake_response):
            from redaktion.pipeline.writer import write_post_from_candidate

            post = write_post_from_candidate(
                candidate,
                {"kategorie": "datenschutz", "geo": "DE", "type": "leitlinie", "relevanz": "hoch"},
            )

        assert "—" not in post.titel
        assert "–" not in post.lead
        assert "–" not in post.body_html

    def test_writer_appends_source_if_missing(self, candidate):
        fake_response = {
            "titel": "Titel ohne Quell-Link",
            "lead": "Lead ohne Link",
            "body_html": "<p>Body ganz ohne Quelle.</p>",
        }
        with mock.patch("redaktion.pipeline.writer.call_json", return_value=fake_response):
            from redaktion.pipeline.writer import write_post_from_candidate

            post = write_post_from_candidate(
                candidate,
                {"kategorie": "datenschutz", "geo": "DE", "type": "leitlinie", "relevanz": "hoch"},
            )

        assert candidate.quell_url in post.body_html

    def test_writer_returns_none_on_no_llm(self, candidate):
        with mock.patch("redaktion.pipeline.writer.call_json", return_value=None):
            from redaktion.pipeline.writer import write_post_from_candidate

            assert (
                write_post_from_candidate(
                    candidate,
                    {"kategorie": "datenschutz", "geo": "DE", "type": "leitlinie", "relevanz": "hoch"},
                )
                is None
            )


# -- Verifier+Publisher-Tests --------------------------------------------


@pytest.mark.django_db
class TestVerifierPublisher:
    @pytest.fixture
    def draft_post(self, candidate):
        return NewsPost.objects.create(
            candidate=candidate,
            slug="test-entwurf",
            titel="Test",
            lead="Lead",
            body_html="<p>Body</p>",
            kategorie="datenschutz",
            geo="DE",
            type="leitlinie",
            relevanz="hoch",
            source_links=[{"titel": "BfDI", "url": "https://bfdi.bund.de/test"}],
        )

    def test_high_confidence_publishes(self, draft_post):
        with mock.patch(
            "redaktion.pipeline.verifier.call_json",
            return_value={"verified": True, "confidence": 0.92, "issues": []},
        ), mock.patch(
            "redaktion.pipeline.verifier._fetch_source_text", return_value="Quell-Text"
        ):
            from redaktion.pipeline.publisher import publish_or_hold
            from redaktion.pipeline.verifier import verify_post

            result = verify_post(draft_post)
            outcome = publish_or_hold(draft_post, result)

        draft_post.refresh_from_db()
        assert outcome == "published"
        assert draft_post.status == NewsPostStatus.PUBLISHED
        assert draft_post.verifier_confidence == 0.92

    def test_low_confidence_holds(self, draft_post):
        with mock.patch(
            "redaktion.pipeline.verifier.call_json",
            return_value={"verified": False, "confidence": 0.6, "issues": ["Aktenzeichen falsch"]},
        ), mock.patch(
            "redaktion.pipeline.verifier._fetch_source_text", return_value="Quell-Text"
        ):
            from redaktion.pipeline.publisher import publish_or_hold
            from redaktion.pipeline.verifier import verify_post

            result = verify_post(draft_post)
            outcome = publish_or_hold(draft_post, result)

        draft_post.refresh_from_db()
        assert outcome == "hold"
        assert draft_post.status == NewsPostStatus.HOLD
        assert "Aktenzeichen falsch" in draft_post.verifier_issues


# -- Tagesmail-Test ------------------------------------------------------


@pytest.mark.django_db
class TestDailyDigest:
    def test_digest_sends_when_posts_exist(self, candidate, settings):
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        from django.core import mail
        mail.outbox = []

        post = NewsPost.objects.create(
            candidate=candidate,
            slug="published-heute",
            titel="Heute-Post",
            lead="L",
            body_html="<p>B</p>",
            kategorie="datenschutz",
            geo="DE",
            type="leitlinie",
            relevanz="hoch",
        )
        post.publish()

        from redaktion.mail import send_daily_digest

        result = send_daily_digest()

        assert result["sent"] is True
        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert "Heute-Post" in msg.body
        assert "Notbremse:" in msg.body
        assert post.unpublish_token in msg.body

    def test_digest_skips_when_no_posts(self, db, settings):
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        from django.core import mail
        mail.outbox = []

        from redaktion.mail import send_daily_digest

        result = send_daily_digest()
        assert result == {"sent": False, "count": 0}
        assert len(mail.outbox) == 0


# -- Parser-Smoke-Tests --------------------------------------------------


class TestParserImports:
    """Stellt sicher, dass die Parser-Module valide laden."""

    @pytest.mark.parametrize(
        "fqdn",
        [
            "redaktion.sources.eur_lex.EurLexParser",
            "redaktion.sources.bfdi.BfdiParser",
            "redaktion.sources.bmj.BmjParser",
            "redaktion.sources.edpb.EdpbParser",
        ],
    )
    def test_parser_loads(self, fqdn):
        from redaktion.sources.base import load_parser

        parser = load_parser(fqdn)
        assert parser is not None
        assert hasattr(parser, "parse")
