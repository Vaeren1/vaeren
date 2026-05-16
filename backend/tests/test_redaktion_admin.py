"""Admin-Smoke-Test: alle Models sind registriert."""

import pytest
from django.contrib import admin

from redaktion.models import (
    Korrektur,
    NewsCandidate,
    NewsPost,
    NewsSource,
    RedaktionRun,
)


@pytest.mark.parametrize(
    "model",
    [NewsSource, NewsCandidate, NewsPost, RedaktionRun, Korrektur],
)
def test_model_in_admin(model):
    assert model in admin.site._registry
