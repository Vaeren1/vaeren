"""Prod-Settings. Wird in Sprint 8 (Production-Deploy) finalisiert."""

from .base import *

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
