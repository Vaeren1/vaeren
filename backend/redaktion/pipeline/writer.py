"""Writer-Stufe: erzeugt aus selektiertem Candidate einen NewsPost-Entwurf."""

from __future__ import annotations

import json
import logging
import re

from django.utils.text import slugify

from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus

from .llm import MODELS_FAST, call_json_with_fallback
from .prompts import WRITER_SYSTEM

logger = logging.getLogger(__name__)


def _clean_dashes(text: str) -> str:
    """Ersetzt en-/em-Dash durch normales Komma + Leerzeichen.

    Style-Vorgabe: keine Gedankenstriche.
    """
    return text.replace(" – ", ", ").replace(" — ", ", ").replace("–", "-").replace("—", "-")


def _make_unique_slug(base: str) -> str:
    slug = slugify(base)[:180] or "beitrag"
    if not NewsPost.objects.filter(slug=slug).exists():
        return slug
    i = 2
    while NewsPost.objects.filter(slug=f"{slug}-{i}").exists():
        i += 1
    return f"{slug}-{i}"


def write_post_from_candidate(candidate: NewsCandidate, meta: dict) -> NewsPost | None:
    """Ruft Writer-LLM und schreibt einen NewsPost-Row.

    meta enthält die Curator-Entscheidung: kategorie, geo, type, relevanz.
    Returns None wenn LLM keinen valid JSON liefert.
    """
    user = json.dumps(
        {
            "instruction": (
                "Verfasse einen Beitrag mit titel, lead und body_html aus folgender Quelle. "
                "Halte dich strikt an die Stilvorgaben."
            ),
            "source_titel": candidate.titel_raw,
            "source_excerpt": candidate.excerpt_raw,
            "source_url": candidate.quell_url,
            "source_name": candidate.source.name,
            "kategorie": meta.get("kategorie"),
            "geo": meta.get("geo"),
            "type": meta.get("type"),
        },
        ensure_ascii=False,
    )
    response = call_json_with_fallback(
        system=WRITER_SYSTEM,
        user=user,
        models=MODELS_FAST,
        max_tokens=1600,
        temperature=0.4,
    )
    if not response:
        logger.warning("Writer: keine valide Antwort für candidate %s", candidate.pk)
        return None

    titel = _clean_dashes(response.get("titel", "").strip())[:200]
    lead = _clean_dashes(response.get("lead", "").strip())[:600]
    body_html = _clean_dashes(response.get("body_html", "").strip())
    if not titel or not lead or not body_html:
        logger.warning("Writer: unvollständige Antwort: %r", response)
        return None

    # Quell-Link sicherstellen (falls Writer ihn nicht im body_html eingebaut hat)
    if candidate.quell_url not in body_html:
        body_html += (
            f'<p><strong>Quelle:</strong> '
            f'<a href="{candidate.quell_url}" rel="external nofollow">{candidate.source.name}</a></p>'
        )

    slug = _make_unique_slug(titel)
    post, created = NewsPost.objects.update_or_create(
        candidate=candidate,
        defaults={
            "slug": slug,
            "titel": titel,
            "lead": lead,
            "body_html": body_html,
            "kategorie": meta.get("kategorie", "datenschutz"),
            "geo": meta.get("geo", "EU"),
            "type": meta.get("type", "leitlinie"),
            "relevanz": meta.get("relevanz", "mittel"),
            "source_links": [
                {"titel": candidate.source.name, "url": candidate.quell_url}
            ],
            "status": NewsPostStatus.PENDING_VERIFY,
        },
    )
    logger.info(
        "Writer: NewsPost %s [%s] (%s) angelegt",
        post.slug,
        post.kategorie,
        "neu" if created else "aktualisiert",
    )
    return post
