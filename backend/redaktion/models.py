"""Redaktions-Models (public-Schema, tenant-übergreifend).

Spec: docs/superpowers/specs/2026-05-16-marketing-site-design.md §3.3

- NewsSource: Whitelist-Quelle (EUR-Lex, BfDI, EuGH, …)
- NewsCandidate: Roh-Item aus dem Crawler, Curator wählt aus
- NewsPost: Fertiger öffentlicher Beitrag, sichtbar auf Marketing-Site
- RedaktionRun: Pro Pipeline-Lauf eine Telemetrie-Zeile
- Korrektur: Öffentlich angezeigte Korrektur-Historie
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


class NewsSource(models.Model):
    """Whitelist-Quelle (EUR-Lex, BfDI, EuGH, ...)."""

    key = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    base_url = models.URLField()
    parser_key = models.CharField(
        max_length=200,
        help_text="FQDN der Parser-Klasse, z.B. redaktion.sources.eur_lex.EurLexParser",
    )
    active = models.BooleanField(default=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "News-Quelle"
        verbose_name_plural = "News-Quellen"

    def __str__(self) -> str:
        return self.name


class NewsCandidate(models.Model):
    """Roh-Item aus dem Crawler. Curator wählt daraus aus."""

    source = models.ForeignKey(
        NewsSource, on_delete=models.PROTECT, related_name="candidates"
    )
    quell_url = models.URLField(max_length=500)
    quell_url_hash = models.CharField(max_length=64, unique=True, editable=False)
    titel_raw = models.TextField()
    excerpt_raw = models.TextField(blank=True, default="")
    published_at_source = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    selected_at = models.DateTimeField(null=True, blank=True)
    discarded_at = models.DateTimeField(null=True, blank=True)
    curator_begruendung = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-fetched_at",)
        verbose_name = "News-Kandidat"
        verbose_name_plural = "News-Kandidaten"
        indexes = [
            models.Index(fields=["selected_at"]),
            models.Index(fields=["discarded_at"]),
        ]

    def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        if not self.quell_url_hash:
            self.quell_url_hash = hashlib.sha256(self.quell_url.encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def is_pending(self) -> bool:
        return self.selected_at is None and self.discarded_at is None

    @property
    def is_selected(self) -> bool:
        return self.selected_at is not None

    def __str__(self) -> str:
        return f"{self.source.key}: {self.titel_raw[:60]}"


class NewsPostStatus(models.TextChoices):
    PENDING_VERIFY = "pending_verify", "Wartet auf Verifier"
    HOLD = "hold", "Manuelle Sichtung erforderlich"
    PUBLISHED = "published", "Live"
    UNPUBLISHED = "unpublished", "Zurückgezogen"


class NewsPostKategorie(models.TextChoices):
    AI_ACT = "ai_act", "AI Act"
    DATENSCHUTZ = "datenschutz", "Datenschutz"
    HINSCHG = "hinschg", "HinSchG"
    LIEFERKETTE = "lieferkette", "Lieferkette"
    ARBEITSRECHT = "arbeitsrecht", "Arbeitsrecht"
    GELDWAESCHE_FINANZEN = "geldwaesche_finanzen", "Geldwäsche/Finanzen"
    IT_SICHERHEIT = "it_sicherheit", "IT-Sicherheit"
    ESG_NACHHALTIGKEIT = "esg_nachhaltigkeit", "ESG/Nachhaltigkeit"


class NewsPostGeo(models.TextChoices):
    EU = "EU", "EU"
    DE = "DE", "DE"
    EU_DE = "EU_DE", "EU→DE-Umsetzung"


class NewsPostType(models.TextChoices):
    GESETZGEBUNG = "gesetzgebung", "Gesetzgebung"
    URTEIL = "urteil", "Urteil"
    LEITLINIE = "leitlinie", "Leitlinie/FAQ"
    KONSULTATION = "konsultation", "Konsultation"
    FRIST = "frist", "Frist"


class NewsPostRelevanz(models.TextChoices):
    HOCH = "hoch", "Hoch"
    MITTEL = "mittel", "Mittel"
    NIEDRIG = "niedrig", "Niedrig"


LIFETIME_DAYS_BY_RELEVANZ = {
    NewsPostRelevanz.HOCH: 90,
    NewsPostRelevanz.MITTEL: 30,
    NewsPostRelevanz.NIEDRIG: 7,
}


def _generate_unpublish_token() -> str:
    return secrets.token_urlsafe(48)


class NewsPost(models.Model):
    """Fertiger News-Beitrag. Sichtbar auf der Marketing-Site."""

    candidate = models.OneToOneField(
        NewsCandidate,
        on_delete=models.PROTECT,
        related_name="post",
        null=True,
        blank=True,
    )
    slug = models.SlugField(max_length=200, unique=True)
    titel = models.CharField(max_length=200)
    lead = models.TextField()
    body_html = models.TextField()
    kategorie = models.CharField(max_length=30, choices=NewsPostKategorie.choices)
    geo = models.CharField(max_length=10, choices=NewsPostGeo.choices)
    type = models.CharField(max_length=20, choices=NewsPostType.choices)
    relevanz = models.CharField(max_length=10, choices=NewsPostRelevanz.choices)
    source_links = models.JSONField(
        default=list,
        help_text="Liste [{titel: str, url: str}]",
    )
    status = models.CharField(
        max_length=20,
        choices=NewsPostStatus.choices,
        default=NewsPostStatus.PENDING_VERIFY,
    )
    verifier_confidence = models.FloatField(null=True, blank=True)
    verifier_issues = models.JSONField(default=list, blank=True)
    pinned = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    unpublish_token = models.CharField(
        max_length=80,
        default=_generate_unpublish_token,
        editable=False,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")
        verbose_name = "News-Beitrag"
        verbose_name_plural = "News-Beiträge"
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["kategorie"]),
            models.Index(fields=["geo"]),
        ]

    def publish(self) -> None:
        now = timezone.now()
        days = LIFETIME_DAYS_BY_RELEVANZ[NewsPostRelevanz(self.relevanz)]
        self.status = NewsPostStatus.PUBLISHED
        self.published_at = now
        self.expires_at = now + timedelta(days=days)
        self.save()

    def unpublish(self) -> None:
        self.status = NewsPostStatus.UNPUBLISHED
        self.save()

    @property
    def is_visible(self) -> bool:
        if self.status != NewsPostStatus.PUBLISHED:
            return False
        if self.pinned:
            return True
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def __str__(self) -> str:
        return f"{self.titel} [{self.status}]"


class RedaktionRun(models.Model):
    """Pro Pipeline-Lauf eine Zeile (Crawler→Curator→Writer→Verifier→Publisher)."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    crawler_items_in = models.IntegerField(default=0)
    curator_items_out = models.IntegerField(default=0)
    writer_runs = models.IntegerField(default=0)
    verifier_runs = models.IntegerField(default=0)
    published = models.IntegerField(default=0)
    held = models.IntegerField(default=0)
    cost_eur = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ("-started_at",)
        verbose_name = "Redaktions-Lauf"
        verbose_name_plural = "Redaktions-Läufe"

    def __str__(self) -> str:
        return f"Run #{self.pk} @ {self.started_at:%Y-%m-%d %H:%M}"


class Korrektur(models.Model):
    """Öffentlich angezeigte Korrektur-Historie."""

    post = models.ForeignKey(
        NewsPost, on_delete=models.PROTECT, related_name="korrekturen"
    )
    korrigiert_am = models.DateTimeField(auto_now_add=True)
    was_geaendert = models.TextField()
    grund = models.TextField()

    class Meta:
        ordering = ("-korrigiert_am",)
        verbose_name = "Korrektur"
        verbose_name_plural = "Korrekturen"

    def __str__(self) -> str:
        return f"Korrektur #{self.pk} an {self.post.slug}"
