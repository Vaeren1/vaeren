"""Seed: 12 NewsSources + 10 handgeschriebene Initial-Posts.

Idempotent: bei wiederholtem Aufruf werden bestehende Einträge nicht
dupliziert (update_or_create). Posts werden direkt published (analog zum
ersten Site-Launch).
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from redaktion.fixtures.initial_posts import INITIAL_POSTS
from redaktion.models import NewsCandidate, NewsPost, NewsPostStatus, NewsSource

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


class Command(BaseCommand):
    help = "Seedet 12 NewsSources + 10 Initial-Posts (idempotent)."

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        sources_created = self._seed_sources()
        posts_created = self._seed_posts()
        self.stdout.write(
            self.style.SUCCESS(
                f"redaktion seed: sources={sources_created}, posts={posts_created}"
            )
        )

    def _seed_sources(self) -> int:
        path = FIXTURES_DIR / "initial_sources.json"
        with path.open() as fh:
            data = json.load(fh)
        created = 0
        for row in data:
            _, was_created = NewsSource.objects.update_or_create(
                key=row["key"],
                defaults={
                    "name": row["name"],
                    "base_url": row["base_url"],
                    "parser_key": row["parser_key"],
                },
            )
            created += 1 if was_created else 0
        return created

    def _seed_posts(self) -> int:
        created = 0
        for entry in INITIAL_POSTS:
            source = NewsSource.objects.get(key=entry["source_key"])
            candidate, _ = NewsCandidate.objects.update_or_create(
                quell_url=entry["source_links"][0]["url"],
                defaults={
                    "source": source,
                    "titel_raw": entry["titel"],
                    "excerpt_raw": entry["lead"],
                    "selected_at": timezone.now(),
                },
            )
            post, was_created = NewsPost.objects.update_or_create(
                slug=entry["slug"],
                defaults={
                    "candidate": candidate,
                    "titel": entry["titel"],
                    "lead": entry["lead"],
                    "body_html": entry["body_html"],
                    "kategorie": entry["kategorie"],
                    "geo": entry["geo"],
                    "type": entry["type"],
                    "relevanz": entry["relevanz"],
                    "source_links": entry["source_links"],
                },
            )
            if post.status != NewsPostStatus.PUBLISHED:
                post.publish()
            created += 1 if was_created else 0
        return created
