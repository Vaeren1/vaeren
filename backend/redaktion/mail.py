"""Tagesmail-Versand an die Vaeren-Redaktion.

Listet alle Posts der letzten 24h (published + hold) mit Notbremse-Links.
Versand via Anymail/Brevo (bestehende Konfiguration aus core/notifications).
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from redaktion.models import NewsPost, NewsPostStatus

logger = logging.getLogger(__name__)


REDAKTION_EMAIL = getattr(settings, "REDAKTION_EMAIL", "kontakt@vaeren.de")
PUBLIC_BASE = getattr(settings, "VAEREN_PUBLIC_BASE", "https://vaeren.de")
APP_BASE = getattr(settings, "VAEREN_APP_BASE", "https://app.vaeren.de")


def send_daily_digest() -> dict:
    """Schickt eine Mail mit den Posts der letzten 24h."""
    since = timezone.now() - timedelta(hours=24)
    recent = NewsPost.objects.filter(
        updated_at__gte=since,
        status__in=[NewsPostStatus.PUBLISHED, NewsPostStatus.HOLD],
    ).order_by("-updated_at")

    if not recent.exists():
        logger.info("daily_digest: nichts zu berichten (0 Posts in 24h)")
        return {"sent": False, "count": 0}

    published = [p for p in recent if p.status == NewsPostStatus.PUBLISHED]
    held = [p for p in recent if p.status == NewsPostStatus.HOLD]

    lines: list[str] = [
        "Vaeren-Redaktion · Tagesbericht " + timezone.now().strftime("%d. %B %Y"),
        "",
        f"Veröffentlicht heute ({len(published)}):",
    ]
    if not published:
        lines.append("  (keine)")
    for p in published:
        lines.append(f"  - [{p.titel}]")
        lines.append(f"    Vorschau:  {PUBLIC_BASE}/news/{p.slug}")
        lines.append(
            f"    Notbremse: {APP_BASE}/api/public/redaktion/unpublish/{p.unpublish_token}/"
        )
        lines.append("")

    lines.append(f"Warten auf manuelle Sichtung ({len(held)}):")
    if not held:
        lines.append("  (keine)")
    for p in held:
        issues_short = (
            "; ".join(str(i)[:120] for i in (p.verifier_issues or [])[:3])
            or "kein Issue gemeldet"
        )
        lines.append(f"  - [{p.titel}] confidence={p.verifier_confidence or 0:.2f}")
        lines.append(f"    Issues: {issues_short}")
        lines.append(f"    Admin:  {APP_BASE}/admin/redaktion/newspost/{p.pk}/change/")
        lines.append("")

    body = "\n".join(lines)
    msg = EmailMessage(
        subject=f"Vaeren-Redaktion Tagesbericht ({len(published)} live, {len(held)} hold)",
        body=body,
        from_email=getattr(settings, "VAEREN_FROM_EMAIL", "noreply@vaeren.de"),
        to=[REDAKTION_EMAIL],
    )
    try:
        sent = msg.send(fail_silently=False)
    except Exception as exc:
        logger.warning("daily_digest: Mail-Versand fehlgeschlagen: %s", exc)
        return {"sent": False, "count": recent.count(), "error": str(exc)}

    logger.info(
        "daily_digest: %d Mails versendet (published=%d hold=%d)",
        sent,
        len(published),
        len(held),
    )
    return {"sent": bool(sent), "count": recent.count(), "published": len(published), "held": len(held)}
