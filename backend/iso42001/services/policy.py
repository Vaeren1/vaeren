"""Services rund um AiPolicy + AiPolicyKenntnisnahme."""

from __future__ import annotations

import datetime

from django.core.exceptions import PermissionDenied
from django.db import transaction

from iso42001.models import (
    AiPolicy,
    AiPolicyGeltungsbereich,
    AiPolicyKenntnisnahme,
)


# Standard-Policy-Templates (Plan-Schritt 7).
POLICY_TEMPLATES: dict[str, dict[str, str]] = {
    "allgemein": {
        "geltungsbereich": AiPolicyGeltungsbereich.ALLGEMEIN,
        "titel": "Allgemeine KI-Policy",
        "inhalt_markdown": (
            "# Allgemeine KI-Policy\n\n"
            "## 1. Zweck und Geltungsbereich\n\n"
            "Diese Richtlinie beschreibt den verantwortungsvollen Einsatz von KI-Systemen"
            " in der Organisation. Sie gilt für alle Mitarbeitenden und externe Personen,"
            " die KI-Systeme im Auftrag der Organisation nutzen.\n\n"
            "## 2. Grundsätze\n\n"
            "- KI-Systeme werden nur eingesetzt, wenn ihr Zweck dokumentiert und genehmigt ist.\n"
            "- Die Nutzung erfolgt unter menschlicher Aufsicht (Art. 14 AI Act).\n"
            "- Personenbezogene Daten dürfen nur DSGVO-konform verarbeitet werden.\n"
            "- KI-Outputs gelten als Vorschläge, nicht als finale Entscheidung.\n\n"
            "## 3. Rollen und Verantwortlichkeiten\n\n"
            "Der/Die KI-Beauftragte ist verantwortlich für die Pflege des KI-Inventars und"
            " die Durchführung von Impact Assessments.\n\n"
            "## 4. Vorfall-Meldung\n\n"
            "Auffälligkeiten (Bias, Fehlausgaben, Datenverluste) sind unverzüglich über das"
            " Vaeren-Incident-Modul zu melden.\n\n"
            "## 5. Review\n\n"
            "Diese Policy wird jährlich überprüft.\n"
        ),
    },
    "akzeptable_nutzung": {
        "geltungsbereich": AiPolicyGeltungsbereich.AKZEPTABLE_NUTZUNG,
        "titel": "Akzeptable Nutzung von KI-Systemen",
        "inhalt_markdown": (
            "# Akzeptable Nutzung von KI-Systemen\n\n"
            "## 1. Erlaubte Nutzungen\n\n"
            "- Recherche und Textentwurf für interne Zwecke\n"
            "- Übersetzung allgemein zugänglicher Inhalte\n"
            "- Code-Review und Bugfix-Vorschläge\n\n"
            "## 2. Eingeschränkte Nutzungen\n\n"
            "- Eingabe personenbezogener Daten nur in freigegebenen Tools mit AVV.\n"
            "- Geschäftsgeheimnisse oder Kundendaten dürfen nicht in öffentliche KI-Dienste eingegeben werden.\n\n"
            "## 3. Verbotene Nutzungen\n\n"
            "- Automatisiertes Erstellen von Bewerber-Bewertungen ohne menschliche Prüfung\n"
            "- Erzeugung von Deepfakes oder irreführenden Inhalten\n"
            "- Umgehen von Sicherheits- oder Compliance-Kontrollen\n\n"
            "## 4. Meldepflichten\n\n"
            "Verstöße sind über die Compliance-Stelle zu melden.\n"
        ),
    },
    "incident": {
        "geltungsbereich": AiPolicyGeltungsbereich.INCIDENT,
        "titel": "KI-Vorfall-Management-Policy",
        "inhalt_markdown": (
            "# KI-Vorfall-Management-Policy\n\n"
            "## 1. Was ist ein KI-Vorfall?\n\n"
            "Ein KI-Vorfall liegt vor, wenn ein KI-System Schaden verursacht, fehlerhafte"
            " Outputs liefert, Bias zeigt, Daten preisgibt oder missbräuchlich genutzt wird.\n\n"
            "## 2. Sofortmaßnahmen\n\n"
            "- KI-System pausieren, falls Schaden droht.\n"
            "- Vorfall im Vaeren-Modul `Incidents` dokumentieren.\n"
            "- Bei personenbezogenen Daten: 72-h-Frist nach Art. 33 DSGVO prüfen.\n\n"
            "## 3. Eskalationswege\n\n"
            "- Niedrig/Mittel: KI-Beauftragte:r dokumentiert + plant Korrektur.\n"
            "- Hoch/Kritisch: Geschäftsführung wird unverzüglich informiert; Behördenmeldung prüfen.\n\n"
            "## 4. Nachbetrachtung\n\n"
            "Jeder Vorfall wird in der nächsten Management-Review besprochen.\n"
        ),
    },
}


