"""Seed-Daten für ISO/IEC 42001:2023 Annex A.

Source: ISO 42001:2023 Annex A (38 Controls in 9 Kategorien A.2-A.10).

Beschreibungen sind "best-effort" deutsche Erst-Übersetzungen — werden bei
Pilot-Kunde inkrementell verfeinert. Wording lehnt sich an die Norm an, ist
aber bewusst kürzer und nicht-juristisch (RDG-Schutz).

Reihenfolge ist die Norm-Reihenfolge — UI sortiert nach (kategorie, reihenfolge).
"""

from __future__ import annotations

# Tuple-Format: (code, title_de, description_de, kategorie, reihenfolge, applicability_default)
ANNEX_A_CONTROLS: list[tuple[str, str, str, str, int, bool]] = [
    # ===== A.2 Policies related to AI =====
    (
        "A.2.2",
        "KI-Policy",
        "Die Organisation soll eine dokumentierte Richtlinie für die Entwicklung und/oder den Einsatz von KI-Systemen festlegen, die mit Geschäftsstrategie und Werten der Organisation in Einklang steht.",
        "a2_policies",
        1,
        True,
    ),
    (
        "A.2.3",
        "Ausrichtung an anderen organisationalen Policies",
        "Die KI-Policy soll mit bestehenden Richtlinien zu Datenschutz, Informationssicherheit, Qualität und Risikomanagement abgestimmt werden.",
        "a2_policies",
        2,
        True,
    ),
    (
        "A.2.4",
        "Review der KI-Policy",
        "Die KI-Policy soll in geplanten Intervallen und bei wesentlichen Änderungen überprüft werden, um Angemessenheit und Wirksamkeit sicherzustellen.",
        "a2_policies",
        3,
        True,
    ),
    # ===== A.3 Internal Organization =====
    (
        "A.3.2",
        "Rollen und Verantwortlichkeiten für KI",
        "Rollen und Verantwortlichkeiten zur Erreichung der KI-bezogenen Ziele sollen definiert, dokumentiert und kommuniziert werden (z. B. AI Risk Owner).",
        "a3_organization",
        1,
        True,
    ),
    (
        "A.3.3",
        "Berichterstattung über Bedenken",
        "Mechanismen sollen eingerichtet werden, über die Personen Bedenken zu KI-Systemen melden können (Whistleblower-/Incident-Pfad).",
        "a3_organization",
        2,
        True,
    ),
    # ===== A.4 Resources for AI Systems =====
    (
        "A.4.2",
        "Ressourcen-Dokumentation",
        "Die für KI-Systeme bereitgestellten Ressourcen (Personal, Tools, Datensätze, Rechenleistung) sollen dokumentiert werden.",
        "a4_resources",
        1,
        True,
    ),
    (
        "A.4.3",
        "Daten-Ressourcen",
        "Die für Training, Validierung und Betrieb von KI-Systemen benötigten Datensätze sollen identifiziert und ihre Eignung dokumentiert werden.",
        "a4_resources",
        2,
        True,
    ),
    (
        "A.4.4",
        "Tooling-Ressourcen",
        "Werkzeuge, Frameworks und Plattformen für KI-Systeme sollen erfasst und auf Eignung geprüft werden.",
        "a4_resources",
        3,
        True,
    ),
    (
        "A.4.5",
        "Kompetenz für KI-Systeme",
        "Die für den Lebenszyklus von KI-Systemen erforderlichen Kompetenzen sollen identifiziert, vorhanden oder durch Schulung erworben werden.",
        "a4_resources",
        4,
        True,
    ),
    (
        "A.4.6",
        "System- und Compute-Ressourcen",
        "Die für Entwicklung, Training und Betrieb benötigten Rechen-Ressourcen sollen erfasst, geplant und überwacht werden.",
        "a4_resources",
        5,
        False,  # eher Entwickler-relevant
    ),
    # ===== A.5 Assessing Impacts of AI Systems =====
    (
        "A.5.2",
        "Impact Assessment Prozess",
        "Ein dokumentierter Prozess für die Bewertung der Auswirkungen von KI-Systemen auf Personen, Gruppen und Gesellschaft soll etabliert werden.",
        "a5_impact",
        1,
        True,
    ),
    (
        "A.5.3",
        "Dokumentation des Impact Assessments",
        "Die Ergebnisse der Impact Assessments sollen dokumentiert, regelmäßig aktualisiert und betroffenen Stakeholdern kommuniziert werden.",
        "a5_impact",
        2,
        True,
    ),
    (
        "A.5.4",
        "Bewertung der Auswirkungen auf Personen/Gruppen",
        "Auswirkungen auf einzelne Personen und identifizierte Gruppen (inkl. vulnerabler Gruppen) sollen explizit bewertet werden.",
        "a5_impact",
        3,
        True,
    ),
    (
        "A.5.5",
        "Bewertung gesellschaftlicher Auswirkungen",
        "Breitere gesellschaftliche, ökonomische und umweltbezogene Auswirkungen sollen berücksichtigt werden.",
        "a5_impact",
        4,
        True,
    ),
    # ===== A.6 AI System Life Cycle =====
    (
        "A.6.1.2",
        "Ziele für verantwortungsvolle KI-Entwicklung",
        "Ziele für eine verantwortungsvolle Entwicklung/Beschaffung von KI-Systemen sollen definiert und in den Lebenszyklus integriert werden.",
        "a6_lifecycle",
        1,
        True,
    ),
    (
        "A.6.1.3",
        "Prozesse für verantwortungsvolle KI-Entwicklung",
        "Dokumentierte Prozesse sollen die Erreichung dieser Ziele über den gesamten Lebenszyklus unterstützen.",
        "a6_lifecycle",
        2,
        True,
    ),
    (
        "A.6.2.2",
        "Anforderungen und Spezifikation",
        "Funktionale und nicht-funktionale Anforderungen an KI-Systeme sollen dokumentiert werden, inkl. Performance- und Robustheits-Kriterien.",
        "a6_lifecycle",
        3,
        True,
    ),
    (
        "A.6.2.3",
        "Dokumentation von Design und Entwicklung",
        "Design-Entscheidungen, Modell-Architektur und Entwicklungsschritte sollen nachvollziehbar dokumentiert werden.",
        "a6_lifecycle",
        4,
        False,  # Entwickler-Pflicht; Deployer typischerweise N/A
    ),
    (
        "A.6.2.4",
        "Verifikation und Validierung",
        "KI-Systeme sollen vor Einsatz verifiziert und validiert werden (Performance, Bias, Robustheit, Sicherheit).",
        "a6_lifecycle",
        5,
        True,
    ),
    (
        "A.6.2.5",
        "Deployment",
        "Ein dokumentierter Prozess für die Einführung von KI-Systemen in die Produktivumgebung soll etabliert werden.",
        "a6_lifecycle",
        6,
        True,
    ),
    (
        "A.6.2.6",
        "Operation und Monitoring",
        "Im Betrieb sollen KI-Systeme kontinuierlich auf Performance, Drift und Auffälligkeiten überwacht werden.",
        "a6_lifecycle",
        7,
        True,
    ),
    (
        "A.6.2.7",
        "Technische Dokumentation",
        "Eine aktuelle technische Dokumentation der eingesetzten KI-Systeme soll vorgehalten werden.",
        "a6_lifecycle",
        8,
        True,
    ),
    (
        "A.6.2.8",
        "Aufzeichnung und Logging",
        "Geeignete Logs und Aufzeichnungen sollen das Audit und die Nachvollziehbarkeit von KI-System-Aktivitäten ermöglichen.",
        "a6_lifecycle",
        9,
        True,
    ),
    # ===== A.7 Data for AI Systems =====
    (
        "A.7.2",
        "Daten für KI-Entwicklung und -Erweiterung",
        "Datenanforderungen für die KI-Systeme sollen erhoben und dokumentiert werden.",
        "a7_data",
        1,
        True,
    ),
    (
        "A.7.3",
        "Erfassung von Daten",
        "Datenerfassungsprozesse sollen die Eignung, Aktualität und rechtmäßige Herkunft der Daten sicherstellen.",
        "a7_data",
        2,
        True,
    ),
    (
        "A.7.4",
        "Datenqualität für KI-Systeme",
        "Datenqualität (Vollständigkeit, Konsistenz, Repräsentativität) soll dokumentiert und überprüft werden.",
        "a7_data",
        3,
        True,
    ),
    (
        "A.7.5",
        "Datenherkunft",
        "Die Herkunft (Provenance) der für Training und Validierung verwendeten Datensätze soll nachvollziehbar sein.",
        "a7_data",
        4,
        True,
    ),
    (
        "A.7.6",
        "Datenvorbereitung",
        "Datenvorbereitungs-Schritte (Filterung, Labeling, Normalisierung) sollen dokumentiert werden.",
        "a7_data",
        5,
        False,
    ),
    # ===== A.8 Information for Interested Parties =====
    (
        "A.8.2",
        "Systeminformationen für Nutzer",
        "Nutzer von KI-Systemen sollen Informationen zur Funktionsweise, zu Grenzen und zur korrekten Verwendung erhalten (Transparenz).",
        "a8_information",
        1,
        True,
    ),
    (
        "A.8.3",
        "Externe Berichterstattung",
        "Externe Stakeholder sollen über für sie relevante Aspekte der eingesetzten KI-Systeme informiert werden können.",
        "a8_information",
        2,
        True,
    ),
    (
        "A.8.4",
        "Kommunikation von Vorfällen",
        "Ein Kommunikationsprozess für KI-bezogene Vorfälle gegenüber Betroffenen und Behörden soll etabliert werden.",
        "a8_information",
        3,
        True,
    ),
    (
        "A.8.5",
        "Informationen für betroffene Personen",
        "Personen, die durch KI-Outputs beeinflusst werden, sollen geeignete Informationen erhalten.",
        "a8_information",
        4,
        True,
    ),
    # ===== A.9 Use of AI Systems =====
    (
        "A.9.2",
        "Zweck-konforme Nutzung",
        "Es soll sichergestellt werden, dass KI-Systeme entsprechend ihrer dokumentierten Zwecke eingesetzt werden.",
        "a9_use",
        1,
        True,
    ),
    (
        "A.9.3",
        "Verantwortlicher Einsatz",
        "Der Einsatz von KI-Systemen soll die Werte und Verpflichtungen der Organisation berücksichtigen (Akzeptable-Nutzung-Policy).",
        "a9_use",
        2,
        True,
    ),
    (
        "A.9.4",
        "Menschliche Aufsicht",
        "KI-Systeme sollen so eingesetzt werden, dass eine angemessene menschliche Aufsicht und Eingriffsmöglichkeit gewährleistet ist.",
        "a9_use",
        3,
        True,
    ),
    # ===== A.10 Third-Party Relationships =====
    (
        "A.10.2",
        "Zuweisung von Verantwortlichkeiten Drittpartei",
        "Verantwortlichkeiten zwischen Organisation und KI-Drittanbietern sollen klar zugewiesen werden.",
        "a10_third_party",
        1,
        True,
    ),
    (
        "A.10.3",
        "Lieferanten",
        "KI-Lieferanten sollen anhand definierter Kriterien geprüft und überwacht werden (AVV, Zertifizierungen, Sicherheit).",
        "a10_third_party",
        2,
        True,
    ),
    (
        "A.10.4",
        "Kunden",
        "Kunden, denen KI-Systeme bereitgestellt werden, sollen über Eigenschaften, Grenzen und Verantwortlichkeiten informiert werden.",
        "a10_third_party",
        3,
        False,  # nur für KI-Anbieter
    ),
]


def get_seed_controls() -> list[dict]:
    """Liefert Liste der Annex-A-Controls als Dicts (für RunPython-Migration)."""
    return [
        {
            "code": code,
            "title_de": title,
            "description_de": description,
            "kategorie": kategorie,
            "reihenfolge": reihenfolge,
            "applicability_default": applicability,
        }
        for code, title, description, kategorie, reihenfolge, applicability in ANNEX_A_CONTROLS
    ]
