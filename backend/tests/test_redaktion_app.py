"""Smoke-Test: redaktion-App ist registriert + im SHARED_APPS-Block."""

import pytest
from django.apps import apps
from django.conf import settings


def test_redaktion_app_is_registered():
    assert "redaktion" in [a.name for a in apps.get_app_configs()]


def test_redaktion_in_shared_apps():
    assert "redaktion" in settings.SHARED_APPS
