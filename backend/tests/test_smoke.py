"""Smoke-Test — wird durch echte Tests in Task 5+ ersetzt."""
import django


def test_django_imports() -> None:
    assert django.VERSION[0] == 5
