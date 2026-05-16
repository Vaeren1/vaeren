"""Publisher-Stufe: entscheidet auto-publish vs. hold.

Logik:
- verified=True UND confidence >= 0.85 → post.publish()
- sonst → status = HOLD (Konrad sieht es in der Tagesmail)
"""

from __future__ import annotations

import logging

from redaktion.models import NewsPost, NewsPostStatus

from .verifier import CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)


def publish_or_hold(post: NewsPost, verify_result: dict) -> str:
    """Returns 'published' or 'hold'."""
    if verify_result.get("verified") and verify_result.get("confidence", 0.0) >= CONFIDENCE_THRESHOLD:
        post.publish()
        logger.info("Publisher: %s published (confidence=%.2f)", post.slug, verify_result["confidence"])
        return "published"
    post.status = NewsPostStatus.HOLD
    post.save(update_fields=["status"])
    logger.info(
        "Publisher: %s on hold (verified=%s confidence=%.2f)",
        post.slug,
        verify_result.get("verified"),
        verify_result.get("confidence", 0.0),
    )
    return "hold"
