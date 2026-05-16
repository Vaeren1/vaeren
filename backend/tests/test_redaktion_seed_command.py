"""seed_redaktion-Command: idempotent."""

import pytest
from django.core.management import call_command

from redaktion.models import NewsPost, NewsSource


@pytest.mark.django_db
def test_seed_creates_12_sources_and_10_posts():
    call_command("seed_redaktion")
    assert NewsSource.objects.count() == 12
    assert NewsPost.objects.count() == 10
    assert NewsPost.objects.filter(status="published").count() == 10


@pytest.mark.django_db
def test_seed_is_idempotent():
    call_command("seed_redaktion")
    call_command("seed_redaktion")
    assert NewsSource.objects.count() == 12
    assert NewsPost.objects.count() == 10


@pytest.mark.django_db
def test_seed_covers_all_kategorien():
    call_command("seed_redaktion")
    kategorien = set(NewsPost.objects.values_list("kategorie", flat=True))
    # Mindestens 6 der 8 Kategorien sollen abgedeckt sein
    assert len(kategorien) >= 6
