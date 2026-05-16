"""DRF-Serializer für public News-Endpoints.

Wichtig: interne Felder (unpublish_token, verifier_confidence, verifier_issues,
candidate) werden NIE exponiert. Public-Felder werden whitelisted (nicht
exclude), damit neue Felder im Model nicht versehentlich rausgehen.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import Korrektur, NewsPost


class KorrekturPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Korrektur
        fields = ("korrigiert_am", "was_geaendert", "grund")


class NewsPostListSerializer(serializers.ModelSerializer):
    """Kompakte Form für /news-Übersicht."""

    class Meta:
        model = NewsPost
        fields = (
            "slug",
            "titel",
            "lead",
            "kategorie",
            "geo",
            "type",
            "relevanz",
            "published_at",
            "pinned",
        )


class NewsPostPublicSerializer(serializers.ModelSerializer):
    """Voller Public-Detail-Serializer."""

    korrekturen = KorrekturPublicSerializer(many=True, read_only=True)

    class Meta:
        model = NewsPost
        fields = (
            "slug",
            "titel",
            "lead",
            "body_html",
            "kategorie",
            "geo",
            "type",
            "relevanz",
            "source_links",
            "published_at",
            "pinned",
            "korrekturen",
        )


class KorrekturPublicListSerializer(serializers.ModelSerializer):
    """Für /korrekturen-Seite: zeigt Post-Titel + Slug zusätzlich."""

    post_slug = serializers.CharField(source="post.slug", read_only=True)
    post_titel = serializers.CharField(source="post.titel", read_only=True)

    class Meta:
        model = Korrektur
        fields = (
            "korrigiert_am",
            "was_geaendert",
            "grund",
            "post_slug",
            "post_titel",
        )