def policy_template_kopieren(
    *, user, template_slug: str, autor_mitarbeiter=None
) -> AiPolicy:
    """Erzeugt eine neue Entwurfs-Policy aus einem Template."""
    if template_slug not in POLICY_TEMPLATES:
        raise ValueError(f"Unbekanntes Template: {template_slug}")
    tpl = POLICY_TEMPLATES[template_slug]
    return AiPolicy.objects.create(
        geltungsbereich=tpl["geltungsbereich"],
        titel=tpl["titel"],
        inhalt_markdown=tpl["inhalt_markdown"],
        version=1,
        aktiv=False,
        erstellt_von=user if user and user.is_authenticated else None,
    )


@transaction.atomic
def policy_neue_version_anlegen(
    *, user, parent_policy: AiPolicy, neue_felder: dict
) -> AiPolicy:
    """Legt neue Version an. Alte bleibt erhalten, wird auf aktiv=False gesetzt."""
    inhalt = neue_felder.get("inhalt_markdown", parent_policy.inhalt_markdown)
    titel = neue_felder.get("titel", parent_policy.titel)
    neue = AiPolicy.objects.create(
        geltungsbereich=parent_policy.geltungsbereich,
        titel=titel,
        inhalt_markdown=inhalt,
        version=parent_policy.version + 1,
        parent=parent_policy,
        aktiv=False,
        erstellt_von=user if user and user.is_authenticated else None,
    )
    # Bei Versionierung wird die alte Policy automatisch inaktiv (sie wird durch
    # die neue ersetzt sobald diese ratifiziert ist). Wir setzen aktiv=False
    # bereits jetzt, damit es keine zwei aktive Versionen geben kann.
    if parent_policy.aktiv:
        parent_policy.aktiv = False
        parent_policy.save(update_fields=["aktiv"])
    return neue


@transaction.atomic
def policy_ratifizieren(*, user, policy: AiPolicy, mitarbeiter=None) -> AiPolicy:
    """Setzt Policy aktiv. Nur GF (Permission-Check)."""
    import rules

    if not rules.test_rule("can_ratify_ai_policy", user):
        raise PermissionDenied("Nur die Geschäftsführung kann Policies ratifizieren.")

    # Alte aktive Versionen desselben Geltungsbereichs deaktivieren.
    AiPolicy.objects.filter(
        geltungsbereich=policy.geltungsbereich, aktiv=True
    ).exclude(pk=policy.pk).update(aktiv=False)

    policy.aktiv = True
    policy.ratified_at = datetime.date.today()
    policy.ratified_by = mitarbeiter
    policy.save(update_fields=["aktiv", "ratified_at", "ratified_by"])
    return policy


def kenntnisnahme_abgeben(*, mitarbeiter, policy: AiPolicy) -> AiPolicyKenntnisnahme:
    """Mitarbeiter bestätigt Kenntnisnahme. Idempotent."""
    obj, _ = AiPolicyKenntnisnahme.objects.get_or_create(
        policy=policy, mitarbeiter=mitarbeiter
    )
    return obj
