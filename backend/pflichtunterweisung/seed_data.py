"""Standard-Schulungskatalog für Vaeren (20 Pflichtkurse Industrie-Mittelstand).

Wird vom Management-Command `seed_kurs_katalog` konsumiert. Keine
Imports von Django-Models hier — reines Daten-Modul, damit auch ohne
DB-Bootstrap importierbar (für Tests/Doku-Tooling).

Abgedeckt sind die gesetzlich vorgeschriebenen jährlichen Unterweisungen
(ArbSchG, GefStoffV, BetrSichV) plus Querschnitt-Compliance
(DSGVO, HinSchG, AGG, LkSG, GwG, Antikorruption, Exportkontrolle) und
branchen-spezifische Industriethemen (Maschinen, Schweißen, Lärm,
Gabelstapler, PSA, Brandschutz).

Inhalte sind als "best knowledge"-Erstfassung formuliert — Pilot-Kunden
sollen sie vor Live-Schaltung redaktionell prüfen (RDG-Schutz).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptionDef:
    text: str
    korrekt: bool = False


@dataclass(frozen=True)
class FrageDef:
    text: str
    erklaerung: str
    optionen: tuple[OptionDef, ...]


@dataclass(frozen=True)
class ModulDef:
    titel: str
    inhalt_md: str


@dataclass(frozen=True)
class KursDef:
    titel: str
    beschreibung: str
    gueltigkeit_monate: int = 12
    min_richtig_prozent: int = 80
    module: tuple[ModulDef, ...] = field(default_factory=tuple)
    fragen: tuple[FrageDef, ...] = field(default_factory=tuple)


# Helper for shorter literals in the long catalog below.
def _opts(*pairs: tuple[str, bool]) -> tuple[OptionDef, ...]:
    return tuple(OptionDef(text=t, korrekt=k) for t, k in pairs)


# ============================================================================
# KATALOG — 20 Pflicht-/Standardkurse für Industrie-Mittelstand
# ============================================================================

KATALOG: tuple[KursDef, ...] = (
    # ------------------------------------------------------------------- #1
    KursDef(
        titel="DSGVO-Grundlagen",
        beschreibung="Datenschutz-Pflichtschulung nach Art. 39 DSGVO + § 26 BDSG. "
        "Grundbegriffe, Betroffenenrechte, Umgang mit Datenpannen, technisch-"
        "organisatorische Maßnahmen (TOMs).",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Grundbegriffe & Schutzziele",
                inhalt_md=(
                    "## Was ist die DSGVO?\n\n"
                    "Die EU-Datenschutz-Grundverordnung (DSGVO) regelt seit 25.05.2018 "
                    "den Umgang mit **personenbezogenen Daten** in der gesamten EU. "
                    "Ergänzt wird sie in Deutschland durch das **BDSG**.\n\n"
                    "### Schutzziele\n"
                    "- **Vertraulichkeit** — Zugriff nur für Berechtigte\n"
                    "- **Integrität** — Daten dürfen nicht unbemerkt verändert werden\n"
                    "- **Verfügbarkeit** — Daten sind bei Bedarf verfügbar\n\n"
                    "### Personenbezogene Daten\n"
                    "Alle Informationen, die eine natürliche Person identifizieren "
                    "oder identifizierbar machen (Name, E-Mail, IP-Adresse, "
                    "Personalnummer, Gesundheitsdaten …)."
                ),
            ),
            ModulDef(
                titel="Betroffenenrechte",
                inhalt_md=(
                    "## Rechte der Betroffenen (Kapitel III DSGVO)\n\n"
                    "- **Auskunft** (Art. 15) — welche Daten werden zu mir verarbeitet?\n"
                    "- **Berichtigung** (Art. 16)\n"
                    "- **Löschung / Recht auf Vergessenwerden** (Art. 17)\n"
                    "- **Einschränkung der Verarbeitung** (Art. 18)\n"
                    "- **Datenübertragbarkeit** (Art. 20)\n"
                    "- **Widerspruch** (Art. 21)\n\n"
                    "**Frist:** Antrag muss spätestens nach **1 Monat** beantwortet werden, "
                    "in komplexen Fällen verlängerbar um 2 Monate (mit Begründung)."
                ),
            ),
            ModulDef(
                titel="Datenpannen erkennen und melden",
                inhalt_md=(
                    "## Was ist eine Datenpanne (Data Breach)?\n\n"
                    "Jede Verletzung der Schutzziele Vertraulichkeit, Integrität oder "
                    "Verfügbarkeit personenbezogener Daten — z. B.:\n"
                    "- Verlorenes Notebook ohne Festplattenverschlüsselung\n"
                    "- Fehlversand einer E-Mail mit Personaldaten\n"
                    "- Ransomware-Befall\n"
                    "- Diebstahl von Akten/Servern\n\n"
                    "## Meldepflicht\n\n"
                    "**72 Stunden** ab Kenntnis an die Aufsichtsbehörde (Art. 33), "
                    "wenn ein Risiko für Betroffene besteht. **Sofort** an den "
                    "Datenschutzbeauftragten melden — keine Eigeneinschätzung ob "
                    "'wichtig genug'."
                ),
            ),
            ModulDef(
                titel="Technisch-organisatorische Maßnahmen (TOMs)",
                inhalt_md=(
                    "## Art. 32 DSGVO — Sicherheit der Verarbeitung\n\n"
                    "### Technisch\n"
                    "- Verschlüsselung (at-rest + in-transit)\n"
                    "- Pseudonymisierung wo möglich\n"
                    "- Zugriffskontrolle, MFA\n"
                    "- Backup + Wiederherstellungs-Tests\n\n"
                    "### Organisatorisch\n"
                    "- Schulungen, Vertraulichkeitsverpflichtung der Mitarbeiter\n"
                    "- Berechtigungskonzept (Least-Privilege)\n"
                    "- Auftragsverarbeitungsverträge (AV-Verträge) mit Dienstleistern\n"
                    "- Löschkonzept\n\n"
                    "**Praktisch:** Daten am Arbeitsplatz nie unverschlüsselt herumliegen "
                    "lassen, Bildschirm beim Verlassen sperren (Win+L), USB-Sticks nur "
                    "geprüft anschließen."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was sind personenbezogene Daten im Sinne der DSGVO?",
                erklaerung="Bereits eine einzelne ID-Nummer oder IP-Adresse genügt, "
                "wenn sie eine Identifikation ermöglicht.",
                optionen=_opts(
                    ("Alle Informationen, die eine natürliche Person identifizieren oder identifizierbar machen", True),
                    ("Nur Name, Adresse und Geburtsdatum", False),
                    ("Nur Daten, die in Datenbanken gespeichert sind", False),
                    ("Daten von Unternehmen (juristische Personen)", False),
                ),
            ),
            FrageDef(
                text="Innerhalb welcher Frist muss eine Datenpanne an die Aufsichtsbehörde gemeldet werden?",
                erklaerung="Art. 33 DSGVO: spätestens 72 Stunden ab Kenntnis, wenn ein "
                "Risiko für Betroffene besteht.",
                optionen=_opts(
                    ("Sofort, spätestens 24 Stunden", False),
                    ("72 Stunden ab Kenntnis", True),
                    ("Innerhalb von 7 Tagen", False),
                    ("Innerhalb von 4 Wochen", False),
                ),
            ),
            FrageDef(
                text="Welches dieser Beispiele ist KEINE Datenpanne?",
                erklaerung="Eine verschlüsselte E-Mail an die richtige Empfängerin ist "
                "der bestimmungsgemäße Vorgang.",
                optionen=_opts(
                    ("Eine verschlüsselte E-Mail an die richtige Empfängerin", True),
                    ("Verlorenes Notebook ohne Festplattenverschlüsselung", False),
                    ("Ransomware-Befall im Personalsystem", False),
                    ("Fehlversand der Gehaltsliste an einen falschen Verteiler", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet das 'Recht auf Vergessenwerden'?",
                erklaerung="Art. 17 DSGVO. Es gibt Ausnahmen, z. B. wenn gesetzliche "
                "Aufbewahrungspflichten dagegen stehen (Steuerrecht, HGB).",
                optionen=_opts(
                    ("Recht, die Löschung der eigenen Daten zu verlangen — mit gesetzlichen Ausnahmen", True),
                    ("Recht, anonym im Internet zu surfen", False),
                    ("Pflicht des Arbeitgebers, alle Daten nach 1 Jahr zu löschen", False),
                    ("Recht, eigene Akten aus dem Archiv mitzunehmen", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'TOM' im Datenschutzkontext?",
                erklaerung="Technisch-organisatorische Maßnahme — die Schutzvorkehrungen "
                "nach Art. 32 DSGVO.",
                optionen=_opts(
                    ("Technisch-organisatorische Maßnahme", True),
                    ("Technical Object Marker", False),
                    ("Test-Output-Modell", False),
                    ("Tagesaktuelle Online-Meldung", False),
                ),
            ),
            FrageDef(
                text="Wann darf ich personenbezogene Daten an einen externen Dienstleister weitergeben?",
                erklaerung="Auftragsverarbeitung (AV) nach Art. 28 DSGVO erfordert "
                "vertragliche Regelung VOR der Datenweitergabe.",
                optionen=_opts(
                    ("Nur mit unterzeichnetem Auftragsverarbeitungsvertrag", True),
                    ("Immer, solange der Zweck nachvollziehbar ist", False),
                    ("Wenn der Dienstleister 'vertrauenswürdig' wirkt", False),
                    ("Nie — externe Dienstleister sind grundsätzlich verboten", False),
                ),
            ),
            FrageDef(
                text="Was solltest du tun, wenn dir eine Datenpanne im Unternehmen auffällt?",
                erklaerung="Eigeneinschätzung 'ist nicht so schlimm' ist nicht zulässig — "
                "die DSB/IT prüft das Risiko.",
                optionen=_opts(
                    ("Sofort intern an Datenschutzbeauftragte/IT-Sicherheit melden", True),
                    ("Erst beobachten, ob etwas passiert", False),
                    ("Selbst entscheiden, ob es relevant ist", False),
                    ("In der Mittagspause die Kollegen fragen", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'Least-Privilege' im Berechtigungskonzept?",
                erklaerung="Mitarbeiter erhalten nur die Rechte, die für die konkrete "
                "Tätigkeit erforderlich sind.",
                optionen=_opts(
                    ("Jeder Nutzer bekommt nur die minimal notwendigen Zugriffsrechte", True),
                    ("Berechtigungen werden zentral vom CIO vergeben", False),
                    ("Privilegierte Nutzer bekommen weniger Geld", False),
                    ("Alle Mitarbeiter haben dieselben Rechte", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #2
    KursDef(
        titel="IT-Security & Phishing-Erkennung",
        beschreibung="Cyber-Security-Pflichtbasiskurs nach DSGVO Art. 32 + ISO 27001. "
        "Passwörter, MFA, Phishing-Erkennung, mobiles Arbeiten, Verhalten "
        "bei Sicherheitsvorfällen.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Passwörter & Multi-Faktor-Authentifizierung",
                inhalt_md=(
                    "## Sichere Passwörter\n\n"
                    "- **Mindestens 12 Zeichen**, besser 16+\n"
                    "- Keine Wörter aus dem Wörterbuch, keine Namen, keine Geburtsdaten\n"
                    "- Pro Dienst ein **eigenes** Passwort — niemals wiederverwenden\n"
                    "- **Passwort-Manager** verwenden (Bitwarden, 1Password, KeePass)\n\n"
                    "## MFA (Zwei-Faktor) ist Pflicht\n\n"
                    "- Aktiviere MFA überall wo angeboten — besonders bei E-Mail, "
                    "VPN, Cloud-Diensten\n"
                    "- **TOTP-App** (Microsoft Authenticator, Aegis) > SMS\n"
                    "- Recovery-Codes sicher offline verwahren"
                ),
            ),
            ModulDef(
                titel="Phishing erkennen",
                inhalt_md=(
                    "## Typische Anzeichen einer Phishing-Mail\n\n"
                    "- **Dringlichkeit** ('Ihr Konto wird in 24h gesperrt!')\n"
                    "- **Unpersönliche Anrede** ('Sehr geehrte Damen und Herren')\n"
                    "- **Fehlerhafte Absenderadresse** (paypal.support@evil.com)\n"
                    "- **Verdächtige Links** — Mauszeiger drüber halten, NICHT klicken\n"
                    "- **Anhänge** wie .zip, .exe, .docm, .xlsm\n"
                    "- **Rechtschreibfehler**, ungewöhnlicher Sprachstil\n\n"
                    "## Spear-Phishing & CEO-Fraud\n\n"
                    "Gezielte Mails, die vorgeben vom CEO oder einem Kollegen zu kommen "
                    "und Überweisungen oder Datenherausgabe verlangen. **Bei Geldforderungen "
                    "immer telefonisch rückbestätigen** (über bekannte Nummer, nicht aus "
                    "der Mail)."
                ),
            ),
            ModulDef(
                titel="Mobiles Arbeiten & BYOD",
                inhalt_md=(
                    "## Außerhalb des Büros\n\n"
                    "- **VPN aktivieren** bei jeder externen Verbindung\n"
                    "- Kein **offenes WLAN** (Café, Hotel, Bahn) ohne VPN\n"
                    "- **Blickschutzfolie** im Zug/Café\n"
                    "- Notebook beim Verlassen nicht unbeaufsichtigt lassen\n\n"
                    "## Eigene Geräte (BYOD)\n\n"
                    "- Privates Smartphone für dienstliche E-Mails: nur mit MDM-Profil\n"
                    "- App-Berechtigungen prüfen — keine Taschenlampen-App mit Kontaktzugriff\n"
                    "- Bei Verlust: SOFORT melden, Remote-Wipe wird ausgelöst"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Passwort-Praxis ist empfehlenswert?",
                erklaerung="Wiederverwendung ist das größte Risiko: ein geleaktes Passwort "
                "öffnet sonst viele Konten gleichzeitig.",
                optionen=_opts(
                    ("Für jeden Dienst ein eigenes Passwort, verwaltet im Passwort-Manager", True),
                    ("Ein starkes Passwort, das für alle wichtigen Dienste verwendet wird", False),
                    ("Passwörter auf einem Post-it am Bildschirm", False),
                    ("Geburtsdatum + Initialen — leicht zu merken", False),
                ),
            ),
            FrageDef(
                text="Was ist der sicherste zweite Faktor?",
                erklaerung="SMS-OTPs sind durch SIM-Swap-Angriffe kompromittierbar; "
                "Hardware-Token (FIDO2) und TOTP-Apps sind deutlich sicherer.",
                optionen=_opts(
                    ("Hardware-Token (YubiKey) oder TOTP-App", True),
                    ("SMS-Code", False),
                    ("Geheimfrage 'Mädchenname der Mutter'", False),
                    ("PIN per E-Mail", False),
                ),
            ),
            FrageDef(
                text="Eine E-Mail von 'IT-Support' fordert dich auf, deine Zugangsdaten über einen Link zu bestätigen. Was tust du?",
                erklaerung="Echte IT-Abteilungen fragen niemals per E-Mail nach Passwörtern. "
                "Bei Unsicherheit telefonisch rückfragen.",
                optionen=_opts(
                    ("Mail an IT-Sicherheit weiterleiten, NICHT klicken", True),
                    ("Auf den Link klicken und Zugangsdaten eingeben", False),
                    ("An Kollegen weiterleiten — vielleicht wissen die mehr", False),
                    ("Antworten und nachfragen, ob das echt ist", False),
                ),
            ),
            FrageDef(
                text="CEO-Fraud: Was ist das?",
                erklaerung="Auch 'Business E-Mail Compromise' (BEC) genannt. Häufig "
                "kombiniert mit Druck/Eilbedürftigkeit.",
                optionen=_opts(
                    ("Gefälschte E-Mail/Anruf, der vorgibt vom CEO zu kommen, um Überweisungen auszulösen", True),
                    ("Wenn der CEO einen Mitarbeiter beim Betrug erwischt", False),
                    ("Wenn der CEO sein Passwort vergisst", False),
                    ("Ein Excel-Macro-Virus", False),
                ),
            ),
            FrageDef(
                text="Du arbeitest im Café mit offenem WLAN. Welche Schutzmaßnahme ist unverzichtbar?",
                erklaerung="Offenes WLAN ist abhörbar. VPN verschlüsselt den gesamten "
                "Traffic Richtung Firmennetz.",
                optionen=_opts(
                    ("VPN-Verbindung aktivieren", True),
                    ("Antivirus reicht aus", False),
                    ("Inkognito-Modus im Browser", False),
                    ("Bildschirmsperre genügt", False),
                ),
            ),
            FrageDef(
                text="Du verlierst dein Diensthandy. Was tust du zuerst?",
                erklaerung="Schnelligkeit minimiert das Risiko von Datenabfluss — "
                "Remote-Wipe + Konto-Sperre brauchen IT-Aktion.",
                optionen=_opts(
                    ("Sofort die IT-Sicherheit melden, damit Remote-Wipe ausgelöst wird", True),
                    ("Erst zuhause suchen, dann morgen melden", False),
                    ("Auf Fundgegenstand warten", False),
                    ("Selber das Handy mit Find-My-iPhone löschen", False),
                ),
            ),
            FrageDef(
                text="Ein Anhang heißt 'Rechnung-Mai.pdf.exe'. Wie reagierst du?",
                erklaerung="Doppelte Dateiendungen sind ein klassisches Malware-Indiz. "
                ".exe ist eine ausführbare Datei — niemals öffnen.",
                optionen=_opts(
                    ("Mail an IT melden, Anhang nicht öffnen", True),
                    ("Öffnen — Rechnungen müssen ja geprüft werden", False),
                    ("In Outlook-Vorschau anschauen — das ist ja noch nicht 'ausführen'", False),
                    ("Antivirus drüber laufen lassen, dann öffnen", False),
                ),
            ),
            FrageDef(
                text="Wie erkennst du eine Phishing-Mail meist am schnellsten?",
                erklaerung="Dringlichkeit + ungewöhnliche Absenderadresse sind die "
                "stärksten Indikatoren, oft kombiniert mit unpersönlicher Anrede.",
                optionen=_opts(
                    ("Dringlichkeit, fremde Absenderadresse, unpersönliche Anrede", True),
                    ("Sie kommt immer zur Mittagspause", False),
                    ("Sie ist immer auf Englisch", False),
                    ("Sie hat ein Microsoft-Logo", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #3
    KursDef(
        titel="Arbeitsschutz — Grundunterweisung",
        beschreibung="Jährliche Pflichtunterweisung nach § 12 ArbSchG. "
        "Gefährdungsbeurteilung, Unterweisungspflichten, Notfallorganisation.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Verantwortung & Pflichten",
                inhalt_md=(
                    "## Wer ist verantwortlich?\n\n"
                    "Nach § 3 ArbSchG ist der Arbeitgeber für den Arbeitsschutz "
                    "**rechtlich** verantwortlich, kann Aufgaben aber an Führungskräfte "
                    "und Fachkräfte für Arbeitssicherheit (Sifa) delegieren.\n\n"
                    "## Pflichten der Beschäftigten (§ 15-16 ArbSchG)\n"
                    "- Schutzmaßnahmen befolgen\n"
                    "- Eigene Sicherheit und die anderer nicht gefährden\n"
                    "- **Gefahren melden**, sobald sie erkannt werden\n"
                    "- Mangel an Schutzeinrichtungen melden\n"
                    "- Arbeitsmedizinische Untersuchungen ermöglichen"
                ),
            ),
            ModulDef(
                titel="Gefährdungsbeurteilung",
                inhalt_md=(
                    "## Was ist die GBU?\n\n"
                    "Schriftliche Bewertung aller Gefährdungen am Arbeitsplatz — "
                    "Pflicht nach § 5 ArbSchG. Sie ist die Grundlage für jede "
                    "Schutzmaßnahme.\n\n"
                    "## Typische Gefährdungen in der Produktion\n"
                    "- Mechanisch (rotierende Teile, Schnittverletzungen)\n"
                    "- Thermisch (heiße Oberflächen, Schweißfunken)\n"
                    "- Elektrisch (Strom, Lichtbogen)\n"
                    "- Chemisch (Gefahrstoffe, Dämpfe)\n"
                    "- Physikalisch (Lärm, Vibration, Strahlung)\n"
                    "- Ergonomisch (Heben/Tragen, Bildschirmarbeit)\n"
                    "- Psychisch (Zeitdruck, Schichtarbeit)\n\n"
                    "**Bei Veränderung** (neue Maschine, neuer Prozess) muss die "
                    "GBU aktualisiert werden — VOR Aufnahme der Tätigkeit."
                ),
            ),
            ModulDef(
                titel="Notfallorganisation",
                inhalt_md=(
                    "## Im Notfall\n\n"
                    "1. **Eigenschutz** — niemals als Held auftreten\n"
                    "2. **Notruf 112** absetzen (5 W: Wo / Was / Wieviele / Welche "
                    "Verletzungen / Warten auf Rückfragen)\n"
                    "3. **Erste Hilfe** leisten — innerhalb der eigenen Möglichkeiten\n"
                    "4. **Unfall melden** an Vorgesetzte/n + Sicherheitsfachkraft\n\n"
                    "## Meldepflichten an die BG\n"
                    "- Bei Arbeitsunfähigkeit > 3 Tage: Unfallanzeige innerhalb 3 Tagen\n"
                    "- Tödlicher Unfall: sofort\n\n"
                    "## Verbandbuch\n"
                    "Auch Bagatell-Verletzungen MÜSSEN ins Verbandbuch — wichtig für "
                    "BG-Anerkennung bei Spätfolgen."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wer ist nach § 3 ArbSchG für den Arbeitsschutz im Betrieb rechtlich verantwortlich?",
                erklaerung="Der Arbeitgeber. Er kann delegieren, aber die rechtliche "
                "Letzt-Verantwortung bleibt bei ihm.",
                optionen=_opts(
                    ("Der Arbeitgeber", True),
                    ("Die Sicherheitsfachkraft (Sifa)", False),
                    ("Der Betriebsrat", False),
                    ("Jeder Beschäftigte für sich selbst", False),
                ),
            ),
            FrageDef(
                text="Was ist die zentrale Pflicht der Beschäftigten nach § 15-16 ArbSchG?",
                erklaerung="Aktive Mitwirkung: Maßnahmen befolgen UND Gefahren melden.",
                optionen=_opts(
                    ("Schutzmaßnahmen befolgen und erkannte Gefahren melden", True),
                    ("Eigene Schutzmaßnahmen erfinden", False),
                    ("Den Betriebsrat informieren — sonst nichts", False),
                    ("Nur, was im Arbeitsvertrag steht", False),
                ),
            ),
            FrageDef(
                text="Wann muss die Gefährdungsbeurteilung aktualisiert werden?",
                erklaerung="Bei jeder relevanten Veränderung — neuer Stoff, neue Maschine, "
                "geänderter Prozess. Auch nach Unfällen.",
                optionen=_opts(
                    ("Bei neuen Maschinen/Prozessen oder nach Unfällen, VOR Aufnahme der Tätigkeit", True),
                    ("Alle 5 Jahre", False),
                    ("Nur wenn die Berufsgenossenschaft danach fragt", False),
                    ("Nie — sie wird einmal erstellt und gilt für immer", False),
                ),
            ),
            FrageDef(
                text="Welche Reihenfolge gilt im Notfall?",
                erklaerung="Eigenschutz immer zuerst — sonst kommt es zu Folgeopfern.",
                optionen=_opts(
                    ("1. Eigenschutz  2. Notruf 112  3. Erste Hilfe  4. Meldung", True),
                    ("1. Notruf  2. Eigenschutz  3. Erste Hilfe  4. Meldung", False),
                    ("1. Erste Hilfe  2. Notruf  3. Eigenschutz  4. Meldung", False),
                    ("1. Vorgesetzter informieren  2. Notruf  3. Erste Hilfe", False),
                ),
            ),
            FrageDef(
                text="Welche Bagatellverletzungen müssen ins Verbandbuch?",
                erklaerung="ALLE — auch der harmlose Schnitt. BG-relevante Spätfolgen "
                "(Tetanus, Infektionen) lassen sich nur so beweisen.",
                optionen=_opts(
                    ("Alle Verletzungen, auch kleine", True),
                    ("Nur Verletzungen mit Krankenhausbesuch", False),
                    ("Nur Verletzungen mit AU > 3 Tagen", False),
                    ("Nur Verletzungen, die ein Vorgesetzter gesehen hat", False),
                ),
            ),
            FrageDef(
                text="Welche Frist gilt für die Unfallanzeige an die BG bei AU > 3 Tagen?",
                erklaerung="DGUV Vorschrift 1 § 24: 3-Tage-Frist nach Beginn der "
                "Arbeitsunfähigkeit.",
                optionen=_opts(
                    ("3 Tage", True),
                    ("24 Stunden", False),
                    ("7 Tage", False),
                    ("30 Tage", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #4
    KursDef(
        titel="Brandschutz am Arbeitsplatz",
        beschreibung="Pflichtunterweisung nach ASR A2.2 + § 10 ArbSchG. "
        "Brandklassen, Löschmittel, Verhalten im Brandfall, Flucht- und Rettungswege.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Brandklassen & Löschmittel",
                inhalt_md=(
                    "## Brandklassen nach DIN EN 2\n\n"
                    "| Klasse | Brennstoff | Beispiel | Löschmittel |\n"
                    "|---|---|---|---|\n"
                    "| **A** | Feste Stoffe | Holz, Papier, Textil | Wasser, Schaum, ABC-Pulver |\n"
                    "| **B** | Flüssigkeiten | Benzin, Öl, Lacke | Schaum, CO₂, BC-Pulver |\n"
                    "| **C** | Gase | Propan, Erdgas | Pulver (NICHT Wasser/Schaum) |\n"
                    "| **D** | Metalle | Magnesium, Alu-Späne | Spezial-Pulver (D-Pulver) |\n"
                    "| **F** | Speisefette | Frittierfett | Fettbrand-Löscher (F-Klasse) |\n\n"
                    "⚠️ **Niemals Wasser auf Fettbrand** — Explosionsartige Verdampfung!"
                ),
            ),
            ModulDef(
                titel="Verhalten im Brandfall",
                inhalt_md=(
                    "## Reihenfolge\n\n"
                    "1. **Ruhe bewahren** — kein Panik-Verhalten\n"
                    "2. **Brand melden** — Notruf 112, Brandmeldetaster betätigen\n"
                    "3. **In Sicherheit bringen** — Personen warnen, Hilflose mitnehmen\n"
                    "4. **Löschversuche** nur wenn:\n"
                    "   - Eigener Fluchtweg ist gesichert\n"
                    "   - Brand ist im Entstehungsstadium\n"
                    "   - Geeignetes Löschmittel verfügbar\n\n"
                    "## Im Brandfall NICHT\n"
                    "- Aufzug benutzen\n"
                    "- Wertgegenstände holen\n"
                    "- Türen aufreißen — Rauch saugt sich an, Stichflamme!\n"
                    "- Im Rauch aufrecht gehen — am Boden ist mehr Sauerstoff"
                ),
            ),
            ModulDef(
                titel="Flucht- und Rettungswege",
                inhalt_md=(
                    "## Anforderungen\n\n"
                    "- Stets **freigehalten** — keine Paletten, Kartons, Möbel\n"
                    "- Gekennzeichnet mit grünen Rettungszeichen (DIN 4844)\n"
                    "- Sicherheitsbeleuchtung muss bei Stromausfall 60 min leuchten\n"
                    "- Türen in Fluchtrichtung **aufschlagend**, nicht abgeschlossen "
                    "(Panikschloss)\n\n"
                    "## Sammelplatz\n"
                    "Jeder muss wissen, wo der Sammelplatz nach Evakuierung ist. "
                    "Sammelplatz-Verantwortliche zählen die Beschäftigten — "
                    "Feuerwehr erfährt sofort, ob jemand fehlt."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welches Löschmittel eignet sich NICHT für brennende Metallspäne (Klasse D)?",
                erklaerung="Wasser reagiert mit brennenden Metallen explosionsartig. "
                "Spezielles D-Pulver oder trockener Sand sind richtig.",
                optionen=_opts(
                    ("Wasser", True),
                    ("D-Pulver", False),
                    ("Trockener Sand", False),
                    ("Spezial-Trockenlöschmittel", False),
                ),
            ),
            FrageDef(
                text="Du entdeckst in der Werkhalle einen Schwelbrand. Was tust du zuerst?",
                erklaerung="Reihenfolge: Ruhe → Brand melden (112) → Personen retten → "
                "ggf. Löschen.",
                optionen=_opts(
                    ("Ruhe bewahren, Notruf 112 absetzen, Personen warnen", True),
                    ("Sofort selbst löschen, dann melden", False),
                    ("Erst Vorgesetzten suchen", False),
                    ("Foto machen und Twittern", False),
                ),
            ),
            FrageDef(
                text="Was darf NICHT auf Flucht- und Rettungswegen abgestellt werden?",
                erklaerung="Fluchtwege müssen jederzeit frei sein — sonst lebensgefährlich.",
                optionen=_opts(
                    ("Nichts — sie müssen immer komplett frei sein", True),
                    ("Kleine Kartons, wenn sie schnell weggeräumt werden können", False),
                    ("Mülltonnen, solange sie nicht voll sind", False),
                    ("Schreibtische am Rand", False),
                ),
            ),
            FrageDef(
                text="Wie verhält man sich in einem stark verrauchten Flur?",
                erklaerung="Am Boden ist die Sicht besser und mehr Sauerstoff — kriechen.",
                optionen=_opts(
                    ("Geduckt oder kriechend am Boden bewegen", True),
                    ("Aufrecht und schnell laufen", False),
                    ("Atem anhalten und rennen", False),
                    ("Aufzug benutzen, das ist schneller", False),
                ),
            ),
            FrageDef(
                text="Wann darfst du selbst löschen?",
                erklaerung="Drei Bedingungen müssen alle erfüllt sein: Entstehungsbrand, "
                "Fluchtweg gesichert, geeignetes Löschmittel.",
                optionen=_opts(
                    ("Nur wenn Fluchtweg gesichert, Entstehungsbrand und passendes Löschmittel da", True),
                    ("Immer — der Schaden soll klein bleiben", False),
                    ("Nur als Brandschutzhelfer/in", False),
                    ("Nur wenn die Feuerwehr nicht erreichbar ist", False),
                ),
            ),
            FrageDef(
                text="Wozu dient der Sammelplatz?",
                erklaerung="Damit die Einsatzkräfte schnell wissen, ob noch Personen "
                "im Gebäude vermisst werden.",
                optionen=_opts(
                    ("Personen zählen — wer fehlt, wird vermisst und gesucht", True),
                    ("Ein gemütlicher Ort zum Warten", False),
                    ("Pflicht-Raucherpause für alle", False),
                    ("Ein Ort, wo die Feuerwehr ihre Schläuche abstellt", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #5
    KursDef(
        titel="Erste Hilfe — Auffrischung",
        beschreibung="Auffrischung nach DGUV Vorschrift 1 § 26. Notruf, Bewusstlosigkeit, "
        "Wiederbelebung, Wundversorgung.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Notruf-Schema 5 W",
                inhalt_md=(
                    "## Notruf 112 — die 5 W\n\n"
                    "1. **Wo** ist der Notfall?\n"
                    "2. **Was** ist passiert?\n"
                    "3. **Wieviele** Verletzte?\n"
                    "4. **Welche** Verletzungen/Erkrankungen?\n"
                    "5. **Warten** auf Rückfragen — nicht auflegen!\n\n"
                    "**Wichtig:** Niemals selbst auflegen, immer die Leitstelle "
                    "beenden lassen."
                ),
            ),
            ModulDef(
                titel="Bewusstlosigkeit & Wiederbelebung",
                inhalt_md=(
                    "## Prüfen — Rufen — Drücken\n\n"
                    "1. **Prüfen** — Ansprechen, schütteln, Atmung prüfen (max 10 s)\n"
                    "2. **Rufen** — 112 + Helfer organisieren\n"
                    "3. **Drücken** — Herzdruckmassage: Brustmitte, 5–6 cm tief, "
                    "100–120 / min, bis Rettungsdienst kommt\n\n"
                    "## Stabile Seitenlage\n"
                    "Nur wenn die Person **atmet** aber **nicht ansprechbar** ist.\n\n"
                    "## AED (Defibrillator)\n"
                    "Wenn vorhanden: sofort einschalten und Sprachanweisungen folgen — "
                    "auch ohne Vorerfahrung. AED entscheidet selbst, ob Schock nötig ist."
                ),
            ),
            ModulDef(
                titel="Wunden, Verbrennungen, Schock",
                inhalt_md=(
                    "## Starke Blutung\n"
                    "- Direkter Druck mit Verbandmaterial\n"
                    "- Druckverband — Polster auf die Wunde, fest umwickeln\n"
                    "- **Tourniquet** nur bei lebensgefährlicher Blutung an Extremitäten\n\n"
                    "## Verbrennungen\n"
                    "- **10–20 Minuten** mit lauwarmem Wasser kühlen (NICHT eiskalt)\n"
                    "- Kleidung nicht abreißen, falls sie an der Wunde klebt\n"
                    "- Keine Hausmittel (Mehl, Öl, Zahnpasta)\n\n"
                    "## Schock-Zeichen\n"
                    "- Blass, kalter Schweiß, schneller Puls, Unruhe\n"
                    "- **Maßnahmen:** Beine hochlegen (außer bei Bein/Bauch-Verletzung), "
                    "warm halten, beruhigen, kein Essen/Trinken"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was sind die 5 W beim Notruf?",
                erklaerung="Wo, Was, Wieviele, Welche Verletzungen, Warten auf Rückfragen.",
                optionen=_opts(
                    ("Wo, Was, Wieviele, Welche Verletzungen, Warten auf Rückfragen", True),
                    ("Wer, Wann, Warum, Wieso, Wohin", False),
                    ("Wache, Wagen, Wehr, Wasser, Werkzeug", False),
                    ("Es gibt nur 3 Ws", False),
                ),
            ),
            FrageDef(
                text="Mit welcher Frequenz wird die Herzdruckmassage durchgeführt?",
                erklaerung="100–120 / min — etwa Stayin' Alive-Beat.",
                optionen=_opts(
                    ("100–120 Druckpunkte pro Minute", True),
                    ("60 / min", False),
                    ("So schnell wie möglich", False),
                    ("30 / min", False),
                ),
            ),
            FrageDef(
                text="Wann legt man eine Person in die stabile Seitenlage?",
                erklaerung="Atmend aber bewusstlos — dann darf die Luftwege nicht "
                "die Zunge verlegen.",
                optionen=_opts(
                    ("Wenn sie atmet, aber nicht ansprechbar ist", True),
                    ("Wenn sie blutet", False),
                    ("Bei Wirbelsäulenverletzung sofort", False),
                    ("Bei Verbrennung am Bein", False),
                ),
            ),
            FrageDef(
                text="Wie lange wird eine Verbrennung gekühlt?",
                erklaerung="10–20 Minuten mit lauwarmem Wasser. Eiskalt kann zu "
                "Erfrierung führen.",
                optionen=_opts(
                    ("10–20 Minuten mit lauwarmem Wasser", True),
                    ("Bis kein Schmerz mehr da ist", False),
                    ("Eiskalt — je kälter desto besser", False),
                    ("Gar nicht — Pflaster reicht", False),
                ),
            ),
            FrageDef(
                text="Du findest einen AED neben dem Verletzten. Darfst du ihn benutzen?",
                erklaerung="AEDs sind für Laien gemacht. Sprachanweisungen folgen — "
                "Gerät entscheidet selbst über Schock.",
                optionen=_opts(
                    ("Ja, AEDs sind für Laien — Anweisungen befolgen", True),
                    ("Nein, nur Ärzte dürfen das", False),
                    ("Nur mit Erste-Hilfe-Schein", False),
                    ("Nur wenn der Patient zustimmt", False),
                ),
            ),
            FrageDef(
                text="Wann ist die Erste-Hilfe-Auffrischung Pflicht?",
                erklaerung="DGUV V1 § 26: Auffrischung alle 2 Jahre für betriebliche "
                "Ersthelfer.",
                optionen=_opts(
                    ("Alle 2 Jahre für betriebliche Ersthelfer", True),
                    ("Einmal pro Berufsleben", False),
                    ("Jedes Jahr", False),
                    ("Alle 5 Jahre", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #6
    KursDef(
        titel="Umgang mit Gefahrstoffen",
        beschreibung="Jährliche Pflichtunterweisung nach § 14 GefStoffV. "
        "GHS-Piktogramme, Sicherheitsdatenblätter, Lagerung, Unfallvermeidung.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="GHS-Piktogramme & H/P-Sätze",
                inhalt_md=(
                    "## Die 9 GHS-Piktogramme\n\n"
                    "- **GHS01 — Explodierende Bombe** (explosionsgefährlich)\n"
                    "- **GHS02 — Flamme** (entzündbar)\n"
                    "- **GHS03 — Flamme über Kreis** (oxidierend, brandfördernd)\n"
                    "- **GHS04 — Gasflasche** (Gase unter Druck)\n"
                    "- **GHS05 — Ätzwirkung** (auf Haut + Augen)\n"
                    "- **GHS06 — Totenkopf** (akut giftig)\n"
                    "- **GHS07 — Ausrufezeichen** (reizend, gesundheitsschädlich)\n"
                    "- **GHS08 — Gesundheitsgefahr** (CMR — krebserzeugend, "
                    "erbgutverändernd, fortpflanzungsgefährdend)\n"
                    "- **GHS09 — Umweltgefahr** (gewässergefährdend)\n\n"
                    "## H-Sätze und P-Sätze\n"
                    "- **H** (Hazard) — Gefahrenhinweis (H225 = leicht entzündbar)\n"
                    "- **P** (Precautionary) — Sicherheitshinweis (P210 = von "
                    "Hitzequellen fernhalten)"
                ),
            ),
            ModulDef(
                titel="Sicherheitsdatenblatt (SDB) lesen",
                inhalt_md=(
                    "## Die 16 Abschnitte des SDB\n\n"
                    "Pflicht-Aufbau nach REACH Anhang II. Wichtig im Alltag:\n\n"
                    "1. **Bezeichnung** + Identifikation des Lieferanten\n"
                    "2. **Mögliche Gefahren**\n"
                    "3. Zusammensetzung\n"
                    "4. **Erste-Hilfe-Maßnahmen** ← bei Unfall\n"
                    "5. **Brandbekämpfung** ← welches Löschmittel\n"
                    "6. **Unbeabsichtigte Freisetzung** ← bei Leck\n"
                    "7. Handhabung & Lagerung\n"
                    "8. **Expositionsbegrenzung & PSA**\n"
                    "9. Physikalische Eigenschaften\n"
                    "10. Stabilität & Reaktivität\n"
                    "11. Toxikologie\n"
                    "12. Ökologie\n"
                    "13. Entsorgung\n"
                    "14. Transport\n"
                    "15. Rechtsvorschriften\n"
                    "16. Sonstiges\n\n"
                    "SDB muss am Arbeitsplatz **zugänglich** sein — Papierordner "
                    "oder digital."
                ),
            ),
            ModulDef(
                titel="Lagerung & Substitution",
                inhalt_md=(
                    "## Lagergrundsätze\n\n"
                    "- **Zusammenlagerungsverbote** beachten (TRGS 510): z. B. "
                    "Säuren nicht neben Laugen, brennbar nicht neben oxidierend\n"
                    "- Kennzeichnung am Lagerort\n"
                    "- Auffangwannen für flüssige Gefahrstoffe\n"
                    "- Belüftung sicherstellen\n"
                    "- Zugang **abschließbar** bei besonders gefährlichen Stoffen\n\n"
                    "## Substitutionspflicht (§ 6 GefStoffV)\n"
                    "Vor Einsatz eines Gefahrstoffs muss geprüft werden, ob ein "
                    "**weniger gefährlicher Stoff** möglich ist. Beispiel: "
                    "Bremsenreiniger ohne Halogene statt Trichlorethylen."
                ),
            ),
            ModulDef(
                titel="Verhalten im Schadensfall",
                inhalt_md=(
                    "## Bei Hautkontakt\n"
                    "- Sofort mit reichlich Wasser spülen, 10–15 min\n"
                    "- Kontaminierte Kleidung entfernen\n"
                    "- SDB-Abschnitt 4 prüfen — manchmal NICHT abwaschen "
                    "(Calciumcarbid u. ä.)\n\n"
                    "## Bei Augenkontakt\n"
                    "- Augendusche, min. 15 min mit gespreizten Lidern\n"
                    "- Arzt aufsuchen, SDB mitnehmen\n\n"
                    "## Verschütten\n"
                    "- Atemschutz wenn nötig\n"
                    "- Mit geeignetem Bindemittel aufnehmen (KEIN Wasser)\n"
                    "- Vorgesetzte/n informieren\n\n"
                    "## Ein-/Verschlucken\n"
                    "- Mund ausspülen\n"
                    "- **NIE Erbrechen auslösen** ohne Anweisung der Giftnotruf-"
                    "zentrale (z. B. Säuren!)\n"
                    "- Giftnotruf (z. B. Berlin: 030-19240)"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was bedeutet das GHS06-Piktogramm (Totenkopf)?",
                erklaerung="Akut toxisch — schon kleine Mengen können tödlich sein.",
                optionen=_opts(
                    ("Akut giftig", True),
                    ("Reizend", False),
                    ("Umweltgefährlich", False),
                    ("Brandfördernd", False),
                ),
            ),
            FrageDef(
                text="Wo finde ich Informationen zur ersten Hilfe bei Kontakt mit einem Gefahrstoff?",
                erklaerung="Sicherheitsdatenblatt (SDB), Abschnitt 4.",
                optionen=_opts(
                    ("Im Sicherheitsdatenblatt, Abschnitt 4", True),
                    ("Auf Wikipedia", False),
                    ("Im Rezeptbuch der Werkstatt", False),
                    ("Auf der Lieferschein-Rückseite", False),
                ),
            ),
            FrageDef(
                text="Was ist die Substitutionspflicht?",
                erklaerung="§ 6 GefStoffV: vor Einsatz prüfen, ob es einen weniger "
                "gefährlichen Ersatzstoff gibt.",
                optionen=_opts(
                    ("Pflicht, weniger gefährliche Stoffe einzusetzen, sofern technisch möglich", True),
                    ("Pflicht, Gefahrstoffe regelmäßig zu erneuern", False),
                    ("Pflicht, jeden Mitarbeiter alle 2 Jahre auszutauschen", False),
                    ("Pflicht, Reststoffe zu entsorgen", False),
                ),
            ),
            FrageDef(
                text="Was tust du bei Augenkontakt mit einer Säure?",
                erklaerung="Lange spülen (min 15 min) mit Augendusche, danach immer "
                "Arzt aufsuchen.",
                optionen=_opts(
                    ("Mindestens 15 Minuten mit Augendusche spülen und Arzt aufsuchen", True),
                    ("Kurz mit Toilettenpapier abtupfen", False),
                    ("Mit Lauge neutralisieren", False),
                    ("Augen schließen und abwarten", False),
                ),
            ),
            FrageDef(
                text="Welche Stoffe dürfen NICHT zusammen gelagert werden?",
                erklaerung="TRGS 510: Säuren + Laugen, brennbar + oxidierend, "
                "giftig + Lebensmittel etc.",
                optionen=_opts(
                    ("Säuren und Laugen / brennbare und oxidierende Stoffe", True),
                    ("Wasser und Öl", False),
                    ("Alle festen Stoffe mit allen flüssigen", False),
                    ("Es gibt keine Zusammenlagerungsverbote", False),
                ),
            ),
            FrageDef(
                text="Wie oft muss die Gefahrstoff-Unterweisung wiederholt werden?",
                erklaerung="§ 14 GefStoffV: mindestens jährlich, vor Aufnahme der Tätigkeit "
                "und bei Veränderungen.",
                optionen=_opts(
                    ("Mindestens jährlich", True),
                    ("Einmal beim Eintritt — dann nie wieder", False),
                    ("Alle 3 Jahre", False),
                    ("Nur wenn der Arbeitgeber Lust hat", False),
                ),
            ),
            FrageDef(
                text="Was solltest du NIE tun, wenn jemand einen Gefahrstoff verschluckt hat?",
                erklaerung="Bei Säuren/Laugen würde Erbrechen die Speiseröhre erneut "
                "verätzen — immer Giftnotruf fragen.",
                optionen=_opts(
                    ("Ohne Anweisung Erbrechen auslösen", True),
                    ("Giftnotruf anrufen", False),
                    ("SDB-Abschnitt 4 lesen", False),
                    ("Mund mit Wasser ausspülen", False),
                ),
            ),
            FrageDef(
                text="Was bedeuten 'H-Sätze' im SDB?",
                erklaerung="H = Hazard = Gefahrenhinweis. P = Precautionary = Sicherheits"
                "hinweis.",
                optionen=_opts(
                    ("Gefahrenhinweise (Hazard Statements)", True),
                    ("Herstellerangaben", False),
                    ("Häufigkeit der Anwendung", False),
                    ("Hilfestellung in Notfällen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #7
    KursDef(
        titel="Persönliche Schutzausrüstung (PSA)",
        beschreibung="Unterweisung nach PSA-Benutzungsverordnung. Auswahl, Tragepflicht, "
        "Prüfung & Wartung, Atemschutz.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Auswahl & Tragepflicht",
                inhalt_md=(
                    "## TOP-Prinzip\n\n"
                    "Schutzmaßnahmen-Reihenfolge nach ArbSchG:\n"
                    "1. **T**echnisch (Abschirmung, Kapselung)\n"
                    "2. **O**rganisatorisch (Abläufe, Trennung Bereiche)\n"
                    "3. **P**ersönlich (PSA als letzte Linie)\n\n"
                    "## Typen\n"
                    "- **Kopf** — Schutzhelm bei Anstoß-/Aufprallgefahr\n"
                    "- **Augen** — Schutzbrille bei Funken, Splittern, Strahlung\n"
                    "- **Gehör** — Stöpsel, Kapsel ab 80 dB(A)\n"
                    "- **Atemwege** — Filtermaske oder umluftunabhängig\n"
                    "- **Hand** — Schnitt-, Hitze-, Chemikalienschutz (Material!)\n"
                    "- **Fuß** — S1/S2/S3 Sicherheitsschuh mit Stahlkappe\n"
                    "- **Körper** — Warnweste, Hitzeschutz, Säureschutzanzug\n\n"
                    "## Tragepflicht\n"
                    "Wo PSA-Pflicht ausgeschildert ist (Piktogramme nach DIN EN ISO 7010), "
                    "MUSS PSA getragen werden — auch für 'nur 5 Sekunden'."
                ),
            ),
            ModulDef(
                titel="Prüfung & Wartung",
                inhalt_md=(
                    "## Vor jeder Nutzung\n"
                    "- Sichtprüfung auf Risse, Verschleiß, Verformung\n"
                    "- Helm: Riss in Schale → austauschen\n"
                    "- Brille: Kratzer, lose Bügel → tauschen\n"
                    "- Handschuh: Loch, Versteifung → tauschen\n\n"
                    "## Wiederkehrende Prüfung\n"
                    "- Helm: alle 4–5 Jahre tauschen (UV-Versprödung)\n"
                    "- Auffanggurt: jährliche Sachkundigen-Prüfung\n"
                    "- Atemschutzgerät: jährlich + nach jedem Einsatz reinigen\n\n"
                    "## Hygiene\n"
                    "PSA ist **persönlich** — nicht teilen. Mehrweg-Atemmaske nach "
                    "Nutzung reinigen und desinfizieren."
                ),
            ),
            ModulDef(
                titel="Atemschutz im Detail",
                inhalt_md=(
                    "## Filterklassen (für Partikel)\n"
                    "- **FFP1** — Filterleistung 80 %, ungiftiger Staub\n"
                    "- **FFP2** — 94 %, gesundheitsschädlicher Staub (Metallstaub, Holzstaub)\n"
                    "- **FFP3** — 99 %, krebserzeugend (Asbest, Quarz, Schweißrauch CMR)\n\n"
                    "## Gasfilter (farbcodiert)\n"
                    "- **A** (braun) — organische Dämpfe\n"
                    "- **B** (grau) — anorganische Gase (Chlor, H₂S)\n"
                    "- **E** (gelb) — saure Gase (SO₂)\n"
                    "- **K** (grün) — Ammoniak\n\n"
                    "## Wichtig\n"
                    "Filtergeräte schützen NUR bei mindestens 17 % Restsauerstoff in "
                    "der Atemluft. In engen Räumen / Tanks / Silos **immer umluft"
                    "unabhängig** (Pressluftatmer)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was bedeutet das 'TOP-Prinzip' in der Schutzhierarchie?",
                erklaerung="Technisch vor Organisatorisch vor Persönlich. PSA ist immer "
                "die letzte Schutzlinie.",
                optionen=_opts(
                    ("Technisch > Organisatorisch > Persönlich", True),
                    ("Time-On-Plant — Anwesenheitspflicht", False),
                    ("Tarifvertraglich-Organisations-Pflicht", False),
                    ("Tragepflicht-Organisations-PSA", False),
                ),
            ),
            FrageDef(
                text="Ab welchem Lärmpegel ist Gehörschutz Pflicht?",
                erklaerung="80 dB(A) Auslösewert (LärmVibrationsArbSchV § 8): "
                "Bereitstellung. 85 dB(A): Tragepflicht.",
                optionen=_opts(
                    ("Bereitstellung ab 80 dB(A), Pflicht ab 85 dB(A)", True),
                    ("Erst ab 100 dB(A)", False),
                    ("Ab 50 dB(A)", False),
                    ("Gibt keine Pflicht", False),
                ),
            ),
            FrageDef(
                text="Du hast eine FFP2-Maske. Wofür eignet sie sich NICHT?",
                erklaerung="FFP2 ist Partikelfilter, kein Gasfilter — gegen Dämpfe braucht "
                "es Filter Typ A/B/E/K.",
                optionen=_opts(
                    ("Gegen organische Lösemitteldämpfe", True),
                    ("Gegen Holzstaub", False),
                    ("Gegen Metallschleif-Staub", False),
                    ("Gegen Mehlstaub", False),
                ),
            ),
            FrageDef(
                text="Was tust du, wenn dein Schutzhelm einen Riss in der Schale hat?",
                erklaerung="Beschädigte PSA verliert ihre Schutzwirkung — sofort ersetzen.",
                optionen=_opts(
                    ("Sofort austauschen", True),
                    ("Mit Klebeband flicken", False),
                    ("Noch 1 Woche tragen, dann tauschen", False),
                    ("Nur intern verwenden, draußen neuen nehmen", False),
                ),
            ),
            FrageDef(
                text="Was ist beim Einsatz in einem geschlossenen Tank zu beachten?",
                erklaerung="Filtergeräte funktionieren nur bei genug Sauerstoff. Tanks → "
                "umluftunabhängiger Atemschutz (Pressluft).",
                optionen=_opts(
                    ("Nur umluftunabhängiger Atemschutz, FFP-Masken sind nicht zulässig", True),
                    ("Eine FFP3-Maske reicht aus", False),
                    ("Kein Schutz nötig", False),
                    ("Pressluftatmer nur, wenn man Allergiker ist", False),
                ),
            ),
            FrageDef(
                text="Wie häufig wird ein Auffanggurt (Absturzsicherung) geprüft?",
                erklaerung="DGUV-Grundsatz 312-906: jährliche Sachkundigen-Prüfung Pflicht.",
                optionen=_opts(
                    ("Mindestens jährlich durch eine Sachkundige Person", True),
                    ("Nur beim Kauf", False),
                    ("Alle 10 Jahre", False),
                    ("Nur nach einem Sturz", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #8
    KursDef(
        titel="Maschinen- und Anlagensicherheit",
        beschreibung="Sichere Arbeit an Maschinen nach BetrSichV § 12. "
        "Schutzeinrichtungen, Lockout-Tagout, Wartungssicherheit.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Schutzeinrichtungen verstehen",
                inhalt_md=(
                    "## Typen von Schutzeinrichtungen\n\n"
                    "- **Trennend** — feste Verkleidung, bewegliche Schutztür mit "
                    "Verriegelung\n"
                    "- **Nichttrennend** — Lichtgitter, Trittmatte, Zweihand-"
                    "schaltung, Laserscanner\n\n"
                    "## NIEMALS\n"
                    "- Schutzeinrichtungen überbrücken, manipulieren, abschrauben\n"
                    "- Beweglichen Schutz mechanisch festklemmen ('damit's schneller geht')\n"
                    "- Maschine mit fehlerhaftem Sicherheits-Lichtgitter weiter betreiben\n\n"
                    "**Manipulation ist Straftat** nach § 23 BetrSichV (Bußgeld bis "
                    "30.000 €, in schweren Fällen Freiheitsstrafe)."
                ),
            ),
            ModulDef(
                titel="Lockout-Tagout (LOTO)",
                inhalt_md=(
                    "## Prinzip\n\n"
                    "Bei Wartung, Reinigung, Störungsbeseitigung MUSS die Maschine "
                    "in einen **sicheren, energiefreien Zustand** gebracht werden.\n\n"
                    "## 6 Schritte\n"
                    "1. **Vorbereitung** — Welche Energiequellen sind aktiv? (elektrisch, "
                    "pneumatisch, hydraulisch, Schwerkraft, Federn)\n"
                    "2. **Abschalten** der Maschine\n"
                    "3. **Trennen** aller Energiequellen (Hauptschalter aus, Druck ablassen, "
                    "Schwerkraft sichern)\n"
                    "4. **Verschließen** (Lockout) — Vorhängeschloss am Schalter\n"
                    "5. **Kennzeichnen** (Tagout) — Schild mit Namen + Datum\n"
                    "6. **Wirkungsprüfung** — Probelauf-Versuch: Maschine darf NICHT "
                    "anlaufen\n\n"
                    "**Mehrere Personen** = jede Person hat ihr eigenes Schloss. "
                    "Erst wenn alle ihre Schlösser entfernt haben, kann die Maschine wieder anlaufen."
                ),
            ),
            ModulDef(
                titel="Wartung & Störungsbeseitigung sicher",
                inhalt_md=(
                    "## Vor jeder Wartung\n"
                    "- Wartungsplan einsehen (Hersteller)\n"
                    "- Werkzeuge prüfen\n"
                    "- LOTO durchführen\n"
                    "- PSA anlegen\n\n"
                    "## Restenergien beachten\n"
                    "- **Federkraft** — Pneumatik-Aktor hat Notrückstellung\n"
                    "- **Schwerkraft** — hochgefahrenes Werkzeug abstützen / abgesenkt halten\n"
                    "- **Restdruck** — pneumatische Leitungen entlüften\n"
                    "- **Restladung** — Kondensatoren bis 5 min entladen lassen\n\n"
                    "## Nach der Wartung\n"
                    "- Werkzeuge entfernen\n"
                    "- Schutzeinrichtungen wieder anbringen\n"
                    "- LOTO aufheben (jeder seine Schlösser)\n"
                    "- Probelauf nur in **gesichertem Bereich**"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Strafe droht bei Manipulation von Schutzeinrichtungen?",
                erklaerung="§ 23 BetrSichV: bis 30.000 € Bußgeld, in schweren Fällen "
                "Freiheitsstrafe.",
                optionen=_opts(
                    ("Bußgeld bis 30.000 €, in schweren Fällen Freiheitsstrafe", True),
                    ("Eine Verwarnung", False),
                    ("Keine — ist Privatsache", False),
                    ("Nur Abmahnung durch den Chef", False),
                ),
            ),
            FrageDef(
                text="Was ist 'Lockout-Tagout' (LOTO)?",
                erklaerung="Verfahren, eine Maschine sicher in den energielosen Zustand zu "
                "bringen und gegen Wiedereinschalten zu sichern.",
                optionen=_opts(
                    ("Verfahren zur sicheren Außerbetriebnahme einer Maschine für Wartung", True),
                    ("Schließsystem für die Werkstatttür", False),
                    ("Eine Akkord-Vergütungsregel", False),
                    ("Eine Sportart", False),
                ),
            ),
            FrageDef(
                text="Wieviele Schlösser werden bei LOTO mit 3 Wartungstechnikern verwendet?",
                erklaerung="Jede Person bringt ihr eigenes Schloss an — Maschine bleibt "
                "gesperrt bis der LETZTE sein Schloss abnimmt.",
                optionen=_opts(
                    ("Drei — jede Person ihr eigenes", True),
                    ("Eines reicht", False),
                    ("Eines pro Energiequelle", False),
                    ("Keines — Schild reicht", False),
                ),
            ),
            FrageDef(
                text="Was darf NICHT überbrückt werden?",
                erklaerung="Sicherheits-Lichtgitter ist Schutzeinrichtung — Überbrückung "
                "= Straftat.",
                optionen=_opts(
                    ("Ein Sicherheits-Lichtgitter, um die Maschine schneller zu starten", True),
                    ("Eine optische LED-Anzeige für Wartung", False),
                    ("Der Hupschalter", False),
                    ("Der Pausen-Taster", False),
                ),
            ),
            FrageDef(
                text="Was tust du, wenn eine Maschine mit defekter Schutzeinrichtung läuft?",
                erklaerung="Stillsetzen, melden — niemals weiterlaufen lassen.",
                optionen=_opts(
                    ("Sofort stillsetzen und Vorgesetzte/n + Sifa informieren", True),
                    ("Eigenmächtig reparieren", False),
                    ("Weiter arbeiten und Bescheid sagen wenn Pause ist", False),
                    ("Selbst die Lichtschranke deaktivieren", False),
                ),
            ),
            FrageDef(
                text="Welche Restenergie wird oft übersehen?",
                erklaerung="Schwerkraft / Federn werden häufig vergessen — Werkstücke "
                "können sich beim Lösen plötzlich bewegen.",
                optionen=_opts(
                    ("Schwerkraft (hochgefahrenes Werkzeug, gespannte Federn)", True),
                    ("Elektrischer Hauptanschluss", False),
                    ("Pneumatik-Hauptleitung", False),
                    ("Kühlwasser", False),
                ),
            ),
            FrageDef(
                text="Was ist der letzte Schritt vor Beginn der Wartung nach LOTO?",
                erklaerung="Wirkungsprüfung: Probelauf-Versuch zeigt, ob die Energietrennung "
                "wirklich greift.",
                optionen=_opts(
                    ("Wirkungsprüfung — Maschine darf nicht anlaufen", True),
                    ("Kaffeepause", False),
                    ("Aushändigung der Werkzeuge", False),
                    ("Vorgesetzte/n grüßen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #9
    KursDef(
        titel="Lärm und Vibration am Arbeitsplatz",
        beschreibung="Unterweisung nach LärmVibrationsArbSchV. Auslösewerte, "
        "Gehörschutz-Praxis.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Auslösewerte und Pflichten",
                inhalt_md=(
                    "## Lärm — § 6 LärmVibrationsArbSchV\n\n"
                    "| Wert | Konsequenz |\n"
                    "|---|---|\n"
                    "| **80 dB(A)** Tages-Lärmexposition | Bereitstellung Gehörschutz, "
                    "Unterweisung |\n"
                    "| **85 dB(A)** | Tragepflicht, Kennzeichnung als Lärmbereich, "
                    "G20-Vorsorge angeboten |\n"
                    "| **137 dB(C)** Spitzenwert | sofortiger Schutz nötig |\n\n"
                    "## Vibration\n"
                    "- Hand-Arm: Auslösewert 2,5 m/s² (8h), Grenzwert 5,0 m/s²\n"
                    "- Ganzkörper: Auslösewert 0,5 m/s², Grenzwert 1,15 m/s²\n\n"
                    "## Gesundheitliche Folgen\n"
                    "- Lärm: Lärmschwerhörigkeit (irreversibel!), Tinnitus, Bluthochdruck\n"
                    "- Vibration: Weißfingerkrankheit (HAV-Syndrom), Bandscheibenschäden"
                ),
            ),
            ModulDef(
                titel="Gehörschutz in der Praxis",
                inhalt_md=(
                    "## Auswahl\n"
                    "- **Stöpsel** — 15–25 dB Dämmung, kostengünstig, einweg/mehrweg\n"
                    "- **Bügel** — schnelles Auf-/Absetzen, gut für kurze Lärmbereiche\n"
                    "- **Kapsel** — 20–35 dB Dämmung, robust, evtl. mit Funkmodul\n"
                    "- **Otoplastik** (individuell angepasst) — Komfort + sehr gute Dämmung\n\n"
                    "## Auswahlfehler\n"
                    "Zu hohe Dämmung kann gefährlich sein: Warnsignale werden überhört. "
                    "Ziel ist Restpegel **65–80 dB(A)** am Ohr.\n\n"
                    "## Tragehinweise\n"
                    "- Stöpsel: rollen, einführen, halten bis sich Material entfaltet\n"
                    "- Kapsel: Dichtkissen müssen direkt am Schädel anliegen — Brille, "
                    "lange Haare können stören\n"
                    "- **Konsequent tragen** — auch kurze Auszeiten zerstören die "
                    "Schutzwirkung deutlich"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Ab welchem Lärmpegel muss der Arbeitgeber Gehörschutz bereitstellen?",
                erklaerung="Unterer Auslösewert 80 dB(A) → Bereitstellung. Oberer 85 dB(A) → "
                "Tragepflicht.",
                optionen=_opts(
                    ("Ab 80 dB(A) Tages-Lärmexposition", True),
                    ("Ab 90 dB(A)", False),
                    ("Ab 100 dB(A)", False),
                    ("Erst wenn Mitarbeiter sich beschweren", False),
                ),
            ),
            FrageDef(
                text="Was ist die Lärmschwerhörigkeit?",
                erklaerung="Irreversibler Schaden der Haarzellen im Innenohr — kann nicht "
                "rückgängig gemacht werden.",
                optionen=_opts(
                    ("Eine irreversible Schädigung des Innenohrs durch zu lauten Schall", True),
                    ("Eine vorübergehende Hörminderung nach einem Konzert", False),
                    ("Eine Ohrenentzündung", False),
                    ("Eine Allergie gegen Lärm", False),
                ),
            ),
            FrageDef(
                text="Welche Dämmung ist sinnvoll, damit du noch Warnsignale hören kannst?",
                erklaerung="Restpegel 65–80 dB(A) — Warnsignale müssen noch wahrnehmbar sein.",
                optionen=_opts(
                    ("So viel, dass am Ohr noch 65–80 dB(A) ankommen", True),
                    ("Maximale Dämmung — je mehr desto besser", False),
                    ("Mindest-Dämmung 5 dB", False),
                    ("Keine — Warnsignale sind wichtiger als Schutz", False),
                ),
            ),
            FrageDef(
                text="Was ist die Weißfingerkrankheit (HAV-Syndrom)?",
                erklaerung="Hand-Arm-Vibrations-Syndrom: Durchblutungsstörung der Finger "
                "durch Vibrationsexposition (z. B. Schlagschrauber, Bohrhammer).",
                optionen=_opts(
                    ("Durchblutungsstörung der Finger durch jahrelange Vibrationsexposition", True),
                    ("Eine Hauterkrankung von Bäckern", False),
                    ("Frostbeulen im Winter", False),
                    ("Allergie gegen Latex-Handschuhe", False),
                ),
            ),
            FrageDef(
                text="Wann ist die G20-Vorsorgeuntersuchung anzubieten?",
                erklaerung="Ab dem oberen Auslösewert 85 dB(A) ist die arbeitsmedizinische "
                "Vorsorge anzubieten (DGUV-Grundsatz G20).",
                optionen=_opts(
                    ("Ab 85 dB(A) Tages-Lärmexposition", True),
                    ("Ab 70 dB(A)", False),
                    ("Erst bei Beschwerden", False),
                    ("Einmal beim Eintritt — dann nie wieder", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #10
    KursDef(
        titel="Antikorruption & Geschenke-Policy",
        beschreibung="Compliance-Schulung zu Bestechung & Vorteilsnahme nach § 299 StGB "
        "+ ISO 37001. Zuwendungen erkennen, Lieferantenkontakt, Meldewege.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Was ist Korruption?",
                inhalt_md=(
                    "## Definition\n\n"
                    "Korruption ist der **Missbrauch einer anvertrauten Stellung** zum "
                    "privaten Vorteil oder zum Vorteil eines Dritten. Im StGB:\n\n"
                    "- **§ 299 StGB** — Bestechlichkeit/Bestechung im geschäftlichen Verkehr\n"
                    "- **§ 331-335 StGB** — Vorteilsannahme/Bestechung von Amtsträgern\n"
                    "- **§ 266 StGB** — Untreue\n\n"
                    "## Beispiele Privatwirtschaft\n"
                    "- Einkäufer erhält Provision vom Lieferanten für Auftragsvergabe\n"
                    "- Vertriebsleiter lädt Kunde auf Mallorca-Reise ein\n"
                    "- 'Beratungshonorar' für Person ohne tatsächliche Leistung\n"
                    "- Schwarzgeld-Kasse für 'Anbahnung von Geschäften'\n\n"
                    "## Strafe\n"
                    "Freiheitsstrafe bis 5 Jahre (§ 299), in schweren Fällen bis 10 Jahre. "
                    "Plus Geldbuße gegen das Unternehmen nach § 30 OWiG."
                ),
            ),
            ModulDef(
                titel="Zuwendungen — was ist erlaubt?",
                inhalt_md=(
                    "## Faustregel\n\n"
                    "Geschenke sind erlaubt, wenn sie\n"
                    "- **geringwertig** sind (häufig Schwellenwert 50 € je Anlass + "
                    "Kalenderjahr)\n"
                    "- **anlassbezogen** (Weihnachten, Jubiläum, Vertragsabschluss)\n"
                    "- **transparent** angenommen (Vorgesetzter informiert, ggf. "
                    "Geschenke-Register)\n"
                    "- **nicht beeinflussend** wirken\n\n"
                    "## Eher problematisch\n"
                    "- Bargeld, Gutscheine\n"
                    "- Reisen, Hotels, Eintrittskarten\n"
                    "- Wiederholte Zuwendungen vom gleichen Geschäftspartner\n"
                    "- Geschenke an Familienmitglieder\n"
                    "- Zuwendungen vor/während Vergabe-Entscheidungen\n\n"
                    "## Gegenüber Amtsträgern\n"
                    "Schon **geringe** Zuwendungen können strafbar sein — strikteres "
                    "Regime. Im Zweifel: ablehnen und Compliance fragen."
                ),
            ),
            ModulDef(
                titel="Lieferanten- und Kundenbeziehungen",
                inhalt_md=(
                    "## Einladungen zu Veranstaltungen\n\n"
                    "Erlaubt sind:\n"
                    "- **Fachveranstaltungen** mit klarem geschäftlichen Bezug\n"
                    "- **Übliche** Bewirtungen (Geschäftsessen)\n"
                    "- Sportevent mit Geschäftspartnern, wenn **Geschäftsbezug** "
                    "überwiegt\n\n"
                    "Nicht erlaubt:\n"
                    "- Familien-Wochenende auf Firmenkosten des Lieferanten\n"
                    "- Goldene Visitenkarten in der Beraterbranche\n\n"
                    "## Sponsoring & Spenden\n"
                    "- Müssen transparent + dokumentiert sein\n"
                    "- Genehmigung durch Geschäftsleitung\n"
                    "- Keine Spenden 'für die Erleichterung der Genehmigung'\n\n"
                    "## Meldewege\n"
                    "Verdacht? **Anonyme Meldung über das Hinweisgeberportal** "
                    "(HinSchG-Kanal) oder direkt an Compliance-Beauftragte/n. "
                    "Repressalien gegen Meldende sind verboten."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was regelt § 299 StGB?",
                erklaerung="Bestechlichkeit und Bestechung im geschäftlichen Verkehr — "
                "auch zwischen Privatunternehmen strafbar.",
                optionen=_opts(
                    ("Bestechlichkeit und Bestechung im geschäftlichen Verkehr", True),
                    ("Steuerhinterziehung", False),
                    ("Datenschutzverletzungen", False),
                    ("Arbeitssicherheit", False),
                ),
            ),
            FrageDef(
                text="Welcher Wert wird in Geschenke-Policies häufig als Schwellenwert pro Anlass genannt?",
                erklaerung="Häufig 50 € — variiert aber pro Unternehmen und Branche.",
                optionen=_opts(
                    ("Ca. 50 € pro Anlass und Geschäftspartner pro Jahr", True),
                    ("500 €", False),
                    ("5 €", False),
                    ("Es gibt keinen Schwellenwert", False),
                ),
            ),
            FrageDef(
                text="Welches Geschenk wäre besonders problematisch?",
                erklaerung="Vor einer Vergabeentscheidung sind selbst kleine Zuwendungen "
                "kritisch wegen des Anscheins der Beeinflussung.",
                optionen=_opts(
                    ("Eine teure Uhr eines Lieferanten kurz vor einer Vergabe-Entscheidung", True),
                    ("Ein Tannenzweig zur Weihnachtszeit", False),
                    ("Ein Werbekugelschreiber im Wert von 5 €", False),
                    ("Ein Stück Schokolade vom Kundenbesuch", False),
                ),
            ),
            FrageDef(
                text="Du erhältst eine Wochenendreise nach Mallorca von einem Lieferanten. Was tust du?",
                erklaerung="Wertvolle Reise = unzulässig. Annahme könnte strafbar sein "
                "(§ 299 StGB), Ablehnung dokumentieren.",
                optionen=_opts(
                    ("Ablehnen und der/dem Compliance-Beauftragten melden", True),
                    ("Annehmen und nicht weiter erwähnen", False),
                    ("Mit Familie hinfahren — ist ja privat", False),
                    ("Erst nehmen, dann später Bescheid sagen", False),
                ),
            ),
            FrageDef(
                text="Worüber kannst du anonym einen Korruptions-Verdacht melden?",
                erklaerung="Hinweisgeberschutzgesetz: anonymer Meldekanal mit Schutz vor "
                "Repressalien ist Pflicht.",
                optionen=_opts(
                    ("Anonymes Hinweisgeberportal nach HinSchG", True),
                    ("Schwarzes Brett in der Kantine", False),
                    ("Linkedin-Post mit Tag des Compliance-Officers", False),
                    ("Anrufer-Hotline der Polizei (für Privatpersonen)", False),
                ),
            ),
            FrageDef(
                text="Was sind die Folgen für das Unternehmen bei nachgewiesener Korruption?",
                erklaerung="§ 30 OWiG: Verbandsgeldbuße bis 10 Mio. € + Gewinnabschöpfung. "
                "Reputations-Schaden + Vergabeausschluss.",
                optionen=_opts(
                    ("Hohe Geldbußen, Gewinnabschöpfung, Vergabeausschluss, Reputations-Schaden", True),
                    ("Eine kurze öffentliche Entschuldigung", False),
                    ("Nur die Person, die bestochen wurde, ist strafbar — Firma nie", False),
                    ("Keine — Korruption ist Privatsache", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #11
    KursDef(
        titel="AGG — Gleichbehandlung am Arbeitsplatz",
        beschreibung="Pflichtunterweisung nach § 12 Abs. 2 AGG. "
        "Diskriminierungsmerkmale + Beschwerderecht.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Geschützte Merkmale & Diskriminierungsformen",
                inhalt_md=(
                    "## Geschützte Merkmale (§ 1 AGG)\n\n"
                    "- **Ethnische Herkunft** / 'Rasse' (Begriff aus dem Gesetzestext)\n"
                    "- **Geschlecht** (inkl. trans*, inter*)\n"
                    "- **Religion / Weltanschauung**\n"
                    "- **Behinderung**\n"
                    "- **Alter**\n"
                    "- **Sexuelle Identität**\n\n"
                    "## Formen der Diskriminierung\n"
                    "- **Unmittelbar** — direkte Schlechterbehandlung wegen eines Merkmals\n"
                    "- **Mittelbar** — neutrale Regel führt faktisch zu Benachteiligung "
                    "(z. B. Größen-Anforderung diskriminiert Frauen)\n"
                    "- **Belästigung** — würdeverletzendes Verhalten\n"
                    "- **Sexuelle Belästigung** — unerwünschte sexuell bestimmte Handlung\n"
                    "- **Anweisung zur Diskriminierung** durch Vorgesetzte"
                ),
            ),
            ModulDef(
                titel="Beschwerderecht & betriebliche Beschwerdestelle",
                inhalt_md=(
                    "## § 13 AGG — Beschwerdestelle\n\n"
                    "Jeder Betrieb MUSS eine Beschwerdestelle haben. Häufig:\n"
                    "- Personalabteilung\n"
                    "- Betriebsrat\n"
                    "- Gleichstellungsbeauftragte/r\n\n"
                    "## Beschwerde-Verfahren\n"
                    "1. Beschwerde wird **vertraulich** geprüft\n"
                    "2. Aufklärung des Sachverhalts\n"
                    "3. **Schutzmaßnahmen** falls Benachteiligung bestätigt — z. B. "
                    "Versetzung, Abmahnung, Kündigung der Person, die diskriminiert hat\n\n"
                    "## Rechte der Beschäftigten\n"
                    "- **Leistungsverweigerungsrecht** (§ 14 AGG) — bei sexueller "
                    "Belästigung ohne Lohnverlust, bis Arbeitgeber Schutz herstellt\n"
                    "- **Entschädigung** (§ 15 AGG) — bis zu 3 Monatsgehälter\n"
                    "- **Schadenersatz** bei Vermögensschaden\n\n"
                    "**Verbot der Maßregelung** (§ 16): keine Repressalien gegen "
                    "Beschwerdeführende."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welches Merkmal ist NICHT im § 1 AGG geschützt?",
                erklaerung="Politische Gesinnung wird im AGG nicht direkt erfasst — "
                "Weltanschauung ist enger gefasst (z. B. Pazifismus, Anthroposophie).",
                optionen=_opts(
                    ("Politische Parteizugehörigkeit", True),
                    ("Ethnische Herkunft", False),
                    ("Behinderung", False),
                    ("Sexuelle Identität", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'mittelbare' Diskriminierung?",
                erklaerung="Eine an sich neutrale Regelung, die in der Praxis eine "
                "geschützte Gruppe systematisch benachteiligt.",
                optionen=_opts(
                    ("Eine neutral wirkende Regel, die eine geschützte Gruppe faktisch benachteiligt", True),
                    ("Ein Streit zwischen Kollegen", False),
                    ("Eine Aussage hinter dem Rücken einer Person", False),
                    ("Direkte Beschimpfung", False),
                ),
            ),
            FrageDef(
                text="An wen kann man sich bei Diskriminierungsverdacht wenden?",
                erklaerung="§ 13 AGG: Beschwerdestelle muss eingerichtet sein (meist HR, "
                "Betriebsrat, Gleichstellungsbeauftragte/r).",
                optionen=_opts(
                    ("Die betriebliche Beschwerdestelle nach § 13 AGG", True),
                    ("Niemanden — das muss man selbst regeln", False),
                    ("Nur die Polizei", False),
                    ("Nur den direkten Vorgesetzten", False),
                ),
            ),
            FrageDef(
                text="Wie hoch kann die Entschädigung bei AGG-Verstoß sein?",
                erklaerung="§ 15 AGG: bei Nicht-Einstellung bis 3 Monatsgehälter, bei "
                "Diskriminierung im laufenden Arbeitsverhältnis keine Obergrenze.",
                optionen=_opts(
                    ("Bei Nicht-Einstellung: bis zu 3 Monatsgehälter", True),
                    ("Maximal 100 €", False),
                    ("Es gibt keine Entschädigung", False),
                    ("Nur das Monatsgehalt zurück", False),
                ),
            ),
            FrageDef(
                text="Du wirst Zeuge einer sexistischen Bemerkung gegenüber einer Kollegin. Was kannst du tun?",
                erklaerung="Aktives Eingreifen ist hilfreich, mindestens aber Vorfall bei "
                "Beschwerdestelle melden — Schweigen normalisiert Verhalten.",
                optionen=_opts(
                    ("Die Bemerkung adressieren und Beschwerdestelle informieren", True),
                    ("Schweigen — ist nicht meine Sache", False),
                    ("Lachen, damit es nicht so ernst wirkt", False),
                    ("Selber Gegen-Bemerkung machen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #12
    KursDef(
        titel="Hinweisgeberschutz (HinSchG)",
        beschreibung="Was Mitarbeitende über das Hinweisgebersystem wissen müssen "
        "(HinSchG § 8 ff.). Meldekanal, Schutzrechte, Repressalienverbot.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Was ist das HinSchG?",
                inhalt_md=(
                    "## Hinweisgeberschutzgesetz (seit 2.7.2023)\n\n"
                    "Setzt die EU-Whistleblower-Richtlinie um. Schützt Personen, die "
                    "Verstöße gegen geltendes Recht melden, vor Repressalien.\n\n"
                    "## Wer ist erfasst?\n"
                    "- Beschäftigte aller Art (auch Praktikant:innen, Leiharbeiter:innen)\n"
                    "- Selbständige, Bewerber:innen, Ehemalige\n"
                    "- Anteilseigner:innen\n\n"
                    "## Welche Verstöße können gemeldet werden?\n"
                    "- Straftaten\n"
                    "- Ordnungswidrigkeiten (mit Geld-/Freiheitsstrafe)\n"
                    "- Verstöße gegen Umwelt-, Daten-, Geldwäsche-, Produktsicherheits-, "
                    "Verbraucherschutzrecht\n"
                    "- Korruption, Geldwäsche\n\n"
                    "## Pflicht für Arbeitgeber\n"
                    "- 50–249 Beschäftigte: interner Meldekanal Pflicht\n"
                    "- 250+: interner Meldekanal Pflicht\n"
                    "- Es gibt zusätzlich externe Meldekanäle (BfJ, BaFin, …)"
                ),
            ),
            ModulDef(
                titel="Meldekanal & Schutzrechte",
                inhalt_md=(
                    "## Wie melde ich?\n\n"
                    "**Interner Kanal** (vorzugsweise): über das Hinweisgeberportal "
                    "unseres Unternehmens — auch **anonym** möglich.\n\n"
                    "**Externer Kanal**: Bundesamt für Justiz (BfJ), Branchen-Aufsichts"
                    "behörden (BaFin, BKartA, Datenschutzbehörden …).\n\n"
                    "**Offenlegung gegenüber Öffentlichkeit** nur als letzte Option, "
                    "wenn intern + extern keine Wirkung erzielt wurde.\n\n"
                    "## Schutzrechte\n"
                    "- **Identitätsschutz** — Identität bleibt vertraulich\n"
                    "- **Repressalien sind verboten** (§ 36 HinSchG) — Kündigung, "
                    "Versetzung, Mobbing, Lohnkürzung sind nichtig\n"
                    "- **Beweislastumkehr** (§ 36 Abs. 2) — Arbeitgeber muss beweisen, "
                    "dass Nachteil nicht wegen der Meldung erfolgte\n"
                    "- **Schadenersatz** bei Repressalien\n\n"
                    "## Bestätigung & Rückmeldung\n"
                    "- Eingangsbestätigung: spätestens **7 Tage**\n"
                    "- Rückmeldung zu Maßnahmen: spätestens **3 Monate** nach Eingang"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wer ist durch das HinSchG geschützt?",
                erklaerung="Sehr breit gefasst — alle, die im beruflichen Kontext einen "
                "Verstoß bemerken (auch Bewerber:innen und Ehemalige).",
                optionen=_opts(
                    ("Alle, die im beruflichen Kontext einen Verstoß bemerken — auch Praktikant:innen + Ehemalige", True),
                    ("Nur fest angestellte Mitarbeitende", False),
                    ("Nur leitende Angestellte", False),
                    ("Nur Mitarbeitende, die persönlich betroffen sind", False),
                ),
            ),
            FrageDef(
                text="Welche Frist gilt für die Eingangsbestätigung einer Meldung?",
                erklaerung="§ 17 HinSchG: 7 Tage Eingangsbestätigung, 3 Monate Rückmeldung "
                "zu Maßnahmen.",
                optionen=_opts(
                    ("7 Tage", True),
                    ("24 Stunden", False),
                    ("1 Monat", False),
                    ("Es gibt keine Frist", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'Beweislastumkehr' nach § 36 Abs. 2 HinSchG?",
                erklaerung="Wenn ein Nachteil zeitlich auf eine Meldung folgt, muss der "
                "Arbeitgeber beweisen, dass der Nachteil nicht wegen der Meldung erfolgte.",
                optionen=_opts(
                    ("Arbeitgeber muss beweisen, dass eine Sanktion NICHT wegen der Meldung erfolgte", True),
                    ("Hinweisgeber:in muss alle Vorwürfe selbst nachweisen", False),
                    ("Beide Seiten teilen sich die Beweisführung 50/50", False),
                    ("Der Betriebsrat trägt die Beweislast", False),
                ),
            ),
            FrageDef(
                text="Welche Repressalien gegen Hinweisgeber:innen sind erlaubt?",
                erklaerung="Keine. Kündigung, Versetzung, Lohnkürzung wegen der Meldung "
                "sind nichtig (§ 36 HinSchG).",
                optionen=_opts(
                    ("Keine — alle Repressalien sind nichtig", True),
                    ("Eine 'milde' Versetzung in eine ruhigere Abteilung", False),
                    ("Kürzung des Weihnachtsgelds", False),
                    ("Nur eine schriftliche Ermahnung", False),
                ),
            ),
            FrageDef(
                text="Wann ist eine 'Offenlegung gegenüber der Öffentlichkeit' nach HinSchG geschützt?",
                erklaerung="Nur als letzte Option: wenn intern + extern keine Wirkung "
                "erzielt wurde oder unmittelbare Gefahr besteht (§ 32 HinSchG).",
                optionen=_opts(
                    ("Nur als letzte Option, wenn intern + extern keine Wirkung erzielt wurde", True),
                    ("Sofort als erste Wahl", False),
                    ("Wenn die Person gerne öffentlich auftritt", False),
                    ("Nur in Print-Medien, nicht im Internet", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #13
    KursDef(
        titel="Flurförderzeuge & Gabelstapler",
        beschreibung="Pflichtunterweisung Stapler-Fahrer:innen nach DGUV Grundsatz 308-001. "
        "Fahrerlaubnis, sicherer Betrieb, Stand­sicherheit/Last.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Fahrerlaubnis & Voraussetzungen",
                inhalt_md=(
                    "## Wer darf Stapler fahren?\n\n"
                    "Nach **DGUV Grundsatz 308-001** muss der/die Fahrer:in:\n"
                    "- **18 Jahre** oder älter sein (Ausnahmen für Auszubildende möglich)\n"
                    "- **Körperlich + geistig geeignet** sein (G25-Untersuchung empfohlen)\n"
                    "- Eine **theoretische + praktische Ausbildung** absolviert haben\n"
                    "- **Schriftliche Beauftragung** durch den Unternehmer\n\n"
                    "## Jährliche Unterweisung\n"
                    "Auch wenn der 'Staplerschein' lebenslang gilt — die jährliche "
                    "Wiederholungs-Unterweisung am Arbeitsplatz ist Pflicht.\n\n"
                    "## Mitfahrer\n"
                    "Mitfahren auf einem Stapler ist **verboten** — außer auf dafür "
                    "ausgerüsteten Beifahrer-Sitzplätzen."
                ),
            ),
            ModulDef(
                titel="Sicherer Betrieb",
                inhalt_md=(
                    "## Vor Arbeitsbeginn\n"
                    "- **Abfahrtskontrolle** (wie beim PKW): Bremsen, Lenkung, Hupe, "
                    "Beleuchtung, Hydraulik\n"
                    "- Mängel SOFORT melden, Stapler stilllegen\n\n"
                    "## Während der Fahrt\n"
                    "- **Sicherheitsgurt anlegen** (auch bei Kurzstrecken)\n"
                    "- **Last gesenkt** transportieren (Bodenfreiheit ~15 cm)\n"
                    "- **Rückwärts fahren** bei Sicht-Hindernis\n"
                    "- Geschwindigkeit der Umgebung anpassen (in Halle Schritt­geschwindigkeit)\n"
                    "- Bei steilen Rampen: **Last bergauf** zeigen\n\n"
                    "## Beim Be-/Entladen\n"
                    "- Niemals unter angehobener Last hindurchgehen oder darunter arbeiten\n"
                    "- Gabel-Schwerpunkt **mittig** auf der Palette\n"
                    "- Nach dem Absenken: Gabeln auf den Boden ablegen, Handbremse"
                ),
            ),
            ModulDef(
                titel="Standsicherheit & Lastdiagramm",
                inhalt_md=(
                    "## Kippen vermeiden\n\n"
                    "Stapler kippt nach **vorn** oder **seitlich**:\n"
                    "- Zu **schwere** Last oder zu **weiter Lastschwerpunkt-Abstand**\n"
                    "- **Schnelle** Lenkbewegung\n"
                    "- **Hohe** Last in Kurve\n"
                    "- **Schiefe Ebene** quer befahren\n\n"
                    "## Lastdiagramm\n"
                    "Auf jedem Stapler angebracht. Zeigt die zulässige Last in "
                    "Abhängigkeit von:\n"
                    "- **Lastschwerpunktabstand** (Standard 500 mm) \n"
                    "- **Hubhöhe**\n\n"
                    "Beispiel: 3 t bei LSP 500 mm und 3,5 m Hubhöhe — bei LSP 700 mm "
                    "und 5 m Hubhöhe nur noch 1,8 t. **Diagramm vor jedem Hub prüfen.**\n\n"
                    "## Wenn der Stapler kippt\n"
                    "- **Nicht abspringen** — Anschnallgurt halten\n"
                    "- Festhalten, in Sitz pressen, vom Fallweg wegneigen\n"
                    "- Stapler-Fahrerkabine schützt — Abspringende werden oft "
                    "vom Stapler erschlagen"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Voraussetzung muss ein/e Staplerfahrer:in erfüllen?",
                erklaerung="DGUV 308-001: 18 J. + körperlich/geistig geeignet + Ausbildung "
                "+ schriftliche Beauftragung.",
                optionen=_opts(
                    ("Mindestens 18 Jahre + Ausbildung + schriftliche Beauftragung des Unternehmers", True),
                    ("Nur einen PKW-Führerschein", False),
                    ("Mündliche Erlaubnis des Vorgesetzten reicht", False),
                    ("Nur einmal Probe gefahren sein", False),
                ),
            ),
            FrageDef(
                text="Wie wird eine Last transportiert?",
                erklaerung="Gesenkt (ca. 15 cm Bodenfreiheit) — schwerpunkt-nah am Stapler, "
                "Kippneigung minimieren.",
                optionen=_opts(
                    ("Knapp über dem Boden, mit Sicherheitsgurt", True),
                    ("So hoch wie möglich angehoben — bessere Sicht", False),
                    ("In Schräglage", False),
                    ("Mit zusätzlichem Mitfahrer auf der Last", False),
                ),
            ),
            FrageDef(
                text="Was tust du, wenn der Stapler zu kippen droht?",
                erklaerung="Festhalten und in Sitz pressen — Abspringen ist die häufigste "
                "tödliche Fehlerquelle.",
                optionen=_opts(
                    ("Festhalten, in den Sitz pressen, vom Fallweg wegneigen", True),
                    ("Sofort abspringen", False),
                    ("Lenkrad maximal in die Gegenrichtung drehen", False),
                    ("Last fallen lassen, dann abspringen", False),
                ),
            ),
            FrageDef(
                text="Was zeigt das Lastdiagramm?",
                erklaerung="Zulässige Last in Abhängigkeit von LSP-Abstand und Hubhöhe.",
                optionen=_opts(
                    ("Zulässige Last abhängig von Lastschwerpunkt und Hubhöhe", True),
                    ("Wo der Stapler getankt werden muss", False),
                    ("Die Schichtpläne der Fahrer:innen", False),
                    ("Die Garantielaufzeit", False),
                ),
            ),
            FrageDef(
                text="Du entdeckst beim Check eine defekte Bremse. Was tust du?",
                erklaerung="Defekte Bremsen sind sicherheitskritisch — Stapler bis "
                "Reparatur stilllegen.",
                optionen=_opts(
                    ("Stapler stilllegen, Defekt melden, nicht fahren", True),
                    ("Nur langsam fahren — passt schon", False),
                    ("Selbst flicken und weiterfahren", False),
                    ("Nur Bescheid sagen, falls jemand fragt", False),
                ),
            ),
            FrageDef(
                text="Wie oft muss die Stapler-Unterweisung am Arbeitsplatz wiederholt werden?",
                erklaerung="DGUV V1 § 4: mindestens jährlich.",
                optionen=_opts(
                    ("Mindestens jährlich", True),
                    ("Einmal nach Erteilung des Staplerscheins", False),
                    ("Alle 5 Jahre", False),
                    ("Nur bei neuem Stapler-Modell", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #14
    KursDef(
        titel="Lieferkettengesetz (LkSG)",
        beschreibung="Pflichten nach LkSG §§ 3-10. Risikoanalyse, Sorgfaltspflichten, "
        "Beschwerdeverfahren in der Lieferkette.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Anwendungsbereich & Ziele",
                inhalt_md=(
                    "## Wann gilt das LkSG?\n\n"
                    "Seit 1.1.2024 für Unternehmen mit **>1.000 Beschäftigten** in "
                    "Deutschland. Auch kleinere Unternehmen sind faktisch betroffen, "
                    "wenn sie an LkSG-pflichtige Kunden liefern — vertragliche "
                    "Sorgfaltsanforderungen werden 'durchgereicht'.\n\n"
                    "## Geschützte Rechtspositionen\n"
                    "- Menschenrechte (Verbot Kinder-/Zwangsarbeit, Diskriminierung, "
                    "menschenwürdige Arbeitsbedingungen, Versammlungsfreiheit, "
                    "Lohnzahlung)\n"
                    "- Umweltschutz (Stockholmer + Minamata + Basler Konvention)\n\n"
                    "## Ab 2027: CSDDD\n"
                    "Die EU-Lieferkettenrichtlinie (CSDDD) erweitert den Kreis auf "
                    "Unternehmen ab 1.000 Beschäftigten EU-weit + ähnliche zivilrecht"
                    "liche Haftung."
                ),
            ),
            ModulDef(
                titel="Sorgfaltspflichten",
                inhalt_md=(
                    "## Die 9 Pflichten nach § 4 ff. LkSG\n\n"
                    "1. **Risikomanagement** etablieren\n"
                    "2. Festlegung **Zuständigkeiten** (Menschenrechtsbeauftragte/r)\n"
                    "3. **Risikoanalyse** — jährlich + anlassbezogen\n"
                    "4. **Grundsatzerklärung** zur Menschenrechtsstrategie\n"
                    "5. **Präventionsmaßnahmen** im eigenen Geschäft + bei direkten "
                    "Zulieferern (Schulungen, Vertragsklauseln, Audits)\n"
                    "6. **Abhilfemaßnahmen** bei festgestellten Verstößen\n"
                    "7. **Beschwerdeverfahren** einrichten\n"
                    "8. **Mittelbare Zulieferer** — anlassbezogene Pflicht bei "
                    "substantiierten Hinweisen\n"
                    "9. **Dokumentation + Berichterstattung** an BAFA jährlich"
                ),
            ),
            ModulDef(
                titel="Beschwerdeverfahren in der Lieferkette",
                inhalt_md=(
                    "## Was muss der Kanal können?\n\n"
                    "- **Zugang** für interne + externe Personen (Lieferanten-MA, "
                    "Anwohner, NGOs)\n"
                    "- **Vertraulichkeit** der Identität\n"
                    "- **Schutz vor Repressalien**\n"
                    "- **Verfahrensordnung** öffentlich verfügbar (Webseite)\n"
                    "- Auch **anonyme** Hinweise zulassen\n\n"
                    "## Ablauf\n"
                    "1. Eingangsbestätigung\n"
                    "2. Sachverhaltsklärung mit Hinweisgeber:in\n"
                    "3. Erörterung mit den Beteiligten\n"
                    "4. **Abhilfemaßnahmen** + Rückmeldung\n\n"
                    "Häufig ist das LkSG-Beschwerdeverfahren mit dem HinSchG-Kanal "
                    "**zusammengeführt** — ein einheitliches Portal."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Ab welcher Unternehmensgröße gilt das LkSG seit 2024?",
                erklaerung="LkSG: ab 1.000 Beschäftigten in Deutschland. Kleinere "
                "Unternehmen werden faktisch über Kundenanforderungen mit erfasst.",
                optionen=_opts(
                    ("Ab 1.000 Beschäftigten in Deutschland", True),
                    ("Ab 50 Beschäftigten", False),
                    ("Ab dem 1. Beschäftigten", False),
                    ("Erst ab 10.000 Beschäftigten", False),
                ),
            ),
            FrageDef(
                text="Welche Rechtspositionen sind durch das LkSG geschützt?",
                erklaerung="Menschenrechte (Kern-Arbeitsnormen der ILO) plus zentrale "
                "Umweltabkommen.",
                optionen=_opts(
                    ("Menschenrechte (Kinder-/Zwangsarbeit, Lohn, Diskriminierung) + bestimmte Umweltrechte", True),
                    ("Nur Datenschutzrechte", False),
                    ("Nur Patentrechte der Lieferanten", False),
                    ("Nur das deutsche Arbeitsrecht", False),
                ),
            ),
            FrageDef(
                text="Was ist die jährliche Berichts-Pflicht des LkSG?",
                erklaerung="Bericht an das BAFA (Bundesamt für Wirtschaft und Ausfuhrkontrolle), "
                "+ Veröffentlichung auf der Unternehmenswebseite.",
                optionen=_opts(
                    ("Jährlicher Bericht an das BAFA + Veröffentlichung auf der Webseite", True),
                    ("Nur ein interner Bericht", False),
                    ("Bericht an die EU-Kommission alle 5 Jahre", False),
                    ("Keine — LkSG hat keine Berichtspflicht", False),
                ),
            ),
            FrageDef(
                text="Was muss der LkSG-Beschwerdekanal mindestens leisten?",
                erklaerung="Anonyme Zugänglichkeit, Vertraulichkeit, Schutz vor "
                "Repressalien — ähnlich HinSchG.",
                optionen=_opts(
                    ("Anonyme Meldung + Identitätsschutz + Schutz vor Repressalien + öffentliche Verfahrensordnung", True),
                    ("Nur eine Mail-Adresse beim Pförtner", False),
                    ("Eine Hotline, die nur intern erreichbar ist", False),
                    ("Eine reine Beschwerde-Kasse für Bargeld-Eingänge", False),
                ),
            ),
            FrageDef(
                text="Welche Konsequenzen drohen bei LkSG-Verstößen?",
                erklaerung="Bußgelder bis 2 % Jahresumsatz (bei umsatzstarken Firmen), "
                "Ausschluss von öffentlichen Aufträgen bis 3 Jahre.",
                optionen=_opts(
                    ("Bußgelder bis zu 2 % des Jahresumsatzes + Vergabeausschluss bis 3 Jahre", True),
                    ("Eine schriftliche Mahnung", False),
                    ("Es gibt keine Sanktionen", False),
                    ("Nur ein PR-Schaden", False),
                ),
            ),
            FrageDef(
                text="Bezieht sich das LkSG auch auf indirekte Zulieferer?",
                erklaerung="§ 9 LkSG: anlassbezogen — bei substantiierten Hinweisen auf "
                "Verstöße muss auch in der vorgelagerten Lieferkette gehandelt werden.",
                optionen=_opts(
                    ("Ja — anlassbezogen, bei substantiierten Hinweisen auf Verstöße", True),
                    ("Nein — nur direkte Lieferanten", False),
                    ("Nur Lieferanten innerhalb der EU", False),
                    ("Nur, wenn die ausdrücklich zustimmen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #15
    KursDef(
        titel="Geldwäscheprävention (GwG)",
        beschreibung="Grundlagen Geldwäschegesetz (§ 6 GwG) + § 261 StGB. "
        "Verdachtsmerkmale, KYC-Pflichten, Meldewege FIU.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Was ist Geldwäsche?",
                inhalt_md=(
                    "## Definition\n\n"
                    "**Einschleusen illegal erworbener Vermögenswerte** in den "
                    "legalen Wirtschaftskreislauf. § 261 StGB: bis 5 Jahre Freiheits"
                    "strafe.\n\n"
                    "## Klassische 3 Phasen\n"
                    "1. **Placement** — Bargeld in das Finanzsystem einbringen\n"
                    "2. **Layering** — Verschleierung durch Vielzahl von Transaktionen\n"
                    "3. **Integration** — 'sauberes' Geld wird wieder investiert\n\n"
                    "## Vortaten\n"
                    "Seit 2021 sind ALLE Straftaten Vortat (vorher Katalog) — "
                    "Drogenhandel, Steuerhinterziehung, Korruption, Menschenhandel etc.\n\n"
                    "## Verpflichtete nach § 2 GwG\n"
                    "- Banken, Versicherungen, Notar:innen, Rechtsanwält:innen\n"
                    "- Steuerberatung, Immobilienmakler:innen\n"
                    "- Güterhändler:innen bei Bargeldgeschäften ≥ 10.000 €\n"
                    "- Kunsthandel ab 10.000 €"
                ),
            ),
            ModulDef(
                titel="Verdachtsmerkmale erkennen",
                inhalt_md=(
                    "## Typische Warnzeichen\n\n"
                    "- **Bargeld** in ungewöhnlich hohen Summen\n"
                    "- **Smurfing** — Aufteilung knapp unter Meldegrenze (z. B. mehrere "
                    "9.900 €-Beträge)\n"
                    "- **Vorkasse + Rückerstattung** als Geldfluss-Trick\n"
                    "- **Drittzahlungen** — Rechnung an A, Zahlung von B (ohne Erklärung)\n"
                    "- **Komplexe Konzernstrukturen** in Steueroasen\n"
                    "- **Wirtschaftlich Berechtigter unklar** oder oft wechselnd\n"
                    "- **Eile + Vermeidung von Identifikation**\n"
                    "- Zahlung **aus Hochrisikoländern** (FATF-Listen)\n\n"
                    "## Kein Pauschal-Verdacht\n"
                    "Bargeld + Eile allein sind kein Verdacht — der **Gesamtkontext** "
                    "muss ein 'nicht erklärbares Bild' ergeben."
                ),
            ),
            ModulDef(
                titel="KYC & Meldepflicht",
                inhalt_md=(
                    "## Know-Your-Customer (§ 10 GwG)\n\n"
                    "Vor Geschäftsbeziehung / bei Schwellenwert-Geschäften:\n"
                    "- **Identifizierung** der Vertragspartei (Ausweisdokument)\n"
                    "- **Wirtschaftlich Berechtigte/n** ermitteln (>25 % Anteil)\n"
                    "- **Zweck** der Geschäftsbeziehung erfassen\n"
                    "- **Politisch exponierte Personen (PEP)** → verstärkte Sorgfalt\n\n"
                    "## Meldepflicht — Financial Intelligence Unit (FIU)\n\n"
                    "Beim Verdacht **unverzüglich** per `goAML`-Portal an die FIU melden:\n"
                    "- Auch bei nicht ausgeführter Transaktion\n"
                    "- Auch ohne Beweise — Verdacht reicht\n"
                    "- **Geheimhaltungspflicht** — Kunde darf NICHT informiert werden "
                    "('Tipping-off-Verbot')\n\n"
                    "## Schutz für Meldende\n"
                    "Gutgläubige Meldung schließt zivil-/strafrechtliche Haftung aus "
                    "(§ 48 GwG)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Ab welcher Bargeld-Schwelle ist ein Güterhändler GwG-verpflichtet?",
                erklaerung="§ 2 Abs. 1 Nr. 16 GwG: 10.000 € Bargeldschwellenwert.",
                optionen=_opts(
                    ("Ab 10.000 € Bargeld pro Transaktion", True),
                    ("Ab 100 €", False),
                    ("Ab 1.000.000 €", False),
                    ("Es gibt keine Schwelle", False),
                ),
            ),
            FrageDef(
                text="Was ist 'Smurfing'?",
                erklaerung="Aufteilung einer großen Summe in viele kleinere unter der "
                "Meldegrenze, um die Identifikation zu vermeiden.",
                optionen=_opts(
                    ("Aufteilung einer Geldsumme in kleinere Beträge unter der Meldegrenze", True),
                    ("Wenn ein Schlumpf die Kasse macht", False),
                    ("Eine Form der Steueroptimierung", False),
                    ("Ein Trick beim Online-Banking", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'Tipping-off-Verbot'?",
                erklaerung="§ 47 GwG: Kunde darf nicht informiert werden, dass eine "
                "Verdachtsmeldung gemacht wurde — Strafbarkeit.",
                optionen=_opts(
                    ("Verbot, den Kunden über eine Verdachtsmeldung zu informieren", True),
                    ("Verbot, Trinkgeld anzunehmen", False),
                    ("Hinweis, beim Bowling nicht zu schummeln", False),
                    ("Pflicht, in jedem Falle zu melden", False),
                ),
            ),
            FrageDef(
                text="Wer ist der 'wirtschaftlich Berechtigte' nach GwG?",
                erklaerung="Natürliche Person, die letztlich >25 % der Anteile hält oder "
                "die Kontrolle ausübt (§ 3 GwG).",
                optionen=_opts(
                    ("Natürliche Person mit >25 % Anteil oder Kontrolle über die juristische Person", True),
                    ("Die Hausbank des Unternehmens", False),
                    ("Der Geschäftsführer", False),
                    ("Der größte Kunde", False),
                ),
            ),
            FrageDef(
                text="Wem wird ein Geldwäsche-Verdacht in Deutschland gemeldet?",
                erklaerung="Financial Intelligence Unit (FIU) beim Zoll, per goAML-Portal.",
                optionen=_opts(
                    ("Der Financial Intelligence Unit (FIU)", True),
                    ("Dem Bundeskriminalamt direkt", False),
                    ("Der eigenen Hausbank", False),
                    ("Niemandem — selbst entscheiden", False),
                ),
            ),
            FrageDef(
                text="Eine 'Politisch exponierte Person' (PEP) ist:",
                erklaerung="Personen in herausgehobener öffentlicher Funktion + ihre Angehörigen "
                "— mit erhöhtem Korruptionsrisiko (§ 1 Abs. 12 GwG).",
                optionen=_opts(
                    ("Person mit herausgehobener öffentlicher Funktion (Minister:in, Botschafter:in …) und deren engste Angehörige", True),
                    ("Jede:r Wähler:in", False),
                    ("Eine Person, die schon mal in der Tagesschau war", False),
                    ("Ein Influencer mit politischen Posts", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #16
    KursDef(
        titel="Schweißen & Heißarbeiten",
        beschreibung="Schutzunterweisung Schweißen/Brennschneiden/Trennen nach "
        "DGUV Regel 100-500 Kapitel 2.26. Erlaubnisschein, Brand-/Explosions"
        "schutz, Atemwege/Strahlung.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Erlaubnisschein für feuergefährliche Arbeiten",
                inhalt_md=(
                    "## Wann braucht es einen Schein?\n\n"
                    "Außerhalb dafür vorgesehener **Schweißerwerkstätten** und überall "
                    "wo Brand-/Explosionsgefahr besteht — z. B.:\n"
                    "- In der Produktion (Holz, Lacke, Kartonage)\n"
                    "- An/in Behältern mit Restinhalt\n"
                    "- Auf Baustellen\n"
                    "- In ATEX-Bereichen\n\n"
                    "## Inhalt des Erlaubnisscheins\n"
                    "- Arbeitsort, Art der Arbeit\n"
                    "- Beteiligte Personen + Brandwache\n"
                    "- Schutzmaßnahmen (Löschmittel, Abdeckung, Entfernen brennbarer "
                    "Stoffe in 10 m Radius)\n"
                    "- **Brandwache** während + mindestens 2 Stunden nach Arbeitsende\n"
                    "- Unterschrift Auftraggeber + Ausführender"
                ),
            ),
            ModulDef(
                titel="Brand- und Explosionsschutz",
                inhalt_md=(
                    "## Funkenflug-Risiko\n\n"
                    "Schweißfunken fliegen **bis 10 m weit** und glühen bei "
                    "Schlackeperlen mehrere Sekunden. Reicht für:\n"
                    "- Anzünden von Staub, Papier, Holzspänen\n"
                    "- Glimmbrand in Ritzen, der erst Stunden später ausbricht\n\n"
                    "## Schutzmaßnahmen\n"
                    "- **Brennbares entfernen** in 10 m Radius (sonst abdecken mit "
                    "Schweißerdecke)\n"
                    "- **Ritzen + Öffnungen** zu Nachbarräumen / Etagen abdichten\n"
                    "- **Feuerlöscher** + Wasserschlauch in Reichweite\n"
                    "- **Lüftung** beachten — Funkenflug kann durch Luftzug verstärkt werden\n\n"
                    "## Behälter mit Restinhalten\n"
                    "**NIEMALS** an Behältern schweißen, die brennbare/explosive "
                    "Reste enthalten **könnten** — selbst wenn 'leer'. "
                    "Erst freimessen lassen oder mit Stickstoff inertisieren."
                ),
            ),
            ModulDef(
                titel="Atemwege & Strahlenschutz",
                inhalt_md=(
                    "## Schweißrauch ist CMR-Stoff\n\n"
                    "TRGS 528 stuft viele Schweißrauche als **krebserzeugend** "
                    "(K1/K2 Edelstahl, K3 Stahl).\n\n"
                    "## Schutz\n"
                    "- **Punktabsaugung** so nah wie möglich an der Schweißstelle\n"
                    "- **Schweißerhelm mit Frischluft** wenn Absaugung nicht reicht\n"
                    "- FFP3 nur als Notlösung\n\n"
                    "## Strahlenschutz\n"
                    "- **UV-Strahlung** vom Lichtbogen → Schweißerblende (DIN 4647, "
                    "Schutzstufen 9-15 je nach Stromstärke)\n"
                    "- **IR-Strahlung** → Hitzeschutzkleidung\n"
                    "- **Gehörschutz** beim Plasmaschneiden\n\n"
                    "## Verbrennung 'Verblitzung'\n"
                    "Häufig nach Schweißarbeiten ohne Blende — Hornhautentzündung, "
                    "sehr schmerzhaft, klingt nach 24-48 h ab. Augen ruhigstellen, "
                    "Arzt aufsuchen."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wann ist ein Erlaubnisschein für Schweißarbeiten Pflicht?",
                erklaerung="Außerhalb der dafür eingerichteten Schweißerwerkstätten — "
                "überall wo Brand-/Explosionsgefahr besteht.",
                optionen=_opts(
                    ("Außerhalb der Schweißerwerkstatt oder bei Brand-/Explosionsgefahr", True),
                    ("Nur bei Schweißen über Kopf", False),
                    ("Nur bei MIG/MAG, nicht bei WIG", False),
                    ("Nie — Schweißer sind Profis", False),
                ),
            ),
            FrageDef(
                text="Wie weit kann Funkenflug brennbare Stoffe entzünden?",
                erklaerung="Bis ca. 10 m — daher ist der Sicherheits-Radius 10 m für "
                "Brennbares.",
                optionen=_opts(
                    ("Bis ca. 10 m", True),
                    ("Maximal 1 m", False),
                    ("100 m", False),
                    ("Nur direkt an der Schweißstelle", False),
                ),
            ),
            FrageDef(
                text="Wie lange muss eine Brandwache nach Ende der Schweißarbeit aufrechterhalten werden?",
                erklaerung="Mindestens 2 Stunden — Glimmbrände können Stunden später ausbrechen.",
                optionen=_opts(
                    ("Mindestens 2 Stunden", True),
                    ("Sofort beendet — Schweißbrenner ist aus", False),
                    ("Bis Feierabend, dann alle nach Hause", False),
                    ("Es braucht keine Brandwache", False),
                ),
            ),
            FrageDef(
                text="Was tust du an einem 'leeren' Tank mit Restöl-Verdacht?",
                erklaerung="Niemals einfach drauflos schweißen — explosionsfähige Atmosphäre "
                "muss durch Freimessung/Inertisierung ausgeschlossen werden.",
                optionen=_opts(
                    ("Erst freimessen oder inertisieren lassen, dann arbeiten", True),
                    ("Schnell schweißen, bevor sich Dämpfe sammeln", False),
                    ("Mit Wasser kühlen, dann schweißen", False),
                    ("Genügt — 'leer' heißt 'leer'", False),
                ),
            ),
            FrageDef(
                text="Was ist die größte Gesundheitsgefahr von Edelstahl-Schweißrauch?",
                erklaerung="Chrom(VI) und Nickel im Edelstahlrauch sind krebserzeugend "
                "(TRGS 528, K1).",
                optionen=_opts(
                    ("Krebs erzeugender Effekt (CMR) durch Chrom(VI) + Nickel", True),
                    ("Allergische Reaktionen sind die Hauptgefahr", False),
                    ("Geruchsbelästigung", False),
                    ("Keine — Schweißrauch ist harmlos", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'Verblitzung'?",
                erklaerung="Hornhautentzündung durch UV-Strahlung vom Lichtbogen ohne "
                "ausreichende Augenabschirmung.",
                optionen=_opts(
                    ("Schmerzhafte Hornhautentzündung durch UV-Strahlung des Lichtbogens", True),
                    ("Ein Trinkspiel nach Feierabend", False),
                    ("Eine Form von Stromschlag", False),
                    ("Wenn der Lichtbogen die Sicherung herausschlägt", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #17
    KursDef(
        titel="Ladungssicherung",
        beschreibung="Pflichtunterweisung Versand-/Fahrpersonal nach § 22 StVO + DGUV "
        "Vorschrift 70. Physik der Sicherung, Hilfsmittel & Stauplan.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Physik der Ladungssicherung",
                inhalt_md=(
                    "## Beschleunigungskräfte\n\n"
                    "Beim Bremsen, Beschleunigen und Kurvenfahren wirken auf die "
                    "Ladung erhebliche Kräfte:\n\n"
                    "| Richtung | Faktor | Beispiel |\n"
                    "|---|---|---|\n"
                    "| Nach vorn (Bremsen) | **0,8 g** | Eine 1 t Last 'will' 800 kg nach vorn |\n"
                    "| Nach hinten (Beschleunigung) | 0,5 g | |\n"
                    "| Seitlich (Kurven) | **0,5 g** | |\n\n"
                    "Diese Kräfte muss die Ladungssicherung **kompensieren**.\n\n"
                    "## VDI 2700 — der Standard\n"
                    "Verbindliche technische Norm für Ladungssicherung im Straßenverkehr. "
                    "Definiert formschlüssige + kraftschlüssige Sicherungsmethoden."
                ),
            ),
            ModulDef(
                titel="Hilfsmittel, Stauplan, Verantwortung",
                inhalt_md=(
                    "## Sicherungsmethoden\n\n"
                    "- **Formschluss** — Ladung an Stirnwand, dichtes Verstauen, "
                    "Sperrbalken — KEIN Spalt\n"
                    "- **Kraftschluss** (Niederzurren) — Zurrgurte mit Vorspannkraft (STF)\n"
                    "- **Direktzurren** (Diagonal-/Schräg-/Niederzurren) — Gurte verhindern "
                    "Bewegung direkt\n\n"
                    "## Hilfsmittel\n"
                    "- **Zurrgurte** nach EN 12195-2, regelmäßig prüfen (max 4 Jahre, "
                    "Einsturzgurt nach Schäden weg)\n"
                    "- **Anti-Rutsch-Matten** (Reibwert µ erhöhen)\n"
                    "- **Keile, Sperrbalken, Ladegestelle**\n"
                    "- **Netze + Planen**\n\n"
                    "## Verantwortung (§ 22 StVO + § 31 StVZO)\n"
                    "- **Fahrer:in** — Kontrollpflicht, kann selbst bei sicherer Verladung "
                    "haften wenn sie/er nicht prüft\n"
                    "- **Verlader** (Absender, Versandabteilung) — Hauptverantwortung\n"
                    "- **Halter** — Auswahl geeignetes Fahrzeug\n\n"
                    "Bußgelder: bis 75 € + 1 Punkt bei einfacher Schlechtsicherung, "
                    "bis 235 € + Fahrverbot bei Gefährdung."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Kraft 'will' eine 1 t Last beim Vollbremsen nach vorn?",
                erklaerung="0,8 g — also 800 kg Massekraft nach vorn.",
                optionen=_opts(
                    ("Etwa 800 kg (0,8 g)", True),
                    ("Genau 100 kg", False),
                    ("Nur die Erdanziehung", False),
                    ("Keine — sie steht ja auf dem LKW", False),
                ),
            ),
            FrageDef(
                text="Was ist Formschluss?",
                erklaerung="Lückenlose Stapelung an feste Aufbauten — keine Bewegungsfreiheit.",
                optionen=_opts(
                    ("Lückenloses Verstauen, sodass die Ladung sich nicht bewegen kann", True),
                    ("Eine schöne Stauform", False),
                    ("Verzurren mit doppeltem Gurt", False),
                    ("Wenn das Logo nach vorn zeigt", False),
                ),
            ),
            FrageDef(
                text="Wann muss ein Zurrgurt ausgesondert werden?",
                erklaerung="Nach EN 12195-2: bei Beschädigungen am Gurtband oder Beschlag — "
                "kein Reparaturversuch.",
                optionen=_opts(
                    ("Bei Einschnitten, Rissen, Hitzeschäden, defekter Ratsche", True),
                    ("Nach jedem Einsatz", False),
                    ("Erst nach 10 Jahren", False),
                    ("Nie — Zurrgurte halten ewig", False),
                ),
            ),
            FrageDef(
                text="Welche Strafe droht bei ungesicherter Gefährdung des Straßenverkehrs?",
                erklaerung="StVO-Bußgeldkatalog: bis 235 € + 1 Punkt + Fahrverbot.",
                optionen=_opts(
                    ("Bis 235 € + 1 Punkt + ggf. Fahrverbot", True),
                    ("Eine mündliche Verwarnung", False),
                    ("Nur Schadenersatz", False),
                    ("Keine — Privatangelegenheit", False),
                ),
            ),
            FrageDef(
                text="Wer trägt die Hauptverantwortung für ordnungsgemäße Ladungssicherung?",
                erklaerung="Verlader (Absender, Versandabteilung) — der/die Fahrer:in hat "
                "aber zusätzlich Kontrollpflicht.",
                optionen=_opts(
                    ("Verlader (Absender) trägt Hauptverantwortung, Fahrer:in hat Kontrollpflicht", True),
                    ("Nur der/die Fahrer:in", False),
                    ("Nur der Halter", False),
                    ("Die Werkstatt", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #18
    KursDef(
        titel="Exportkontrolle & Sanktionen",
        beschreibung="Pflichtschulung für Versand/Vertrieb nach AWG + EU-Dual-Use-VO "
        "2021/821. Embargos, Sanktionslisten-Prüfung, Dual-Use-Güter.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Wer ist betroffen, was ist Exportkontrolle?",
                inhalt_md=(
                    "## Rechtsgrundlagen\n\n"
                    "- **AWG** (Außenwirtschaftsgesetz) + AWV — Deutschland\n"
                    "- **EU-Dual-Use-VO 2021/821** — gilt direkt EU-weit\n"
                    "- **Sanktionsverordnungen** — EU + UN (Russland, Iran, Nordkorea u. a.)\n\n"
                    "## Wer ist betroffen?\n\n"
                    "JEDER Versand außerhalb der EU + bestimmte EU-interne Lieferungen "
                    "(z. B. Waffen) + jede Software-/Technologie-Übermittlung (auch "
                    "Cloud-Zugang, Konstruktionspläne per E-Mail!).\n\n"
                    "## Drei Hauptfragen\n"
                    "1. **Was** wird geliefert? → Güter-Klassifizierung (Ausfuhrlisten)\n"
                    "2. **Wohin** geht es? → Embargo-Liste\n"
                    "3. **An wen** geht es? → Sanktionslisten-Prüfung"
                ),
            ),
            ModulDef(
                titel="Sanktionslisten-Prüfung",
                inhalt_md=(
                    "## Welche Listen?\n\n"
                    "- **EU-Sanktionen** (Annex I bis Annex XX der jeweiligen VO)\n"
                    "- **UN Security Council Consolidated List**\n"
                    "- **OFAC SDN List** (USA — relevant für USD-Geschäfte und Dual-Use)\n\n"
                    "## Pflicht\n"
                    "Vor jedem **neuen Kunden, neuen Lieferanten, neuen Vertragspartner** "
                    "Prüfung gegen Listen. Auch bestehende werden regelmäßig (täglich) "
                    "gescreent.\n\n"
                    "## Tools\n"
                    "Halbautomatische Screening-Lösungen (Compliance-Catalyst, EBA Clearing, "
                    "interne ERP-Module). Ergebnis: 'Hit' → Compliance prüft.\n\n"
                    "## Verbot\n"
                    "Bei **Hit**: KEINE Vertragsanbahnung, keine Lieferung. Vermögens"
                    "werte sind ggf. **einzufrieren**. Verstoß = Straftat.\n\n"
                    "## Auch indirekt!\n"
                    "Mehr als 50 % Eigentum durch eine gelistete Person → indirekte "
                    "Listung. Anteilsstrukturen prüfen."
                ),
            ),
            ModulDef(
                titel="Dual-Use-Güter & Genehmigungspflicht",
                inhalt_md=(
                    "## Was sind Dual-Use-Güter?\n\n"
                    "Güter, die **sowohl zivil als auch militärisch** verwendbar sind:\n"
                    "- Hochleistungs-Werkzeugmaschinen (5-Achs-CNC)\n"
                    "- Verschlüsselungssoftware\n"
                    "- Chemikalien\n"
                    "- Drohnen, Sensorik\n"
                    "- Bestimmte Halbleiter, Wärmebildkameras\n\n"
                    "Liste: **Anhang I der EU-VO 2021/821** (regelmäßig aktualisiert).\n\n"
                    "## Genehmigungspflicht\n\n"
                    "Vor Ausfuhr: Antrag beim **BAFA** (Bundesamt für Wirtschaft und "
                    "Ausfuhrkontrolle):\n"
                    "- Einzelgenehmigung\n"
                    "- Sammelgenehmigung\n"
                    "- Allgemeine Genehmigung (für unkritische Empfänger)\n\n"
                    "## End-Use-Verifikation\n"
                    "**Endverbleibserklärung** vom Empfänger: 'Wir setzen das Gut nicht "
                    "zur Massenvernichtung ein, geben es nicht weiter …'. Fälschung = "
                    "Straftat des Empfängers.\n\n"
                    "## Strafen\n"
                    "AWG § 18: Freiheitsstrafe 1 Monat - 5 Jahre, besonders schwere "
                    "Fälle bis 15 Jahre + Unternehmensbuße bis 1 Mio. €."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche drei Hauptfragen stehen bei jeder Ausfuhr im Vordergrund?",
                erklaerung="Was (Klassifizierung) — Wohin (Embargo) — An wen (Sanktionslisten).",
                optionen=_opts(
                    ("Was, Wohin, An wen", True),
                    ("Wieviel, Wann, Wer zahlt", False),
                    ("Erlöse, Marge, Termin", False),
                    ("Größe, Gewicht, Volumen", False),
                ),
            ),
            FrageDef(
                text="Was sind Dual-Use-Güter?",
                erklaerung="Zivil + militärisch verwendbare Güter (EU-VO 2021/821 Anhang I).",
                optionen=_opts(
                    ("Güter, die sowohl zivil als auch militärisch verwendbar sind", True),
                    ("Güter, die mit zwei Schlüsseln geöffnet werden", False),
                    ("Doppelt vorhandene Lagerartikel", False),
                    ("Güter für zwei verschiedene Kunden", False),
                ),
            ),
            FrageDef(
                text="Welche Sanktionsliste ist besonders relevant für USD-Geschäfte?",
                erklaerung="OFAC SDN (USA) — auch Nicht-US-Unternehmen können bei USD-"
                "Transaktionen über US-Banken betroffen sein (Sekundärsanktionen).",
                optionen=_opts(
                    ("OFAC SDN List (USA)", True),
                    ("Die VG-Wort-Liste", False),
                    ("Die Telefonbuch-Liste", False),
                    ("Es gibt keine US-Listen", False),
                ),
            ),
            FrageDef(
                text="Du erhältst eine Bestellung aus einem sanktionierten Land. Was tust du?",
                erklaerung="Stop und Compliance einschalten — Lieferung kann strafbar sein.",
                optionen=_opts(
                    ("Vertragsschluss anhalten, Compliance/Exportkontrolle einschalten", True),
                    ("Erst liefern, dann fragen", False),
                    ("Über ein Drittland umleiten — 'fällt nicht auf'", False),
                    ("Den Auftrag annehmen wie jeden anderen", False),
                ),
            ),
            FrageDef(
                text="Was ist eine Endverbleibserklärung?",
                erklaerung="Bestätigung des Empfängers, dass das Gut nicht für verbotene "
                "Verwendungen genutzt + nicht weitergegeben wird.",
                optionen=_opts(
                    ("Erklärung des Empfängers, das Gut nicht für verbotene Zwecke einzusetzen", True),
                    ("Eine Garantie der Werkstatt", False),
                    ("Eine Hinweise auf die Garantielaufzeit", False),
                    ("Die Bestätigung der Versandadresse", False),
                ),
            ),
            FrageDef(
                text="Gilt Exportkontrolle auch für Technologie-Übermittlung per E-Mail?",
                erklaerung="Ja — auch Software, Konstruktionspläne, technische Dokumentation, "
                "Cloud-Zugriff aus Drittstaaten fallen unter Exportkontrolle.",
                optionen=_opts(
                    ("Ja — auch Software, Pläne und Cloud-Zugriff aus Drittstaaten", True),
                    ("Nein — nur physische Güter", False),
                    ("Nur in Papierform", False),
                    ("Nur für die Software-Branche", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #19
    KursDef(
        titel="Umweltschutz & Abfallrecht",
        beschreibung="Pflichtgrundlagen Kreislaufwirtschaftsgesetz (KrWG) + ISO 14001. "
        "Abfallhierarchie, Trennung & Doku, Gefahrgut-Versand ADR-Basics.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Abfallhierarchie nach KrWG",
                inhalt_md=(
                    "## Die 5-Stufen-Hierarchie (§ 6 KrWG)\n\n"
                    "1. **Vermeidung** — Abfall gar nicht erst entstehen lassen\n"
                    "2. **Vorbereitung zur Wiederverwendung** — Reparatur, Aufbereitung\n"
                    "3. **Recycling** — stoffliche Verwertung\n"
                    "4. **Sonstige Verwertung** — z. B. energetisch (Verbrennung)\n"
                    "5. **Beseitigung** — Deponie (letzte Option)\n\n"
                    "## Klassifizierung\n\n"
                    "- **Gefährliche Abfälle** (gelb gekennzeichnet in der "
                    "Abfallverzeichnis-Verordnung AVV)\n"
                    "- Nicht-gefährliche Abfälle\n\n"
                    "## Pflichten\n"
                    "- **Andienungspflicht** (Bundesland) — gefährliche Abfälle nur an "
                    "zugelassene Entsorger\n"
                    "- **Nachweisverfahren** (eANV) — elektronisch über das ZKS-Abfall-System\n"
                    "- **Register** mit Begleitscheinen 3 Jahre aufbewahren"
                ),
            ),
            ModulDef(
                titel="Trennung & Dokumentation",
                inhalt_md=(
                    "## Typische Trennfraktionen Industrie\n\n"
                    "- **Metall** — Stahl, Buntmetall (getrennt!)\n"
                    "- **Holz** (A1 unbehandelt vs. A2-A4 belastet)\n"
                    "- **Papier/Pappe**\n"
                    "- **Folien + Verpackungen** (LDPE, HDPE, PP)\n"
                    "- **Glas**\n"
                    "- **Bioabfall**\n"
                    "- **Restmüll**\n"
                    "- **Gefährliche Abfälle** — Altöl, Lackreste, Lithium-Akkus, "
                    "ölverschmutzte Putzlappen\n\n"
                    "## Sammelbehälter\n"
                    "- Eindeutig **gekennzeichnet** mit Abfallschlüssel (AVV-Code)\n"
                    "- Geschlossen wenn flüssig/staubend\n"
                    "- **Trennung** ist Pflicht und macht Entsorgung **billiger** "
                    "(Vermischen treibt alles in die teure 'gefährlich'-Fraktion)\n\n"
                    "## Konsequenz\n"
                    "Falsche Entsorgung = Ordnungswidrigkeit, Bußgeld bis 100.000 €, "
                    "in schweren Fällen Straftat (§ 326 StGB Umweltdelikt)."
                ),
            ),
            ModulDef(
                titel="ADR-Versand & Energie/Wasser",
                inhalt_md=(
                    "## Gefahrgut-Transport (ADR)\n\n"
                    "Bei Versand gefährlicher Stoffe (Säuren, Lösemittel, Lithium-"
                    "Batterien …) gelten besondere Pflichten:\n"
                    "- Klassifizierung nach UN-Nummer\n"
                    "- Verpackungsvorschriften (UN-zertifizierte Gebinde)\n"
                    "- **Kennzeichnung** (Gefahrzettel, UN-Nummer, Klassifizierung)\n"
                    "- Beförderungspapier\n"
                    "- Bei Mengen > Schwellenwert: **Gefahrgutbeauftragte/r** Pflicht\n\n"
                    "## Energiesparen im Betrieb\n"
                    "- Stand-by-Verbraucher vermeiden (Bildschirm, Drucker abends aus)\n"
                    "- Druckluft-Leckagen melden (1 mm Loch = ~1.000 € / Jahr)\n"
                    "- Beleuchtung in selten genutzten Räumen Bewegungsmelder\n\n"
                    "## Wassersparen\n"
                    "- Leckagen melden\n"
                    "- Spül-/Reinigungsprozesse hinterfragen\n"
                    "- Kühlwasser im Kreislauf führen"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was ist die erste Stufe der Abfallhierarchie nach KrWG?",
                erklaerung="Vermeidung — der beste Abfall ist der, der gar nicht entsteht.",
                optionen=_opts(
                    ("Vermeidung", True),
                    ("Recycling", False),
                    ("Verbrennung", False),
                    ("Deponierung", False),
                ),
            ),
            FrageDef(
                text="Wo wird der elektronische Nachweis (eANV) für gefährliche Abfälle geführt?",
                erklaerung="Im ZKS-Abfall — Zentrale Koordinierungsstelle, betrieben von "
                "den Bundesländern.",
                optionen=_opts(
                    ("Im ZKS-Abfall-System", True),
                    ("In einer Excel-Tabelle des Vorgesetzten", False),
                    ("Auf einem Zettel an der Tonne", False),
                    ("Nur mündlich beim Entsorger", False),
                ),
            ),
            FrageDef(
                text="Wieso ist Abfalltrennung auch wirtschaftlich relevant?",
                erklaerung="Vermischter Abfall mit gefährlichen Bestandteilen wird komplett "
                "als gefährlich entsorgt — sehr teuer.",
                optionen=_opts(
                    ("Vermischung treibt alles in die teure 'gefährlich'-Fraktion", True),
                    ("Ist nur eine PR-Maßnahme", False),
                    ("Macht den Müll leichter", False),
                    ("Gar nicht — Trennung kostet nur Zeit", False),
                ),
            ),
            FrageDef(
                text="Was sind ölverschmutzte Putzlappen?",
                erklaerung="Gefährlicher Abfall — eigene Sammelbehälter (Sicherheitsbehälter "
                "mit Deckel, Brandschutz).",
                optionen=_opts(
                    ("Gefährlicher Abfall — separater Sammelbehälter", True),
                    ("Restmüll", False),
                    ("Wertstoff (Papier)", False),
                    ("Biomüll", False),
                ),
            ),
            FrageDef(
                text="Was muss beim ADR-Versand einer Gefahrgut-Sendung mindestens gekennzeichnet sein?",
                erklaerung="UN-Nummer + Klassifizierung + Gefahrzettel gehören zur "
                "Mindest-Kennzeichnung.",
                optionen=_opts(
                    ("UN-Nummer + Klassifizierung + Gefahrzettel-Piktogramm", True),
                    ("Nur der Empfänger", False),
                    ("Nur das Gewicht", False),
                    ("Nichts — die Versandetikette reicht", False),
                ),
            ),
            FrageDef(
                text="Eine Druckluft-Leckage von 1 mm kostet ca.:",
                erklaerung="Pro Jahr ca. 1.000 € (je nach Druck + Strompreis) — "
                "Leckagen sind oft vermeidbarer Energiefresser.",
                optionen=_opts(
                    ("Ca. 1.000 € pro Jahr", True),
                    ("Nichts — Luft ist gratis", False),
                    ("10 Mio. € pro Jahr", False),
                    ("Nur ein paar Cent", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #20
    KursDef(
        titel="ISO 9001 Qualitätsbewusstsein",
        beschreibung="Awareness-Kurs ISO 9001:2015 + IATF 16949. "
        "Prozessdenken & PDCA, Reklamations- und Audit-Verhalten.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Prozessdenken & PDCA",
                inhalt_md=(
                    "## ISO 9001 — High Level Structure\n\n"
                    "ISO 9001:2015 ist der weltweite Standard für Qualitätsmanagement"
                    "systeme. Die zehn Kapitel folgen der HLS (High Level Structure), "
                    "die auch für ISO 14001 und ISO 45001 gilt.\n\n"
                    "## PDCA-Zyklus (Deming)\n\n"
                    "- **P**lan — Ziele + Prozesse definieren\n"
                    "- **D**o — Umsetzung\n"
                    "- **C**heck — Messung + Bewertung\n"
                    "- **A**ct — Verbesserung\n\n"
                    "Wird in der ISO 9001 als Grundprinzip vorausgesetzt — auf jeder "
                    "Ebene, vom Gesamtunternehmen bis zum einzelnen Prozess.\n\n"
                    "## Prozess vs. Funktion\n\n"
                    "Klassisch: 'Abteilungen' (Einkauf, Produktion, Vertrieb). Prozessual: "
                    "End-to-End-Wertströme (Auftragsabwicklung von Bestellung bis "
                    "Auslieferung). ISO 9001 verlangt das **Prozessdenken**: Wer ist "
                    "Kunde wovon, was wird messbar gemacht."
                ),
            ),
            ModulDef(
                titel="Reklamationen & Audit-Verhalten",
                inhalt_md=(
                    "## Reklamationen sind ein Geschenk\n\n"
                    "Nur ein Bruchteil der unzufriedenen Kunden reklamiert — der Rest "
                    "wechselt schweigend zum Wettbewerb. Jede Reklamation ist eine "
                    "Chance zur Verbesserung.\n\n"
                    "## 8D-Methode\n"
                    "1. Team bilden\n"
                    "2. Problem beschreiben\n"
                    "3. **Sofortmaßnahmen**\n"
                    "4. **Ursache** ermitteln (5-Why, Ishikawa)\n"
                    "5. **Abstellmaßnahmen** wählen\n"
                    "6. **Wirksamkeit** prüfen\n"
                    "7. **Wiederholung verhindern** (System-Ebene)\n"
                    "8. **Team würdigen** + Abschluss\n\n"
                    "## Audit-Verhalten\n"
                    "- **Ruhig + sachlich** bleiben\n"
                    "- Nur **bekannte Fakten** sagen — keine Spekulation\n"
                    "- **Nichts behaupten**, was nicht dokumentiert ist\n"
                    "- Bei Unsicherheit: 'Das prüfe ich gern und melde mich' — "
                    "Nachzieh-Antworten sind OK\n"
                    "- Auditor:innen sind **keine Gegner** — sie helfen Schwachstellen "
                    "vor dem Kunden zu finden"
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was bedeutet PDCA?",
                erklaerung="Plan-Do-Check-Act, der von Deming geprägte Verbesserungszyklus.",
                optionen=_opts(
                    ("Plan, Do, Check, Act", True),
                    ("Produce, Develop, Control, Audit", False),
                    ("Promotion, Demo, Cancel, Analyse", False),
                    ("Plan, Demo, Cancel, Adjust", False),
                ),
            ),
            FrageDef(
                text="Was ist die 8D-Methode?",
                erklaerung="Strukturiertes 8-Schritte-Verfahren zur Reklamations-/"
                "Problembehandlung — Standard in Automotive (IATF 16949).",
                optionen=_opts(
                    ("Ein 8-Schritte-Verfahren zur Bearbeitung von Reklamationen", True),
                    ("Eine 8-stündige Schulung", False),
                    ("Ein Excel-Makro", False),
                    ("Eine Schweißtechnik", False),
                ),
            ),
            FrageDef(
                text="Wie verhältst du dich im Kundenaudit?",
                erklaerung="Ruhig, sachlich, faktentreu — Nachzieh-Antworten sind besser "
                "als Spekulation.",
                optionen=_opts(
                    ("Ruhig, sachlich, nur dokumentierte Fakten — bei Unsicherheit nachreichen", True),
                    ("So viel reden wie möglich, damit der Auditor müde wird", False),
                    ("Behaupten, dass alles perfekt läuft", False),
                    ("Spekulieren, damit niemand merkt, dass man unsicher ist", False),
                ),
            ),
            FrageDef(
                text="Warum ist eine Reklamation 'ein Geschenk'?",
                erklaerung="Stille Kunden wechseln einfach — eine Reklamation ist eine "
                "Chance, den Kunden zu halten + Schwachstellen aufzudecken.",
                optionen=_opts(
                    ("Sie bringt eine konkrete Verbesserungschance und Kundenrückmeldung", True),
                    ("Weil man Geld zurück bekommt", False),
                    ("Weil es eine Tortenflagge gibt", False),
                    ("Reklamationen sind kein Geschenk, sondern Ärger", False),
                ),
            ),
            FrageDef(
                text="Was ist der zentrale Gedanke des 'Prozessdenkens'?",
                erklaerung="End-to-End-Wertströme statt isolierter Abteilungs-Optimierung — "
                "Übergaben werden bewusst gestaltet.",
                optionen=_opts(
                    ("End-to-End-Wertströme über Abteilungsgrenzen statt isolierter Funktionen", True),
                    ("Schnelles Abarbeiten ohne Pausen", False),
                    ("Jede Abteilung optimiert sich allein", False),
                    ("Nur das Endprodukt zählt", False),
                ),
            ),
        ),
    ),
)


__all__ = (
    "FrageDef",
    "KATALOG",
    "KursDef",
    "ModulDef",
    "OptionDef",
)
