"""Production-Settings. Sprint 8.

Lädt env-Variablen aus dem Container-Environment (NICHT aus .env-File);
docker-compose.prod.yml mappt die Werte aus dem Host-`.env`-File rein.

Spec §1: Compliance-Sales-Argument first → SECURE-Cookies, HSTS, CSP-Vorbereitung.
Spec §11: Mailjet, OpenRouter, Sentry — alle optional mit Fallbacks.
"""

from __future__ import annotations

import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = False

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://app.vaeren.de,https://hinweise.app.vaeren.de",
    ).split(",")
    if o.strip()
]

# --- E-Mail-Provider (Anymail) -------------------------------------------
# Priorität: Brevo > Mailjet > Console-Backend.
# Beide Provider via django-anymail — Switch ohne Code-Change.
_BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
_MAILJET_API_KEY = os.environ.get("MAILJET_API_KEY", "")
_MAILJET_SECRET_KEY = os.environ.get("MAILJET_SECRET_KEY", "")

if _BREVO_API_KEY:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    ANYMAIL = {"BREVO_API_KEY": _BREVO_API_KEY}
elif _MAILJET_API_KEY and _MAILJET_SECRET_KEY:
    EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
    ANYMAIL = {
        "MAILJET_API_KEY": _MAILJET_API_KEY,
        "MAILJET_SECRET_KEY": _MAILJET_SECRET_KEY,
    }
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get("VAEREN_FROM_EMAIL", "noreply@vaeren.de")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
VAEREN_FROM_EMAIL = DEFAULT_FROM_EMAIL

# Empfänger für das Kontakt-Formular (vaeren.de/kontakt). Alle @vaeren-Mails
# werden ohnehin nach vaeren1@outlook.de geforwarded — wir mailen direkt dorthin.
VAEREN_KONTAKT_EMAIL = os.environ.get("VAEREN_KONTAKT_EMAIL", "vaeren1@outlook.de")

# Absender-Header für Kontakt-Form-Mails. Bewusst kontakt@ statt noreply@ +
# Display-Name → bessere Outlook/Gmail-Deliverability (Spam-Filter werten
# Display-Name + menschliche Local-Part milder).
VAEREN_KONTAKT_FROM = os.environ.get(
    "VAEREN_KONTAKT_FROM", "Vaeren Kontakt <kontakt@vaeren.de>"
)

# --- Sentry (optional) ---------------------------------------------------
_SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if _SENTRY_DSN:
    sentry_sdk.init(
        dsn=_SENTRY_DSN,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,  # DSGVO-Schutz: keine User-Daten an Sentry
    )

# --- Static Files --------------------------------------------------------
STATIC_ROOT = "/app/staticfiles"
MEDIA_ROOT = "/app/media"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# --- Celery --------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Berlin"
CELERY_BEAT_SCHEDULER = "celery.beat.PersistentScheduler"

# --- Logging -------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
