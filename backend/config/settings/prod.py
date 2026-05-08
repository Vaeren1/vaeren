"""Prod-Settings. Wird in Sprint 8 (Production-Deploy) finalisiert."""
from .base import *  # noqa: F401,F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
