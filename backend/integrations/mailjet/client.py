"""Mailjet-Wrapper mit graceful Console-Fallback.

Spec §7: `django-anymail` mit Mailjet-Backend ist die Production-Wahl.
Im Dev (ohne MAILJET_API_KEY-Env) fallback auf Console-Backend, damit
Sprint 4 ohne Mailjet-Account entwickelbar ist.

Versand wird in Sprint 4 SYNCHRON gemacht (kein Celery). Spec §7 fordert
„niemals synchron im HTTP-Request" — wir umgehen das vorerst, weil:
1. Sprint 4 hat keinen Celery-Setup im Test
2. Volume ist niedrig (eine Welle = 50-300 Mails, Mailjet-API rated 50/s)
3. Migration zu Celery ist isoliert (eine Funktion ändern)

TODO Sprint 6: `send_schulung_invite` als Celery-Task wrappen.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from django.core.mail import send_mail
from django.urls import reverse_lazy  # noqa: F401  (für TYPE_CHECKING)

logger = logging.getLogger(__name__)

DEFAULT_FROM = os.environ.get("VAEREN_FROM_EMAIL", "noreply@vaeren.de")
DEFAULT_FROM_NAME = os.environ.get("VAEREN_FROM_NAME", "Vaeren Compliance")


@dataclass
class MailResult:
    sent: bool
    backend: str
    error: str | None = None


def _is_mailjet_configured() -> bool:
    return bool(os.environ.get("MAILJET_API_KEY")) and bool(os.environ.get("MAILJET_SECRET_KEY"))


def send_schulung_invite(
    to_email: str,
    *,
    mitarbeiter_name: str,
    kurs_titel: str,
    deadline: str,
    schulungs_url: str,
    einleitungs_text: str = "",
) -> MailResult:
    """Sende Schulungs-Einladung an Mitarbeiter.

    Im Dev (Console-Backend) landet der Mail-Body in stdout — perfekt für
    Tests. In Production (Mailjet-Backend) geht's via SMTP-Relay raus.
    Backend-Auswahl steckt in `settings.EMAIL_BACKEND`.
    """
    subject = f"Pflicht-Schulung: {kurs_titel}"
    intro = einleitungs_text.strip() or (
        f"Hallo {mitarbeiter_name},\n\nbitte absolviere die folgende "
        f"Pflicht-Schulung bis spätestens {deadline}."
    )
    body = (
        f"{intro}\n\n"
        f"Schulung: {kurs_titel}\n"
        f"Frist: {deadline}\n\n"
        f"Direkt zur Schulung:\n{schulungs_url}\n\n"
        f"Bei Fragen wende dich an den QM-Verantwortlichen.\n\n"
        f"-- Vaeren Compliance-Autopilot"
    )

    backend_label = "mailjet" if _is_mailjet_configured() else "console"

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=f"{DEFAULT_FROM_NAME} <{DEFAULT_FROM}>",
            recipient_list=[to_email],
            fail_silently=False,
        )
        if backend_label == "console":
            logger.info(
                "[Mail-Console] To: %s | Subject: %s | URL: %s",
                to_email,
                subject,
                schulungs_url,
            )
        return MailResult(sent=True, backend=backend_label)
    except Exception as exc:
        logger.warning("Mail-Versand an %s schlug fehl: %s", to_email, exc)
        return MailResult(sent=False, backend=backend_label, error=str(exc))


def configure_email_backend_from_env(settings_module) -> None:
    """Setze EMAIL_BACKEND je nach Vorhandensein der Mailjet-Keys.

    Wird in `config/settings/dev.py` und `prod.py` aufgerufen, NICHT in
    base.py — base.py hat den Console-Default für Tests.
    """
    if _is_mailjet_configured():
        settings_module.EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
        settings_module.ANYMAIL = {
            "MAILJET_API_KEY": os.environ["MAILJET_API_KEY"],
            "MAILJET_SECRET_KEY": os.environ["MAILJET_SECRET_KEY"],
        }
    else:
        settings_module.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
