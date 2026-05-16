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
                    "## Worum geht es?\n\n"
                    "Die **EU-Datenschutz-Grundverordnung (DSGVO)** gilt seit dem "
                    "25. Mai 2018 unmittelbar in allen EU-Staaten. Sie regelt, "
                    "wie Unternehmen mit personenbezogenen Daten umgehen dürfen — "
                    "von der Erhebung über die Speicherung bis zur Löschung. "
                    "Ergänzt wird sie in Deutschland durch das **Bundesdatenschutz"
                    "gesetz (BDSG)**, das nationale Spezialthemen regelt "
                    "(z. B. Beschäftigtendatenschutz nach § 26 BDSG).\n\n"
                    "**Warum für uns wichtig:** Verstöße können mit bis zu "
                    "**20 Mio. €** oder **4 % des weltweiten Jahresumsatzes** "
                    "geahndet werden (Art. 83). Auch jeder/jede Mitarbeitende ist "
                    "persönlich beteiligt — wer fahrlässig Daten verliert, kann "
                    "abgemahnt oder im Wiederholungsfall gekündigt werden.\n\n"
                    "## Personenbezogene Daten — was ist das genau?\n\n"
                    "Nach **Art. 4 Abs. 1 DSGVO** sind das alle Informationen, "
                    "die sich auf eine bestimmte oder bestimmbare natürliche Person "
                    "beziehen. 'Bestimmbar' reicht — du musst nicht den Namen "
                    "kennen, es genügt, dass eine Verknüpfung möglich wäre.\n\n"
                    "| Eindeutig personenbezogen | Auf den ersten Blick 'neutral', trotzdem PB-Daten |\n"
                    "|---|---|\n"
                    "| Name, Anschrift, Geburtsdatum | IP-Adresse |\n"
                    "| E-Mail, Telefonnummer | Personalnummer + Schichtplan |\n"
                    "| Bankverbindung | KFZ-Kennzeichen auf einem Foto |\n"
                    "| Lichtbild / Stimmaufnahme | RFID-Chip im Werksausweis |\n"
                    "| Gesundheitsdaten, Religion | Cookie-IDs, Geräte-IDs |\n\n"
                    "**Besondere Kategorien (Art. 9 DSGVO)** — Gesundheit, "
                    "Religion, Gewerkschaftszugehörigkeit, biometrische Daten, "
                    "sexuelle Orientierung — sind besonders streng geschützt. "
                    "Verarbeitung nur mit ausdrücklicher Einwilligung oder "
                    "klarer gesetzlicher Grundlage (z. B. Arbeitsmedizin).\n\n"
                    "## Die drei Schutzziele\n\n"
                    "**Vertraulichkeit** — Daten sieht nur, wer sie wirklich braucht. "
                    "Beispiel: Lohnabrechnungen liegen nicht offen auf dem "
                    "Drucker, sondern werden direkt abgeholt; der Schichtplan "
                    "der Kollegen wird nicht in Whatsapp-Gruppen geteilt.\n\n"
                    "**Integrität** — Daten dürfen nicht unbemerkt verändert "
                    "werden. Beispiel: Wartungsprotokolle einer Maschine müssen "
                    "manipulationssicher abgelegt sein. Wenn jemand nachträglich "
                    "Wartungstermine fälscht, kann das im Schadensfall straf"
                    "rechtliche Folgen haben.\n\n"
                    "**Verfügbarkeit** — Berechtigte müssen die Daten bei Bedarf "
                    "erreichen. Beispiel: Backup des CRM, sodass nach einem "
                    "Server-Crash die Kundendaten innerhalb der vereinbarten Zeit "
                    "(RTO = Recovery Time Objective) wieder da sind.\n\n"
                    "## Rechtsgrundlagen für die Verarbeitung\n\n"
                    "Daten zu verarbeiten ist **immer erlaubnispflichtig** — du "
                    "brauchst eine der sechs Rechtsgrundlagen aus **Art. 6 DSGVO**:\n\n"
                    "1. **Einwilligung** der betroffenen Person (jederzeit widerrufbar)\n"
                    "2. **Vertragserfüllung** (z. B. Lieferadresse für Bestellung)\n"
                    "3. **Rechtliche Verpflichtung** (z. B. Lohnsteuerdaten ans Finanzamt)\n"
                    "4. **Lebenswichtige Interessen** (Notfall, z. B. Verkehrsunfall)\n"
                    "5. **Öffentliche Aufgabe** (selten in der Privatwirtschaft)\n"
                    "6. **Berechtigtes Interesse** (Abwägung — z. B. Werks-Videoüberwachung)\n\n"
                    "**Im Beschäftigtenkontext** zusätzlich § 26 BDSG: Verarbeitung "
                    "zur Begründung, Durchführung oder Beendigung des Arbeitsverhältnisses.\n\n"
                    "## Praxis-Check: Welche Daten verarbeitest DU täglich?\n\n"
                    "Im Industrie-Mittelstand gehören dazu typischerweise:\n"
                    "- **Personalakten** (HR, Lohnabrechnung)\n"
                    "- **Kundendaten** (Kontakte, Bestellungen, Reklamationen)\n"
                    "- **Lieferanten-/Ansprechpartnerdaten**\n"
                    "- **Zutritts- und Zeiterfassungsdaten**\n"
                    "- **Maschinen-Logs** (wenn personalisierbar — z. B. via Anmelde-PIN)\n"
                    "- **Videoüberwachung** in Werkshalle/Eingangsbereich\n"
                    "- **Telefonate** mit Kunden (Aufzeichnung nur mit Hinweis!)\n\n"
                    "Wenn du unsicher bist, ob ein Vorgang DSGVO-relevant ist: "
                    "frag den/die **Datenschutzbeauftragte:n** (DSB). Das ist "
                    "Pflicht ab 20 Mitarbeitenden mit ständiger automatisierter "
                    "Verarbeitung — bei uns ist die Rolle besetzt."
                ),
            ),
            ModulDef(
                titel="Betroffenenrechte",
                inhalt_md=(
                    "## Was Personen von uns verlangen können\n\n"
                    "Jede natürliche Person, deren Daten wir verarbeiten "
                    "(Beschäftigte, Bewerber:innen, Kund:innen, Lieferanten-"
                    "Mitarbeitende), hat sieben durchsetzbare Rechte aus "
                    "**Kapitel III der DSGVO**. Diese Rechte sind kostenlos für "
                    "die Betroffenen und müssen wir innerhalb von **einem Monat** "
                    "beantworten (Art. 12 Abs. 3) — verlängerbar um zwei weitere "
                    "Monate bei komplexen Fällen, aber nur mit schriftlicher "
                    "Begründung an die Person.\n\n"
                    "### 1. Auskunft (Art. 15)\n\n"
                    "'Welche Daten habt ihr von mir und was tut ihr damit?' Wir "
                    "müssen liefern: Kategorien der Daten, Zwecke, Empfänger, "
                    "Speicherdauer, Herkunft (wenn nicht direkt erhoben), "
                    "Hinweis auf Beschwerderecht. **Praxis:** Formular "
                    "'Auskunftsersuchen' liegt bei der DSB.\n\n"
                    "### 2. Berichtigung (Art. 16)\n\n"
                    "Falsche oder unvollständige Daten müssen korrigiert werden. "
                    "**Beispiel:** Kollege hat geheiratet → Familienname in der "
                    "Personalakte aktualisieren. Wenn er es selbst meldet, "
                    "machen wir das **unverzüglich** — keine Wartezeit auf den "
                    "nächsten Personalgesprächstermin.\n\n"
                    "### 3. Löschung / Recht auf Vergessenwerden (Art. 17)\n\n"
                    "Daten sind zu löschen, wenn:\n"
                    "- der Zweck weggefallen ist (Bewerber:in nicht eingestellt → "
                    "Bewerbungsdaten nach **6 Monaten** löschen)\n"
                    "- die Einwilligung widerrufen wurde\n"
                    "- unrechtmäßig verarbeitet wurde\n\n"
                    "**ABER:** Löschung gilt nicht, wenn gesetzliche **Aufbewah"
                    "rungspflichten** entgegenstehen — z. B. 10 Jahre für "
                    "Buchhaltungsbelege (§ 257 HGB, § 147 AO). In dem Fall werden "
                    "Daten **gesperrt** (kein operativer Zugriff mehr), erst "
                    "nach Ablauf gelöscht.\n\n"
                    "### 4. Einschränkung der Verarbeitung (Art. 18)\n\n"
                    "'Verarbeitet erstmal nichts, bis geklärt ist, ob die Daten "
                    "richtig sind.' Wird oft genutzt während eines Streits über "
                    "Datenrichtigkeit. Praktisch: Datensatz wird markiert, "
                    "Workflows ignorieren ihn.\n\n"
                    "### 5. Datenübertragbarkeit (Art. 20)\n\n"
                    "Die Person bekommt ihre Daten in einem **maschinenlesbaren "
                    "Format** (JSON, CSV, XML) und kann sie zu einem anderen "
                    "Anbieter mitnehmen. **In der Praxis im Mittelstand selten** — "
                    "betrifft v. a. Cloud-Dienste und Vertragsverhältnisse.\n\n"
                    "### 6. Widerspruch (Art. 21)\n\n"
                    "Wenn wir auf 'berechtigtes Interesse' stützen, kann die "
                    "Person widersprechen. Wir müssen dann prüfen, ob unsere "
                    "Gründe ihre Interessen überwiegen. **Direktmarketing-"
                    "Widerspruch ist absolut** — Werbe-E-Mail gestoppt, Punkt.\n\n"
                    "### 7. Recht auf Beschwerde bei der Aufsichtsbehörde\n\n"
                    "Jede Person kann sich direkt an die zuständige Datenschutz"
                    "behörde (in Bayern: BayLDA, in BW: LfDI) wenden. **Folge "
                    "für uns:** behördliche Anfrage, ggf. Bußgeldverfahren.\n\n"
                    "## Was tun, wenn so ein Antrag bei dir landet?\n\n"
                    "1. **Identität prüfen** — kein Auskunftsbescheid an Unbekannte "
                    "per E-Mail. Bei Zweifel Personalausweis oder Geheim-Frage.\n"
                    "2. **Eingang notieren** mit Datum — die Monatsfrist beginnt.\n"
                    "3. **DSB einschalten** — meistens hat die DSB Vorlagen.\n"
                    "4. **Schriftliche Antwort** (auch wenn Anfrage per Telefon kam) — "
                    "Beweissicherung.\n"
                    "5. **Auf Aufsichtsbehörde hinweisen**, falls wir die "
                    "Anfrage ablehnen.\n\n"
                    "**Ablehnung ist selten gerechtfertigt** und immer schriftlich "
                    "zu begründen. Im Zweifel: bewilligen. Eine Bewilligung kostet "
                    "uns Aufwand. Eine zu Unrecht abgelehnte Anfrage kann ein "
                    "Bußgeld kosten."
                ),
            ),
            ModulDef(
                titel="Datenpannen erkennen und melden",
                inhalt_md=(
                    "## Was ist eine Datenpanne?\n\n"
                    "Eine **Datenpanne (Data Breach)** ist jede Verletzung der "
                    "Schutzziele Vertraulichkeit, Integrität oder Verfügbarkeit "
                    "personenbezogener Daten — egal ob durch Schadsoftware, "
                    "menschliches Versehen oder höhere Gewalt.\n\n"
                    "### Typische Beispiele aus dem Mittelstand\n\n"
                    "| Vorfall | Schutzziel verletzt | Schwere |\n"
                    "|---|---|---|\n"
                    "| Notebook ohne Festplattenverschlüsselung verloren | Vertraulichkeit | hoch |\n"
                    "| Lohnabrechnung an falsche E-Mail-Adresse versandt | Vertraulichkeit | hoch |\n"
                    "| Ransomware-Befall in der HR-Abteilung | alle drei | sehr hoch |\n"
                    "| Server-Raum eingebrochen, Backups gestohlen | Vertraulichkeit, Verfügbarkeit | hoch |\n"
                    "| Brand im Archiv (Papierakten ohne Backup) | Verfügbarkeit | mittel |\n"
                    "| Kopierer-Festplatte beim Geräte-Tausch nicht gelöscht | Vertraulichkeit | hoch |\n"
                    "| Fehlversand: 50 statt 1 Adressat auf CC | Vertraulichkeit | mittel-hoch |\n"
                    "| Phishing-E-Mail beantwortet, Anmeldedaten preisgegeben | alle drei | sehr hoch |\n\n"
                    "**Eine vereitelte Datenpanne ist trotzdem meldewürdig**, "
                    "wenn auch nur kurz Zugriff bestand (z. B. E-Mail mit "
                    "Personaldaten 5 Minuten in falschem Postfach, dann zurück"
                    "gerufen — Beweis-Pflicht, dass nichts kopiert wurde).\n\n"
                    "## Die 72-Stunden-Frist (Art. 33 DSGVO)\n\n"
                    "Wenn eine Datenpanne **wahrscheinlich** zu einem Risiko für "
                    "Betroffene führt, muss sie **innerhalb von 72 Stunden** ab "
                    "Kenntnis an die zuständige Aufsichtsbehörde gemeldet werden. "
                    "Die Frist läuft ab dem Moment, in dem die Verantwortlichen "
                    "Kenntnis erlangen — nicht ab dem eigentlichen Vorfall. "
                    "Verzögerung ist nur mit Begründung möglich.\n\n"
                    "**Bei hohem Risiko für die Betroffenen** (z. B. bei Verlust "
                    "von Gesundheitsdaten oder Bankdaten) müssen auch die "
                    "**Betroffenen direkt** benachrichtigt werden (Art. 34) — "
                    "klar, verständlich, mit Hinweis auf Schutzmaßnahmen.\n\n"
                    "## Was tu ICH, wenn ich eine Datenpanne bemerke?\n\n"
                    "1. **NICHTS löschen oder vertuschen.** Beweise sichern.\n"
                    "2. **Sofort melden** — interne Hotline / DSB / IT-Sicherheit. "
                    "Auch wenn du dir nicht sicher bist, ob es 'groß genug' ist. "
                    "Die DSB entscheidet das.\n"
                    "3. **Bei Phishing-Klick**: Rechner vom Netz nehmen (LAN-Kabel "
                    "ziehen, WLAN aus), Passwort sofort ändern, IT informieren.\n"
                    "4. **Schriftlich kurz dokumentieren**: Was, Wann, Wer, Wie "
                    "bemerkt. Diese Notiz hilft der DSB bei der 72h-Meldung.\n"
                    "5. **Nicht intern 'debattieren'**, ob es Meldepflicht ist — "
                    "das ist juristische Bewertung, nicht Bauchgefühl.\n\n"
                    "## Sanktionsbeispiele aus realen Fällen\n\n"
                    "- **2019 — Krankenhaus Portugal**: 400.000 € weil zu viele "
                    "Mitarbeitende Zugriff auf Patientenakten hatten\n"
                    "- **2020 — H&M Deutschland**: 35,3 Mio. € wegen Mitarbeiter-"
                    "Überwachung (Mitschriften aus Krankenrückkehrgesprächen)\n"
                    "- **2021 — Notebooksbilliger.de**: 10,4 Mio. € wegen "
                    "Videoüberwachung im Lager ohne ausreichende Rechtsgrundlage\n\n"
                    "**Lesson:** Die Bußgelder treffen nicht 'die Großen', "
                    "sondern jede:n, der/die unsauber arbeitet. Im Schadensfall "
                    "ist eine saubere, schnelle Meldung der beste Schutz — sie "
                    "kann das Bußgeld erheblich reduzieren oder ganz abwenden."
                ),
            ),
            ModulDef(
                titel="Technisch-organisatorische Maßnahmen (TOMs)",
                inhalt_md=(
                    "## Was Art. 32 DSGVO von uns verlangt\n\n"
                    "**Technisch-organisatorische Maßnahmen (TOMs)** sind die "
                    "Schutzvorkehrungen, mit denen wir personenbezogene Daten vor "
                    "unbefugtem Zugriff, Verlust und Veränderung schützen. "
                    "Art. 32 DSGVO fordert 'angemessenes Schutzniveau' — die "
                    "konkrete Höhe richtet sich nach **Risiko, Stand der Technik, "
                    "Implementierungskosten** und Sensibilität der Daten.\n\n"
                    "Im Industrie-Mittelstand ist das Niveau höher zu setzen, "
                    "wenn z. B. Gesundheitsdaten (Arbeitsmedizin), umfangreiche "
                    "Mitarbeiter-Profile (HR-System) oder vertrauliche Konstruktions"
                    "daten in Verbindung mit Personen verarbeitet werden.\n\n"
                    "## Technische Maßnahmen — konkret bei uns\n\n"
                    "### Verschlüsselung\n\n"
                    "- **At rest** — alle Festplatten in Notebooks + Smartphones "
                    "sind verschlüsselt (BitLocker, FileVault, Android/iOS-Default). "
                    "Verlust = kein Datenabfluss.\n"
                    "- **In transit** — E-Mails an externe Empfänger nur über "
                    "TLS (Standard im Mail-Client), sensible Anhänge zusätzlich "
                    "passwort-geschützt (Passwort über zweiten Kanal: SMS, Telefon).\n"
                    "- **Datenbanken** — Backups verschlüsselt, Datenträger physisch "
                    "in abschließbaren Räumen.\n\n"
                    "### Zugriffskontrolle\n\n"
                    "- **Eindeutige Nutzerkonten** — keine geteilten Accounts "
                    "('station01') für mehrere Mitarbeitende.\n"
                    "- **Multi-Faktor-Authentifizierung (MFA)** — bei E-Mail, "
                    "VPN, Cloud, Admin-Zugängen. Pflicht für alle Mitarbeitenden "
                    "mit Zugriff auf personenbezogene Daten.\n"
                    "- **Berechtigungskonzept** nach **Least-Privilege**: jede "
                    "Person bekommt nur die Rechte, die für ihre konkrete Tätigkeit "
                    "zwingend nötig sind. Vertrieb sieht keine Lohndaten, HR "
                    "sieht keine Lieferanten-Preise.\n\n"
                    "### Backup & Wiederherstellung\n\n"
                    "- **3-2-1-Regel**: 3 Kopien der Daten, auf 2 Medien, 1 "
                    "off-site (Cloud / anderer Standort).\n"
                    "- **Restore-Test** mindestens einmal jährlich — ein Backup, "
                    "das man nie wiederhergestellt hat, ist kein verlässliches "
                    "Backup.\n\n"
                    "### Protokollierung (Logging)\n\n"
                    "Zugriffs- und Änderungslogs in sensiblen Systemen (HR, "
                    "Finanzbuchhaltung), so dass nachträglich nachvollzogen werden "
                    "kann, wer wann was getan hat. Logs selbst sind ebenfalls "
                    "personenbezogen und werden begrenzt (max. 6 Monate, dann "
                    "anonymisiert oder gelöscht).\n\n"
                    "## Organisatorische Maßnahmen\n\n"
                    "### Vertraulichkeitsverpflichtung\n\n"
                    "Alle Mitarbeitenden unterzeichnen bei Eintritt eine **Ver"
                    "pflichtung auf das Datengeheimnis** (§ 53 BDSG). Sie gilt "
                    "auch **nach Austritt** weiter — das ist wichtig: wer hier "
                    "geht, darf erlernte Daten nicht in der nächsten Firma "
                    "verwenden.\n\n"
                    "### Schulungen\n\n"
                    "Jährliche Pflicht-Schulung (Art. 39 DSGVO empfiehlt es, "
                    "die DSB-Tätigkeit dies meist umsetzt) — diese Schulung ist "
                    "Teil davon.\n\n"
                    "### Auftragsverarbeitungsverträge (AV-Verträge)\n\n"
                    "Vor jeder Zusammenarbeit mit einem Dienstleister, der für uns "
                    "personenbezogene Daten verarbeitet (Lohn-Outsourcing, "
                    "Cloud-Anbieter, Mail-Provider, externe IT-Wartung), wird ein "
                    "**AV-Vertrag nach Art. 28 DSGVO** geschlossen. Ohne diesen "
                    "Vertrag ist die Datenweitergabe rechtswidrig.\n\n"
                    "### Löschkonzept\n\n"
                    "Für jede Datenkategorie ist geregelt, wann sie zu löschen "
                    "ist (Bewerbungen 6 Monate, Personalakte 10 Jahre nach "
                    "Austritt, Kundendaten siehe AGB). Automatisierte Löschung "
                    "wo technisch möglich, sonst Erinnerung im Kalender.\n\n"
                    "## Was DU beachten solltest — Alltags-Checkliste\n\n"
                    "- 🔒 Bildschirm immer sperren beim Verlassen (Win+L)\n"
                    "- 📋 'Clean Desk' — keine Personaldaten unbeaufsichtigt "
                    "liegen lassen, auch nicht für 2 Minuten Kaffee\n"
                    "- 🗑️ Vertrauliche Papiere in den **abschließbaren Daten"
                    "schutz-Container**, NICHT in den normalen Papiermüll\n"
                    "- 🔌 Keine **privaten USB-Sticks** an Dienstgeräte und "
                    "umgekehrt — Malware-Risiko\n"
                    "- 📱 **Diensthandy** nicht ungesperrt rumliegen lassen, "
                    "nicht der Familie zur Nutzung geben\n"
                    "- 🎫 Werks-Ausweise nicht weitergeben\n"
                    "- 🌐 Bei VPN-Unsicherheit (Hotel-WLAN, Bahn) **immer VPN** "
                    "aktiviert vor Zugriff auf Firmendaten\n"
                    "- ❓ Im Zweifel: DSB fragen, **bevor** etwas Datenschutz-"
                    "Relevantes passiert"
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
                    "## Warum Passwörter heute noch wichtig sind\n\n"
                    "Bei rund **80 % aller Cyber-Angriffe** auf Unternehmen ist das "
                    "erste Einfallstor ein kompromittiertes Passwort — entweder "
                    "abgefangen, erraten, in einem Daten-Leak veröffentlicht oder "
                    "vom Mitarbeitenden selbst preisgegeben. **Du** entscheidest "
                    "mit deinem Passwort über die Sicherheit aller, weil ein "
                    "geknackter Account oft als Sprungbrett ins ganze Netzwerk dient.\n\n"
                    "## Was ein gutes Passwort heute ausmacht\n\n"
                    "Die alten BSI-Regeln ('mindestens 8 Zeichen, mit Sonderzeichen, "
                    "alle 90 Tage wechseln') sind **überholt**. Aktuelle Empfehlung "
                    "(BSI 2024, NIST SP 800-63B):\n\n"
                    "- **Länge schlägt Komplexität** — mindestens **12 Zeichen**, "
                    "besser 16+. Ein 16-Zeichen-Passwort mit nur Kleinbuchstaben "
                    "ist sicherer als ein 8-Zeichen-Passwort mit allem Drum und Dran.\n"
                    "- **Passphrase statt Passwort** — vier zufällige Wörter sind "
                    "leicht zu merken UND schwer zu brechen, z. B. "
                    "`Lampe!Fahrrad-Schraubenzieher_Wolke3` (Achtung: hier nur "
                    "als Beispiel, nicht real verwenden).\n"
                    "- **Pro Dienst ein eigenes Passwort** — wer dasselbe Passwort "
                    "für 5 Dienste nutzt und einer wird gehackt, hat 5 kompromittierte "
                    "Accounts.\n"
                    "- **Keine Wörterbuchwörter** ohne Anpassung, keine Geburtsdaten, "
                    "keine Namen von Haustieren/Kindern (steht alles auf Facebook).\n"
                    "- **Passwort-Manager** sind heute Standard: Bitwarden (Open-"
                    "Source, kostenlos), 1Password, KeePassXC. Du musst dir nur "
                    "noch EIN gutes Master-Passwort merken.\n\n"
                    "**Wechsel-Intervalle:** Regelmäßige Pflicht-Wechsel sind out — "
                    "sie zwingen Nutzer zu schlechten Mustern (`Sommer2025!`, "
                    "`Sommer2026!`). Stattdessen: Wechsel **anlassbezogen** — bei "
                    "Verdacht auf Leak, nach Phishing-Klick, beim Wechsel auf "
                    "ein neues Gerät.\n\n"
                    "## Multi-Faktor-Authentifizierung (MFA)\n\n"
                    "MFA ist die einzige Maßnahme, die **selbst ein geleaktes "
                    "Passwort unschädlich macht**. Microsoft hat 2019 ausgewertet: "
                    "Wer MFA aktiv hat, blockt **99,9 % aller automatisierten "
                    "Account-Attacken** ab.\n\n"
                    "### Die drei Faktoren-Typen\n\n"
                    "| Faktor | Beispiele | Sicherheit |\n"
                    "|---|---|---|\n"
                    "| Wissen (du weißt) | Passwort, PIN, Geheim-Frage | gering |\n"
                    "| Besitz (du hast) | Smartphone-App, FIDO2-Stick, Smartcard | mittel-hoch |\n"
                    "| Inhärenz (du bist) | Fingerabdruck, Gesicht, Iris | hoch |\n\n"
                    "MFA = **mindestens zwei verschiedene** Faktoren — typisch "
                    "Passwort + Smartphone-App.\n\n"
                    "### Welche MFA-Methode wählen?\n\n"
                    "**1. Hardware-Token (FIDO2 / YubiKey)** — Goldstandard. Nicht "
                    "phishbar (Token verifiziert die Domain). Für Admin-Accounts "
                    "und Schlüsselrollen empfohlen.\n\n"
                    "**2. TOTP-App** (Microsoft Authenticator, Google Authenticator, "
                    "Aegis, 2FAS) — generiert 6-stelligen Code, der alle 30 s "
                    "wechselt. Sehr gute Sicherheit, weit verbreitet.\n\n"
                    "**3. Push-Benachrichtigung** ('Anmeldung bestätigen?') — "
                    "bequem, aber **Vorsicht vor 'MFA-Fatigue'-Angriffen**: der "
                    "Angreifer bombardiert mit Anfragen, bis der/die Nutzer:in "
                    "genervt zustimmt. Immer prüfen: Ist die Anmeldung gerade "
                    "von mir ausgelöst?\n\n"
                    "**4. SMS-Code** — **vermeiden**, wenn andere Faktoren verfügbar "
                    "sind. SIM-Swapping (Angreifer übernimmt deine Telefonnummer) "
                    "ist eine echte Bedrohung. Nur als Notfall-Fallback.\n\n"
                    "### Recovery-Codes\n\n"
                    "Beim Einrichten von MFA bekommst du **8-10 Einmal-Codes**. "
                    "Diese ausdrucken und in einem **physisch sicheren Ort** "
                    "aufbewahren (Tresor zuhause, NICHT im selben Passwort-Manager). "
                    "Sie sind dein letzter Rettungsanker bei Verlust des Tokens.\n\n"
                    "## Praxis-Beispiel\n\n"
                    "Kollege erhält morgens eine Slack-Nachricht: 'Hey, ich hab "
                    "mein Passwort vergessen, kannst du mir kurz deins für den "
                    "CRM-Zugang geben? Brauche nur 5 Minuten.' → **NIEMALS** "
                    "Passwörter weitergeben, auch nicht 'kurz'. Stattdessen: "
                    "IT-Support kann ein temporäres Passwort vergeben oder einen "
                    "MFA-Reset durchführen."
                ),
            ),
            ModulDef(
                titel="Phishing erkennen",
                inhalt_md=(
                    "## Was Phishing ist und warum es funktioniert\n\n"
                    "**Phishing** ist das gezielte Vortäuschen einer vertrauens"
                    "würdigen Identität (Bank, IT-Support, Vorgesetzte:r, "
                    "Lieferant), um an Daten, Passwörter oder Geld zu kommen. "
                    "Es funktioniert, weil es **menschliche Reaktionen** ausnutzt: "
                    "Eile, Autorität, Angst, Hilfsbereitschaft.\n\n"
                    "**Realität für mittelständische Industrieunternehmen:** "
                    "Etwa **30 % der zielgerichteten Cyber-Angriffe** auf den "
                    "deutschen Mittelstand beginnen mit einer Phishing-Mail. "
                    "Schaden pro Vorfall: oft im **mittleren sechsstelligen Bereich** "
                    "(Lösegeld, Betriebsunterbrechung, Datenwiederherstellung, "
                    "Reputationsverlust).\n\n"
                    "## Die acht typischen Indikatoren\n\n"
                    "### 1. Dringlichkeit + Drohung\n\n"
                    "'Ihr Konto wird **in 24 Stunden gesperrt**, wenn Sie nicht "
                    "sofort handeln.' Echte Banken/Behörden setzen keine Stunden-"
                    "Fristen per E-Mail. **Eile ist Manipulation.**\n\n"
                    "### 2. Unpersönliche Anrede\n\n"
                    "'Sehr geehrter Kunde', 'Lieber Nutzer'. Echte Kommunikation "
                    "mit dir nutzt deinen Namen — und zwar richtig geschrieben.\n\n"
                    "### 3. Verdächtige Absenderadresse\n\n"
                    "Der angezeigte **Name** kann beliebig gefälscht werden — "
                    "die eigentliche **E-Mail-Adresse** ist entscheidend. "
                    "Beispiele:\n"
                    "- `paypal-support@pay-pal.com` (falsche Domain mit Bindestrich)\n"
                    "- `service@payp4l.de` (Zahl statt Buchstabe)\n"
                    "- `info@paypal.security-alert.com` (paypal ist nur Subdomain)\n\n"
                    "Im E-Mail-Programm im Zweifel auf den Absender klicken — "
                    "die volle Adresse erscheint. Bei Outlook: Hover, dann hover-"
                    "Vorschau zeigt die echte Adresse.\n\n"
                    "### 4. Verdächtige Links\n\n"
                    "**Niemals klicken ohne vorher zu prüfen.** Mauszeiger über "
                    "den Link, am unteren Bildschirmrand erscheint die echte URL. "
                    "Mobil: Link lange drücken, in der Vorschau die URL ansehen.\n\n"
                    "Roter Alarm bei:\n"
                    "- URL-Verkürzern (`bit.ly`, `tinyurl`)\n"
                    "- Domains mit ungewöhnlichen Endungen (`.tk`, `.xyz`, `.zip`)\n"
                    "- IP-Adressen statt Domain (`http://178.32.99.1/...`)\n"
                    "- Falsche Schreibweise einer bekannten Domain\n\n"
                    "### 5. Anhänge\n\n"
                    "Klassische Malware-Träger: `.exe`, `.scr`, `.bat`, `.cmd`, "
                    "`.zip`, `.iso`, `.docm`, `.xlsm` (Makros!), `.html`. **Doppelte "
                    "Endungen** wie `Rechnung.pdf.exe` sind fast immer Schadsoftware. "
                    "Wenn ein PDF-Anhang ein 'Klick hier'-Button hat → Phishing.\n\n"
                    "### 6. Rechtschreibung & Sprachstil\n\n"
                    "Phishing-Mails wurden oft maschinell übersetzt oder von "
                    "Nicht-Muttersprachlern verfasst. Selten 100 % korrektes "
                    "Deutsch. **Aber Vorsicht**: KI-generierte Phishing-Mails "
                    "der neuen Generation (2024+) sind **sprachlich perfekt**. "
                    "Sprache allein ist kein Schutzmerkmal mehr.\n\n"
                    "### 7. Untypischer Inhalt\n\n"
                    "Eine Bank schreibt dich auf Englisch an, obwohl du eine "
                    "deutsche Filiale nutzt? Dein Provider bittet um 'Verifikation' "
                    "deines Passworts? Ein Lieferant ändert plötzlich seine "
                    "IBAN per E-Mail? → **Telefonisch rückbestätigen** (mit der "
                    "Nummer aus deinem Adressbuch, NICHT aus der Mail).\n\n"
                    "### 8. Druck zur Geheimhaltung\n\n"
                    "'Erzählen Sie niemandem davon' oder 'nur Sie haben dieses ' "
                    "Angebot' — fast immer Betrug. Echte Vorgesetzte und Banken "
                    "haben kein Problem mit interner Rücksprache.\n\n"
                    "## Spezialfall: CEO-Fraud (BEC)\n\n"
                    "**Business Email Compromise** — die Phishing-Variante, die "
                    "den Mittelstand am häufigsten trifft. Ablauf:\n\n"
                    "1. Angreifer recherchiert auf LinkedIn die Führungsebene\n"
                    "2. Mail an Buchhaltung, vorgeblich vom Geschäftsführer: "
                    "'Bin gerade in einem Meeting, wir müssen eine Akquisition ' "
                    "anzahlen. Können Sie 87.000 € auf folgendes Konto "
                    "überweisen? Streng vertraulich.'\n"
                    "3. Buchhaltung will gehorsam sein, hat keine Zeit für "
                    "Rückfragen → Geld weg.\n\n"
                    "**Schutz:** Vier-Augen-Prinzip für Überweisungen >5.000 € "
                    "ist Standard. Bei E-Mail-Anweisungen für Beträge oder "
                    "IBAN-Wechsel: **immer telefonisch rückbestätigen** über "
                    "die bekannte Mobilnummer — nicht über die Nummer in der Mail.\n\n"
                    "## Wenn du verdächtig findest\n\n"
                    "1. **Nicht klicken, nicht antworten.**\n"
                    "2. Mail an `it-security@firma.de` weiterleiten (als Anhang, "
                    "nicht als Forward).\n"
                    "3. Mail dann **löschen**.\n\n"
                    "## Wenn du schon geklickt hast\n\n"
                    "1. Netzwerkkabel ziehen / WLAN ausschalten.\n"
                    "2. IT-Sicherheit sofort anrufen — auch nachts/Wochenende.\n"
                    "3. Passwort am betroffenen Account ändern (von einem anderen Gerät).\n"
                    "4. **Nicht aus Scham schweigen.** Frühe Meldung kostet "
                    "die Firma 10 % von dem, was eine späte Meldung kostet."
                ),
            ),
            ModulDef(
                titel="Mobiles Arbeiten & BYOD",
                inhalt_md=(
                    "## Warum 'außer Haus' ein Sicherheits-Risiko ist\n\n"
                    "Im Büro schützt dich die Firmen-Firewall, gefilterte DNS, "
                    "physische Zutrittskontrolle. Sobald du das Werks- oder "
                    "Büro-Gelände verlässt, bist du **alleine verantwortlich** — "
                    "dein Notebook, dein Smartphone, dein Verhalten.\n\n"
                    "## VPN — die unsichtbare Verlängerungsleitung\n\n"
                    "**VPN = Virtual Private Network**. Es baut einen verschlüsselten "
                    "Tunnel von deinem Gerät direkt ins Firmennetz auf. Vorteile:\n\n"
                    "- Alle Daten zwischen dir und der Firma sind verschlüsselt — "
                    "kein Mitlesen im Hotel-WLAN möglich.\n"
                    "- Du kommst an interne Ressourcen ran (Fileserver, ERP), "
                    "die von außen nicht erreichbar sind.\n"
                    "- Deine Internet-Aktivität wird durch unsere Firewall "
                    "gefiltert — schützt vor Malware-Sites.\n\n"
                    "**Regel: VPN immer aktiviert, BEVOR du auf Firmendaten "
                    "zugreifst.** Auch für 'nur kurz mal die E-Mail checken'.\n\n"
                    "### Offene WLANs sind heute noch riskant\n\n"
                    "Hotel, Café, ICE — die meisten dieser WLANs sind unverschlüsselt "
                    "oder mit nur einem geteilten Passwort gesichert. Andere "
                    "Gäste im selben Netz können theoretisch mitlesen ("
                    "Man-in-the-Middle-Angriffe). HTTPS schützt heutige Websites "
                    "zwar weitgehend, aber DNS-Anfragen und andere Metadaten "
                    "sind oft noch sichtbar.\n\n"
                    "**Faustregel:** WLAN-Symbol mit Schloss → Verschlüsselung "
                    "OK, aber trotzdem VPN. WLAN-Symbol ohne Schloss → **nur "
                    "mit VPN nutzen**, sonst Mobilfunk-Hotspot.\n\n"
                    "## Physische Sicherheit unterwegs\n\n"
                    "### Blickschutz\n\n"
                    "**Blickschutzfolie** für dein Notebook — verdunkelt das "
                    "Bild von der Seite. Pflicht im ICE/Bahn (Konkurrenz, "
                    "Journalisten, einfach Neugierige sitzen daneben).\n\n"
                    "### Geräte nie unbeaufsichtigt\n\n"
                    "Notebook im Café für 3 Minuten Toilette gehen → Diebstahl-"
                    "Risiko, aber **noch wichtiger**: ein USB-Stick mit Malware "
                    "kann in 30 Sekunden eingesteckt werden. 'Bad-USB'-Angriffe "
                    "umgehen Antivirus.\n\n"
                    "**Regel:** Beim Verlassen entweder mitnehmen oder in den "
                    "**Kabelschloss** sperren (Kensington-Lock, gibt es im IT-Lager).\n\n"
                    "### Hotelzimmer-Tresor\n\n"
                    "Beim Auschecken oder Konferenz-Sitzung Notebook im Hotel-"
                    "Tresor — sind nicht perfekt, aber besser als offen "
                    "rumliegen. Diensthandy mitnehmen wenn möglich, sonst "
                    "ebenfalls Tresor.\n\n"
                    "## BYOD — Eigene Geräte beruflich nutzen\n\n"
                    "**Bring Your Own Device (BYOD)** ist bei uns nur **nach "
                    "Freigabe durch die IT** und mit installiertem **MDM-Profil "
                    "(Mobile Device Management)** erlaubt. Das MDM ermöglicht:\n\n"
                    "- Trennung dienstlicher und privater Daten (Container)\n"
                    "- Erzwingung von Bildschirmsperre + Mindest-PIN-Länge\n"
                    "- **Remote-Wipe** bei Verlust (nur der dienstliche Container, "
                    "private Daten bleiben)\n"
                    "- Sperre für riskante Apps (z. B. Anti-Spy-Tools)\n\n"
                    "**Ohne MDM kein Dienst-Mail-Zugang.** Wer privat seinen "
                    "iMessage mit Firmen-Postfach synchronisiert, riskiert "
                    "Datenabfluss und kann für Schäden persönlich haften.\n\n"
                    "### App-Berechtigungen prüfen\n\n"
                    "Eine 'Taschenlampen'-App, die Kontaktzugriff fordert, ist "
                    "ein Datendieb. Periodisch in den App-Einstellungen prüfen, "
                    "welche Apps welche Rechte haben. **Faustregel:** Wenn eine "
                    "App ein Recht fordert, das sie für ihre Hauptfunktion nicht "
                    "braucht → verweigern oder deinstallieren.\n\n"
                    "## Wenn du dein Gerät verlierst\n\n"
                    "1. **Sofort IT-Sicherheit anrufen** — auch am Wochenende. "
                    "Wir lösen Remote-Wipe + Account-Sperre aus.\n"
                    "2. **Polizei-Anzeige** (für Versicherung).\n"
                    "3. **Passwörter ändern** für alle Dienste, die auf dem "
                    "Gerät eingeloggt waren.\n"
                    "4. **Schriftliche Meldung** an Datenschutzbeauftragte:n "
                    "binnen 24h — möglicherweise meldepflichtige Datenpanne.\n\n"
                    "**Je schneller die Meldung, desto kleiner der Schaden.** "
                    "Innerhalb von 30 Minuten nach Verlust ist Remote-Wipe "
                    "meist noch wirksam, weil das Gerät online ist."
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
                    "## Das System der Arbeitsschutzverantwortung\n\n"
                    "Das Arbeitsschutzgesetz (**ArbSchG**) ist seit 1996 die "
                    "deutsche Umsetzung der EU-Rahmenrichtlinie 89/391/EWG. Es "
                    "regelt im Kern eine Verantwortungskette mit klar verteilten "
                    "Rollen — kein 'die Sicherheit macht doch die Sifa'. Jeder "
                    "Beschäftigte ist Teil der Verantwortung.\n\n"
                    "### Pflichten des Arbeitgebers (§ 3 ArbSchG)\n\n"
                    "- Sicherstellen, dass Arbeit so organisiert ist, dass Leben "
                    "und Gesundheit der Beschäftigten geschützt werden\n"
                    "- Gefährdungsbeurteilung durchführen (§ 5 ArbSchG)\n"
                    "- Erforderliche Schutzmaßnahmen ergreifen und ihre Wirksamkeit "
                    "überprüfen\n"
                    "- **Wesentlich:** Die rechtliche Letzt-Verantwortung bleibt "
                    "**immer** beim Arbeitgeber, auch wenn Aufgaben delegiert werden.\n\n"
                    "### Delegation an Führungskräfte\n\n"
                    "Vorgesetzte tragen die Verantwortung im Rahmen ihres "
                    "Aufgabenbereichs. Voraussetzungen für wirksame Delegation:\n"
                    "- **Schriftlich** dokumentiert (Stellenbeschreibung, "
                    "Pflichtenübertragung)\n"
                    "- **Fachlich + persönlich geeignet** — Ausbildung + Erfahrung\n"
                    "- **Mit notwendigen Befugnissen** ausgestattet — Geld, "
                    "Personal, Entscheidungskompetenz, um Mängel beheben zu lassen\n\n"
                    "Eine Vorgesetzte kann nicht 'verantwortlich gemacht' werden, "
                    "wenn sie z. B. einen defekten Maschinen-Notaus melden, aber "
                    "von der Geschäftsleitung kein Reparatur-Budget bekommen hat — "
                    "dann fällt die Verantwortung zurück.\n\n"
                    "### Fachkraft für Arbeitssicherheit (Sifa)\n\n"
                    "Pflicht ab dem 1. Beschäftigten (ASiG § 5). Die Sifa **berät** "
                    "den Arbeitgeber — sie ist keine Linienkraft mit Weisungs"
                    "befugnis. Bei Industrie-Mittelständlern oft extern beauftragt "
                    "oder im Schichtsystem als interne Sifa benannt.\n\n"
                    "### Pflichten der Beschäftigten (§§ 15–16 ArbSchG)\n\n"
                    "**Pflicht zur Mitwirkung:** Jede:r Beschäftigte ist "
                    "**gesetzlich** verpflichtet, an seinem Arbeitsplatz aktiv "
                    "zur Sicherheit beizutragen. Im Detail:\n\n"
                    "1. **Schutzmaßnahmen befolgen** — PSA tragen wo angeordnet, "
                    "Sicherheitsabläufe einhalten, keine Manipulation von Schutz"
                    "einrichtungen\n"
                    "2. **Eigene Sicherheit + die anderer** im Auge behalten\n"
                    "3. **Gefahren melden**, sobald sie erkannt werden — z. B. "
                    "lockerer Stolperdraht, defekter Notaus, Wasserlache auf dem "
                    "Hallenboden\n"
                    "4. **Mängel an Schutzeinrichtungen melden** — sofort, "
                    "schriftlich oder per Meldebogen\n"
                    "5. **Arbeitsmedizinische Untersuchungen** wahrnehmen (G-"
                    "Untersuchungen), wenn der Arbeitgeber sie veranlasst\n\n"
                    "**Konsequenzen bei Verstoß:** Disziplinarisch (Abmahnung, "
                    "im Wiederholungsfall Kündigung), bei grober Fahrlässigkeit "
                    "auch zivilrechtlich (Schadenersatz) und strafrechtlich "
                    "(z. B. § 222 StGB fahrlässige Tötung).\n\n"
                    "### Konkrete Verantwortlichkeiten im Betrieb\n\n"
                    "| Funktion | Was sie/er tun MUSS |\n"
                    "|---|---|\n"
                    "| Beschäftigte:r | Maßnahmen befolgen, Gefahren melden, PSA tragen |\n"
                    "| Schichtleitung | Tägliche Sicherheitsprüfung, Einweisung neuer MA |\n"
                    "| Sifa | Gefährdungsbeurteilung + Beratung |\n"
                    "| Betriebsarzt | G-Vorsorge, Ergonomie-Beratung |\n"
                    "| Sicherheitsbeauftragte:r | Multiplikator im Team, kein Linienvorgesetzter |\n"
                    "| Geschäftsführung | Rahmen + Budget + Letzt-Verantwortung |\n\n"
                    "## Wann 'Nein sagen' Pflicht ist\n\n"
                    "**§ 17 ArbSchG: Recht zur Arbeitsverweigerung.** Wenn der "
                    "Arbeitgeber eine offensichtlich gefährliche Tätigkeit anordnet "
                    "und die Gefahr unmittelbar droht, darfst — und musst — du "
                    "die Arbeit verweigern. Bezahlung läuft weiter. Beispiele: "
                    "Maschine mit offensichtlich defektem Notaus betreiben; "
                    "Schweißarbeit ohne Brandwache in einem Bereich mit Lösungs"
                    "mittel-Dämpfen."
                ),
            ),
            ModulDef(
                titel="Gefährdungsbeurteilung",
                inhalt_md=(
                    "## Das Herzstück des Arbeitsschutzes\n\n"
                    "Die **Gefährdungsbeurteilung (GBU)** nach § 5 ArbSchG ist das "
                    "**zentrale Werkzeug** des modernen Arbeitsschutzes. Sie ist "
                    "die schriftliche Antwort auf die Frage: 'Was kann hier ' "
                    "schiefgehen — und was tun wir dagegen?'\n\n"
                    "Ohne GBU gibt es keine systematischen Schutzmaßnahmen, ohne "
                    "systematische Schutzmaßnahmen gibt es keine wirksame "
                    "Unfallverhütung. Fehlende oder mangelhafte GBU ist eine "
                    "**Ordnungswidrigkeit** (Bußgeld bis 25.000 €, im Wiederholungs"
                    "fall Straftat).\n\n"
                    "## Die sieben Schritte einer GBU\n\n"
                    "1. **Arbeitsbereich** und Tätigkeit abgrenzen (z. B. 'CNC-Fräse ' "
                    "Halle B, Schicht 1')\n"
                    "2. **Gefährdungen ermitteln** — was kann passieren?\n"
                    "3. **Gefährdungen bewerten** — wie wahrscheinlich, wie schwer?\n"
                    "4. **Maßnahmen festlegen** — Reihenfolge: erst technisch, "
                    "dann organisatorisch, zuletzt persönlich (TOP-Prinzip)\n"
                    "5. **Umsetzen** — mit Verantwortlichen + Terminen\n"
                    "6. **Wirksamkeit prüfen** — hat die Maßnahme das Risiko "
                    "wirklich reduziert?\n"
                    "7. **Aktualisieren** — bei jeder Veränderung\n\n"
                    "## Gefährdungsarten in der Produktion\n\n"
                    "### Mechanisch\n"
                    "- **Rotierende Teile** (Sägeblätter, Bohrer, Walzen) → "
                    "Verletzungsgefahr durch Schnitt, Einklemmen, Aufwickeln\n"
                    "- **Schneidende, stechende, scharfe** Werkzeuge\n"
                    "- **Stürzende, kippende** Teile (Werkstücke vom Transportwagen)\n"
                    "- **Stolpern, Rutschen, Stürzen** auf gleicher Ebene — "
                    "übrigens die **häufigste Unfallursache** im Betrieb\n\n"
                    "### Thermisch\n"
                    "- Heiße Oberflächen ab 60 °C (Verbrennung)\n"
                    "- Schweißfunken, Schlackeperlen — können Sekunden später noch zünden\n"
                    "- Kryogene Stoffe (Flüssigstickstoff, CO₂) — Kältebrand\n\n"
                    "### Elektrisch\n"
                    "- Stromfluss durch den Körper bereits ab 50 V AC / 120 V DC "
                    "lebensgefährlich\n"
                    "- Lichtbogen bei Kurzschluss — Verbrennung + Verblitzung\n"
                    "- Statische Aufladung in ATEX-Bereichen (Funke = Brand)\n\n"
                    "### Chemisch\n"
                    "- Hautkontakt, Einatmen, Verschlucken von Gefahrstoffen\n"
                    "- Allergene Substanzen (Epoxidharze, Isocyanate, Nickel)\n"
                    "- CMR-Stoffe (krebserzeugend, erbgutverändernd, fortpflanzungs"
                    "gefährdend) → besondere Schutzpflichten\n\n"
                    "### Physikalisch\n"
                    "- **Lärm** ab 80 dB(A) Tagesexposition gehörgefährdend\n"
                    "- **Vibration** Hand-Arm-Syndrom\n"
                    "- **Strahlung** (UV von Schweißlichtbögen, IR-Wärmestrahlung, "
                    "Laser, ionisierende Strahlung)\n"
                    "- **Klima** — Hitze in Gießereien, Kälte im Tiefkühllager\n\n"
                    "### Ergonomisch\n"
                    "- Schweres Heben (>25 kg Mann, >15 kg Frau dauerhaft)\n"
                    "- Einseitige Belastung, Zwangshaltung\n"
                    "- Bildschirmarbeit — Augen, Nacken, Schulter\n\n"
                    "### Psychisch\n"
                    "- Zeit- und Termindruck, Schichtarbeit, Personalmangel\n"
                    "- Konflikte, Mobbing, mangelnde Anerkennung\n"
                    "- **Pflicht zur Beurteilung psychischer Belastung** seit 2013\n\n"
                    "### Brand- und Explosionsgefahr\n"
                    "- Brennbare Flüssigkeiten, Gase, Stäube\n"
                    "- Heißarbeiten in der Nähe brennbarer Stoffe\n"
                    "- ATEX-Zonen (Explosionsgefährdete Bereiche)\n\n"
                    "## Wann die GBU aktualisiert werden muss\n\n"
                    "- **Neue Maschine, neuer Arbeitsmittel** → vor Inbetriebnahme\n"
                    "- **Neuer Stoff** im Einsatz → vor Verarbeitung\n"
                    "- **Geänderter Prozess** (z. B. neue Arbeitsfolge, andere "
                    "Schichteinteilung)\n"
                    "- **Nach einem Unfall** oder Beinaheunfall — was hätten wir "
                    "verhindern können?\n"
                    "- **Bei Änderungen der Vorschriften** (z. B. neue TRGS)\n"
                    "- **Regelmäßig** — auch ohne Anlass, üblicherweise alle 2 Jahre\n\n"
                    "## Was DU damit zu tun hast\n\n"
                    "Du wirst von deiner Vorgesetzten in die für deinen Arbeits"
                    "platz relevanten Teile der GBU eingewiesen — bei Eintritt "
                    "und jährlich. Wenn dir auffällt, dass eine Gefährdung "
                    "**nicht abgebildet** ist (z. B. eine neue Maschine, ein "
                    "neuer Prozess), **melde es**. Du kennst deinen Arbeitsplatz "
                    "oft besser als die Sifa."
                ),
            ),
            ModulDef(
                titel="Notfallorganisation",
                inhalt_md=(
                    "## Wenn etwas passiert: die richtigen Reflexe\n\n"
                    "Im Notfall zählen Sekunden. Studien der DGUV zeigen: "
                    "qualifizierte Erste Hilfe innerhalb der ersten **5 Minuten** "
                    "kann bei Herzstillstand die Überlebenschance von 5 % auf "
                    "70 % erhöhen. Aber: nur, wenn die richtigen Schritte in "
                    "der richtigen Reihenfolge passieren.\n\n"
                    "## Die richtige Reihenfolge im Notfall\n\n"
                    "### 1. Eigenschutz zuerst\n\n"
                    "Klingt egoistisch, ist aber Pflicht: **wer selbst zum Opfer "
                    "wird, kann niemandem mehr helfen.**\n\n"
                    "- **Stromunfall**: erst Strom abschalten (Sicherung, "
                    "Hauptschalter), DANN zum Verletzten\n"
                    "- **Maschinenunfall**: erst Maschine stoppen (Notaus), "
                    "DANN bergen\n"
                    "- **Brand**: nicht in den Brandraum laufen, ohne dass "
                    "Rettungsweg gesichert ist\n"
                    "- **Gefahrstoff-Austritt**: Atemschutz / Sicherheits"
                    "abstand, bevor du näher gehst\n\n"
                    "### 2. Notruf absetzen — die 5 W\n\n"
                    "**Telefonnummer**: 112 (Feuerwehr + Rettungsdienst, "
                    "europaweit, auch ohne SIM), 110 (Polizei).\n\n"
                    "| W | Was sagen |\n"
                    "|---|---|\n"
                    "| **W**o | Genaue Adresse, Halle, Stockwerk |\n"
                    "| **W**as | 'Arbeitsunfall, Person eingeklemmt' |\n"
                    "| **W**ieviele | Anzahl Verletzter |\n"
                    "| **W**elche Verletzungen | 'Beinverletzung, bewusstlos' |\n"
                    "| **W**arten auf Rückfragen | **NICHT auflegen!** Die "
                    "Leitstelle beendet das Gespräch. |\n\n"
                    "### 3. Erste Hilfe leisten\n\n"
                    "Im Rahmen deiner Möglichkeiten. **Niemand erwartet, dass "
                    "du Arzt:in bist** — aber jeder Beschäftigte hat als Schul"
                    "kind 1× Erste Hilfe gemacht, das reicht für die kritischen "
                    "Minuten:\n"
                    "- Bewusstlos + atmet → **stabile Seitenlage**\n"
                    "- Bewusstlos + atmet **nicht** → **Herzdruckmassage** "
                    "(30:2 oder durchgehend bis Hilfe da ist)\n"
                    "- Blutung → **Druckverband** mit Material aus dem Verbands"
                    "kasten\n"
                    "- Verbrennung → **10–20 min mit lauwarmem Wasser** kühlen\n\n"
                    "**Mehr dazu im Kurs 'Erste Hilfe Auffrischung'** — alle 2 "
                    "Jahre Pflicht.\n\n"
                    "### 4. Unfall melden\n\n"
                    "Auch wenn der Verletzte 'schon wieder fit' ist:\n"
                    "- **Mündlich** an die direkte Vorgesetzte sofort\n"
                    "- **Schriftlich** im Unfallbuch / DGUV-Unfallanzeige\n"
                    "- **An Sifa** und ggf. Betriebsrat\n\n"
                    "## Meldepflichten an die Berufsgenossenschaft (BG)\n\n"
                    "| Art des Vorfalls | Frist |\n"
                    "|---|---|\n"
                    "| Verbandbuch-Eintrag jeder Bagatelle | sofort |\n"
                    "| Unfallanzeige (AU > 3 Tage) | binnen **3 Tagen** |\n"
                    "| Tödlicher Unfall, Massenunfall | **sofort** (Telefon) |\n"
                    "| Berufskrankheits-Verdacht | sofort durch Arzt/Arbeitgeber |\n\n"
                    "**Achtung:** Wer einen meldepflichtigen Unfall verschweigt, "
                    "begeht eine Ordnungswidrigkeit (§ 25 SGB VII).\n\n"
                    "## Das Verbandbuch — der vergessene Held\n\n"
                    "Auch Schnitt am Finger, Splitter im Auge, Quetschung "
                    "müssen ins **Verbandbuch** (Vorgabe DGUV V1 § 24). Warum?\n\n"
                    "- **Spätfolgen** (Tetanus-Infektion nach 5 Tagen, Allergie "
                    "nach Monaten) lassen sich nur als 'Arbeitsunfall' anerkennen, "
                    "wenn die Ursache dokumentiert ist.\n"
                    "- **Wiederholte Bagatellen** zeigen ein Risikomuster — "
                    "Anzeichen, dass eine Gefährdungsbeurteilung nachgebessert "
                    "werden muss.\n"
                    "- **BG zahlt nur**, wenn ein Eintrag existiert.\n\n"
                    "Das Verbandbuch liegt typischerweise im **Erste-Hilfe-Raum** "
                    "oder neben dem Verbandkasten. Frage deinen Sicherheits"
                    "beauftragten, wo bei euch.\n\n"
                    "## Brandfall, Stromschlag, Chemie-Austritt\n\n"
                    "Für die häufigsten Sonderfälle gibt es separate Schulungs"
                    "module (Brandschutz, Gefahrstoffe, Erste Hilfe). Hier nur "
                    "der Reflex:\n"
                    "- **Brand**: 1. Personen warnen + retten 2. Feuerwehr "
                    "rufen 3. nur löschen, wenn Fluchtweg gesichert\n"
                    "- **Stromschlag**: 1. Stromkreis trennen 2. Notruf 3. "
                    "Person aus Gefahrenbereich ziehen (isoliert!) 4. CPR wenn nötig\n"
                    "- **Gefahrstoff-Austritt**: 1. Atemschutz, Bereich räumen "
                    "2. Sicherheitsdatenblatt zur Hand 3. nicht versuchen "
                    "kleinere Mengen selbst zu beseitigen wenn unsicher"
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
                    "## Warum die Brandklassen wichtig sind\n\n"
                    "Das **falsche Löschmittel** kann den Brand **verstärken** — "
                    "Wasser auf einen Fettbrand führt zu einer Fettexplosion mit "
                    "meterhoher Stichflamme. Wasser auf brennende Magnesiumspäne "
                    "(in der Späne-Sammelwanne der CNC-Fräse) erzeugt Knallgas und "
                    "kann eine **Explosion** auslösen. Die Brandklassen-Kennung "
                    "auf jedem Feuerlöscher ist deshalb kein Schmuck, sondern "
                    "lebenswichtig.\n\n"
                    "## Die fünf Brandklassen nach DIN EN 2\n\n"
                    "| Klasse | Brennstoff | Typische Beispiele im Industriebetrieb | Geeignete Löschmittel | UNGEEIGNET |\n"
                    "|---|---|---|---|---|\n"
                    "| **A** | Feste glutbildende Stoffe | Holz, Papier, Kartonage, Textil, Kunststoffe (langsam) | Wasser, Schaum, ABC-Pulver | — |\n"
                    "| **B** | Flüssigkeiten, schmelzende Feststoffe | Benzin, Diesel, Heizöl, Lacke, Lösungsmittel | Schaum, CO₂, BC- oder ABC-Pulver | Wasser (Brand schwimmt + breitet sich aus) |\n"
                    "| **C** | Gase | Propan, Erdgas, Wasserstoff, Acetylen | ABC-Pulver, BC-Pulver | Wasser, Schaum (Wirkungslos, Funkenrisiko) |\n"
                    "| **D** | Metalle | Magnesium, Aluminium-Späne, Lithium, Titan | **NUR** D-Pulver oder trockener Sand | Wasser (Knallgas, Explosion!), Schaum, CO₂ |\n"
                    "| **F** | Speisefette/-öle | Frittiertem, Pflanzenöl, tierische Fette | Fettbrand-Löscher (Klasse F) oder Decke | Wasser (Fettexplosion, lebensgefährlich!) |\n\n"
                    "**Eselsbrücke ABCDEF:** **A**bsolut feste, **B**rennende Flüssigkeit, "
                    "**C**hemisches Gas, **D**ünne Metallspäne, (E ausgelassen — "
                    "war früher für Strom), **F**ettpfanne.\n\n"
                    "## Welcher Löscher steht wo?\n\n"
                    "Bei uns im Betrieb sind die Löscher nach Bereich gewählt:\n\n"
                    "- **Büros, Lager Papier/Karton** → ABC-Pulver oder Schaum (Klasse A)\n"
                    "- **Werkstatt mit Öl/Lacke** → Schaum + CO₂ (Klassen A/B)\n"
                    "- **CNC-Bereich mit Späne-Sammler** → zusätzlich D-Pulver "
                    "in Reichweite (Klasse D)\n"
                    "- **Server-Raum, Elektrik** → CO₂ (rückstandsfrei, leitet nicht)\n"
                    "- **Kantine, Spülküche** → Fettbrandlöscher (Klasse F)\n\n"
                    "## Die wichtigsten Löschmittel im Detail\n\n"
                    "### Wasser\n"
                    "- Wirkt durch **Abkühlen** unter die Zündtemperatur\n"
                    "- Universell für Klasse A, **billig** und reichlich verfügbar\n"
                    "- **Niemals** auf Brennstoffflüssigkeiten (Klasse B), Metalle (D), "
                    "Fette (F), elektrische Anlagen unter Spannung\n\n"
                    "### Schaum\n"
                    "- Erstickt + kühlt — gut für Klassen A + B\n"
                    "- Hinterlässt Rückstände → ungeeignet für Elektronik/Mechanik\n\n"
                    "### CO₂ (Kohlendioxid)\n"
                    "- Wirkt durch **Verdrängen des Sauerstoffs** und Abkühlung\n"
                    "- **Rückstandsfrei** → ideal für Elektronik, Maschinen, "
                    "Lebensmittelbereich\n"
                    "- **Vorsicht in engen Räumen**: Erstickungsgefahr für den "
                    "Löschenden bei zu viel CO₂\n"
                    "- Kalt (-78 °C bei der Austrittsdüse) → **Erfrierungs"
                    "gefahr** an Händen\n\n"
                    "### ABC-Pulver\n"
                    "- Universell, gegen Klassen A, B, C\n"
                    "- Wirkt durch chemische Reaktion + Erstickung\n"
                    "- **Erheblicher Reinigungsaufwand** danach (Pulver kriecht "
                    "in jede Ritze, korrodiert Elektronik) → nicht für Server-Räume\n\n"
                    "### D-Pulver\n"
                    "- **Spezialprodukt** für Metallbrände — chemisch reagiert "
                    "mit dem brennenden Metall, isoliert es\n"
                    "- Nur dort vorhalten, wo Klasse-D-Risiko besteht (Mg, Al-"
                    "Späne in CNC-Hallen)\n\n"
                    "### Fettbrandlöscher (Klasse F)\n"
                    "- Wirkt durch chemische Reaktion mit dem heißen Fett: "
                    "es bildet sich eine Seifenschicht, die Sauerstoff abschneidet\n"
                    "- **Pflicht** in jeder gewerblichen Küche/Kantine\n\n"
                    "## Die richtige Bedienung — alle Löscher gleich\n\n"
                    "Egal welcher Typ, die Bedienung ist nach einem festen Schema:\n\n"
                    "1. **Sicherung ziehen** (Splint oder Plombe)\n"
                    "2. **Schlauch in die Hand** nehmen, auf den Brand richten\n"
                    "3. **Auslöseventil drücken**\n"
                    "4. **Stoßweise löschen** — nicht in einem Zug entleeren\n"
                    "5. Bei mehreren Löschern: **gleichzeitig**, nicht nacheinander\n"
                    "6. Nach dem Löschen: **Brandstelle beobachten** — Wieder"
                    "entzündung möglich\n\n"
                    "**Vorgehen am Brand selbst:**\n"
                    "- **Mit dem Wind im Rücken** löschen — nicht gegen den Wind\n"
                    "- **Glut + Wurzeln** löschen, nicht nur die Flammen oben drauf\n"
                    "- **Flächenbrände** von vorne nach hinten löschen\n"
                    "- **Tropfbrände** (Lack vom Regal in Pfütze): erst die Pfütze, "
                    "dann oben\n\n"
                    "## Niemals Wasser auf …\n\n"
                    "**⚠️ Fettbrand** — Wasser verdampft schlagartig auf 100 °C, "
                    "schleudert das brennende Fett meterhoch. Lebensgefährliche "
                    "Verbrennungen am Lösch-Helfer. Stattdessen: Klassen-F-Löscher "
                    "oder eine **dichte Branddecke** drüberwerfen.\n\n"
                    "**⚠️ Metallbrand** — Wasser reagiert mit brennenden "
                    "Magnesium/Aluminium-Spänen unter Bildung von Knallgas "
                    "(Wasserstoff) → Explosion. **Nur D-Pulver oder Sand.**\n\n"
                    "**⚠️ Strom unter Spannung** — Wasser leitet, Lebensgefahr "
                    "für die löschende Person. Erst Strom abschalten, dann mit "
                    "CO₂ oder ABC-Pulver."
                ),
            ),
            ModulDef(
                titel="Verhalten im Brandfall",
                inhalt_md=(
                    "## Die ersten 60 Sekunden entscheiden\n\n"
                    "Ein Zimmerbrand entwickelt sich in der **'Heißgasphase'** "
                    "nach 2–3 Minuten zur **flashover**-Situation — die gesamten "
                    "Raumgase entzünden sich auf einmal. Wer **innerhalb der "
                    "ersten 60 Sekunden** richtig reagiert, rettet meistens "
                    "alle. Wer zögert oder falsch reagiert, riskiert Tote.\n\n"
                    "## Die richtige Reihenfolge — RAMS-Schema\n\n"
                    "**R**uhe bewahren — **A**larm + Notruf — **M**enschen retten — "
                    "**S**chließen + (eventuell) löschen.\n\n"
                    "### 1. Ruhe bewahren\n\n"
                    "Panik ist der häufigste Tötungsfaktor bei Bränden. Tief "
                    "atmen, Situation einschätzen: Wo brennt's? Wo ist Rauch? "
                    "Wo sind Fluchtwege? Wer ist um mich herum?\n\n"
                    "### 2. Alarm auslösen + Notruf\n\n"
                    "- **Brandmeldetaster** drücken (rote Kästen an Säulen/Wänden, "
                    "Glas einschlagen)\n"
                    "- **Notruf 112** absetzen (Mobil oder Festnetz)\n"
                    "- **Alle anderen warnen** — Rufen, Whistle, Sirene\n\n"
                    "Brandmeldeanlagen lösen automatisch die Sprinkler/Rauchabzüge "
                    "aus und benachrichtigen die Feuerwehr — aber **nicht** "
                    "automatisch alle Etagen. Direkter Notruf parallel macht "
                    "Sinn.\n\n"
                    "### 3. Menschen retten\n\n"
                    "- **Sich selbst und andere** in Sicherheit bringen\n"
                    "- **Hilflose** (gestürzte Kollegen, Verletzte) mitnehmen — "
                    "wenn ohne Eigengefährdung möglich\n"
                    "- **Türen schließen** beim Verlassen (verzögert die Rauch"
                    "ausbreitung um ~10 Minuten!)\n"
                    "- **Niemals den Aufzug** benutzen — kann zwischen Etagen "
                    "stecken bleiben, Schacht wirkt wie Kamin\n"
                    "- **Treppenhäuser** sind 'brandgeschützt' und meist 30–90 "
                    "min sicher\n\n"
                    "### 4. Schließen + ggf. löschen\n\n"
                    "**Türen schließen — nicht aufreißen.** Hinter einer "
                    "geschlossenen Tür kann ein Schwelbrand sich Stunden "
                    "halten, bis Sauerstoff dazukommt. **Beim Aufreißen einer "
                    "Brandraum-Tür** dringt schlagartig Sauerstoff ein → "
                    "**Stichflamme** (Backdraft). Lebensgefährlich.\n\n"
                    "**Hand vor die Tür-Klinke** — heiß? Dann nicht öffnen, "
                    "Fluchtweg woanders suchen.\n\n"
                    "**Löschversuche nur, wenn alle drei Bedingungen erfüllt:**\n"
                    "1. **Fluchtweg gesichert** — du kannst jederzeit raus\n"
                    "2. **Entstehungsbrand** — Flammen klein, nicht über "
                    "Schreibtisch-Höhe\n"
                    "3. **Geeignetes Löschmittel** zur Hand — und du weißt, wie\n\n"
                    "Sonst: **rausgehen, Tür zumachen, warten auf Feuerwehr.**\n\n"
                    "## Verhalten in verqualmten Räumen\n\n"
                    "**Rauchgas tötet schneller als Feuer** — 95 % der Brandtoten "
                    "sterben an Rauchvergiftung, nicht an Verbrennung. Schon "
                    "**3–5 Atemzüge** Brandrauch können tödlich sein (CO, HCN, "
                    "Salzsäure, Phosgen).\n\n"
                    "- **Tief beugen oder kriechen** — am Boden sind etwa 30 cm "
                    "über dem Boden frische Atemluft mit nur leichter Rauch"
                    "verdünnung. In Augenhöhe ist es schon tödlich.\n"
                    "- **Atem anhalten + zügig durch verrauchten Bereich** "
                    "(max. 30 m)\n"
                    "- **Tuch vor Mund und Nase** — feuchtes Tuch ist besser, "
                    "filtert grobe Partikel (aber nicht CO!)\n"
                    "- **Wenn du nicht raus kommst**: in einen Raum mit Tür + "
                    "Fenster, Tür zu, Spalt mit nasser Kleidung abdichten, am "
                    "Fenster bemerkbar machen\n\n"
                    "## Im Brandfall NIEMALS\n\n"
                    "- **Aufzug benutzen** — kann ausfallen, Schacht wird Schornstein\n"
                    "- **Wertgegenstände holen** — Notebook, Handy, Tasche bleiben "
                    "liegen. Sachen sind ersetzbar, du nicht.\n"
                    "- **Türen aufreißen** ohne Klinken-Check\n"
                    "- **Im Rauch aufrecht gehen** — schon ein einziger tiefer "
                    "Atemzug kann zur Bewusstlosigkeit führen\n"
                    "- **In ein Gebäude zurückkehren**, das du schon verlassen hast"
                ),
            ),
            ModulDef(
                titel="Flucht- und Rettungswege",
                inhalt_md=(
                    "## Was Flucht- und Rettungswege leisten müssen\n\n"
                    "Ein **Fluchtweg** ist der Weg, den du nimmst, um aus eigenem "
                    "Antrieb sicher ins Freie zu kommen. Ein **Rettungsweg** ist "
                    "derselbe Weg aus Sicht der Feuerwehr — sie kommt rein, du "
                    "kommst raus.\n\n"
                    "Nach **Arbeitsstättenverordnung (ArbStättV) + ASR A2.3** "
                    "muss jeder Arbeitsplatz mindestens einen **ersten** Flucht"
                    "weg ins Freie haben, der **maximal 35 m lang** ist (in "
                    "Bereichen erhöhter Brandgefahr 25 m, in normalen Büros bis "
                    "50 m). Bei mehr als ~10 Personen oder größeren Räumen sind "
                    "**zwei voneinander unabhängige Fluchtwege** Pflicht.\n\n"
                    "## Bauliche Anforderungen\n\n"
                    "- **Mindestbreite** 1,00 m bei ≤20 Personen, breiter bei "
                    "mehr (0,60 m pro 100 Personen zusätzlich)\n"
                    "- **Türen** öffnen in **Fluchtrichtung** und sind mit "
                    "**Panik-Schloss** versehen (kein Schlüssel nötig, nicht "
                    "abschließbar von Innen)\n"
                    "- **Treppenhäuser** sind in eigene Brandabschnitte gefasst, "
                    "mit feuerhemmenden Türen (T30/T90)\n"
                    "- **Kennzeichnung** mit grünem Rettungszeichen "
                    "(DIN EN ISO 7010 — Männchen läuft durch Tür, Pfeil)\n"
                    "- **Sicherheitsbeleuchtung** muss bei Stromausfall **mindestens "
                    "60 Minuten** leuchten, an der Decke entlang des Wegs montiert\n"
                    "- **Bodenmarkierung** in besonders verqualmungsgefährdeten "
                    "Bereichen (rutschfest, nachleuchtend)\n\n"
                    "## Was darf NICHT auf Fluchtwegen stehen\n\n"
                    "**Gar nichts.** Fluchtwege sind **vollständig freizuhalten** — "
                    "auch 'nur kurz'.\n\n"
                    "- Keine **Paletten, Kartons, Materialwagen**\n"
                    "- Kein **Müll, Putzeimer, Stühle**\n"
                    "- Keine **abgestellten Stapler oder Hubwagen**\n"
                    "- Keine **Brandschutztüren keilen** (mit Holzkeil offen halten) — "
                    "das ist eine **Ordnungswidrigkeit** (Bußgeld bis 50.000 €) "
                    "und kann im Brandfall Menschenleben kosten\n\n"
                    "**Stolperfallen** auf Fluchtwegen sind verboten. Selbst eine "
                    "Bodenschwelle >4 mm muss markiert sein.\n\n"
                    "**Wenn du eine Behinderung siehst**: räume sie weg (wenn "
                    "möglich) oder melde sofort an die Schichtleitung. Das ist "
                    "keine 'Petze' — das ist deine **gesetzliche Pflicht** als "
                    "Beschäftigte:r nach § 16 ArbSchG.\n\n"
                    "## Der Sammelplatz\n\n"
                    "Nach einer Evakuierung gehen alle zum **vereinbarten Sammel"
                    "platz** (bei uns: Parkplatz westlich der Halle, mind. 50 m "
                    "Abstand zum Gebäude). Dort:\n\n"
                    "- **Sammelplatz-Verantwortliche** zählt nach Anwesenheits"
                    "liste / Schichtplan\n"
                    "- **Feuerwehr** wird informiert, ob noch jemand vermisst wird\n"
                    "- **Niemand betritt das Gebäude wieder**, bis die Feuerwehr "
                    "freigibt — auch nicht 'kurz das Handy holen'\n\n"
                    "Vermisste Personen werden gezielt **von Feuerwehrleuten "
                    "unter Atemschutz** gesucht. Wer nach 'Wo ist Hans?' Hans "
                    "selber suchen geht, lenkt die Feuerwehr ab und gefährdet "
                    "alle Helfer.\n\n"
                    "## Brandschutzhelfer\n\n"
                    "Pro Etage bzw. Brandabschnitt sind **mindestens 5 % der "
                    "Beschäftigten** als **Brandschutzhelfer** ausgebildet (ASR A2.2). "
                    "Sie:\n"
                    "- kennen die Position der Löscher + Brandmeldetaster\n"
                    "- können einen Entstehungsbrand bekämpfen\n"
                    "- führen die Evakuierung ihres Bereichs\n"
                    "- kontrollieren Vollständigkeit am Sammelplatz\n\n"
                    "Brandschutzhelfer haben eine Schulung von mind. 2 Stunden "
                    "absolviert (Theorie + praktische Übung mit Löscher). "
                    "Auffrischung alle 3–5 Jahre.\n\n"
                    "## Verhaltens-Übung: Räumungsübung\n\n"
                    "Mindestens **einmal jährlich** wird bei uns eine Räumungs"
                    "übung durchgeführt (vorgegeben durch DGUV V1 § 22). Bei "
                    "Alarm:\n\n"
                    "1. Arbeit **sofort einstellen** — Maschine abschalten, "
                    "PC stehen lassen, Geräte aus wenn schnell möglich\n"
                    "2. **Sachen liegen lassen** — keine Tasche, kein Notebook\n"
                    "3. **Ruhig + zügig** zum Fluchtweg\n"
                    "4. **Türen schließen** beim Verlassen\n"
                    "5. **Zum Sammelplatz** gehen — nicht zum Auto\n"
                    "6. **Bei der Sammelplatz-Verantwortlichen melden**\n\n"
                    "Auch wenn es 'nur eine Übung' ist: ernst nehmen. Wer bei "
                    "einer Übung patzt, patzt im Ernstfall auch."
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
                    "## Warum das richtige Telefonat Leben rettet\n\n"
                    "Die **Leitstelle der Rettungsdienste** entscheidet auf Basis "
                    "deiner Information, welche Einsatzmittel auf den Weg geschickt "
                    "werden: Rettungswagen, Notarzt, Notfallseelsorger, "
                    "Hubschrauber, Feuerwehr, Polizei. Eine schlechte Meldung "
                    "kostet **Minuten** — und Minuten retten oder kosten Leben.\n\n"
                    "## Die fünf W im Detail\n\n"
                    "### 1. **W**o ist der Notfall?\n\n"
                    "**Möglichst exakt:** Straßenname + Hausnummer + Etage + Halle/"
                    "Raum + besondere Hinweise (z. B. 'Eingang über den Hof').\n\n"
                    "Bei uns: **'Vaeren-Werke, Industriestraße 12, 91564 Neuendettelsau, ' "
                    "Halle 2, CNC-Bereich West'** — diesen Standort-Text **kennt "
                    "jede:r Mitarbeiter:in auswendig**. Ohne Adresse keine Hilfe.\n\n"
                    "Auf Werks- und Baustellen-Geländen ist die exakte **Tor**-"
                    "Bezeichnung wichtig (Tor 1 / Tor 2 / Lieferantentor), damit "
                    "das Rettungsfahrzeug nicht 5 Minuten ums Gelände kreist.\n\n"
                    "### 2. **W**as ist passiert?\n\n"
                    "Knapp + sachlich. **Beispiele:**\n"
                    "- 'Arbeitsunfall, Mann ist mit der Hand in die Fräse geraten'\n"
                    "- 'Frau ist bewusstlos in der Pause zusammengebrochen'\n"
                    "- 'Säureverätzung an Augen + Gesicht, ca. 30 Sekunden Kontakt'\n"
                    "- 'Brand in Halle 2, Personen sind raus, Feuerwehr nötig'\n\n"
                    "Keine Geschichten ('… und dann meinte mein Kollege …'), "
                    "keine Spekulationen, keine Vorwürfe. Sachverhalt.\n\n"
                    "### 3. **W**ieviele Verletzte / Betroffene?\n\n"
                    "Anzahl konkret nennen. 'Eine Person', 'drei Personen, davon "
                    "zwei bewusstlos'. Bei Massenanfall: 'Mehrere, mindestens 5, "
                    "wir können noch nicht zählen' — die Leitstelle schickt dann "
                    "automatisch mehr Mittel.\n\n"
                    "### 4. **W**elche Verletzungen oder Erkrankungen?\n\n"
                    "Soweit erkennbar:\n"
                    "- **Bewusst** oder bewusstlos?\n"
                    "- **Atmet** normal / röchelnd / nicht?\n"
                    "- **Blutung** stark / schwach?\n"
                    "- Sichtbare **Verbrennungen, Verätzungen, Brüche**?\n"
                    "- Bei Erkrankungen: Symptome (Brustschmerz, halbseitige "
                    "Lähmung, Verwirrtheit, Atemnot)\n\n"
                    "**Nicht selbst diagnostizieren** ('das ist sicher ein Herzinfarkt') "
                    "— Symptome melden, der Notarzt diagnostiziert.\n\n"
                    "### 5. **W**arten auf Rückfragen — niemals selbst auflegen!\n\n"
                    "Die Leitstelle hat oft präzise Folgefragen:\n"
                    "- 'Können Sie zur Person hin, um die Atmung zu prüfen?'\n"
                    "- 'Ist ein AED in der Nähe?'\n"
                    "- 'Gibt es einen weiteren Verletzten im Bereich?'\n"
                    "- 'Wer von Ihnen kann Erste Hilfe?'\n\n"
                    "Diese Antworten **steuern die Anweisungen**, die du bekommst — "
                    "telefongeführte Reanimation hat schon vielen Menschen das "
                    "Leben gerettet.\n\n"
                    "**Erst auflegen, wenn die Leitstelle es ausdrücklich sagt.**\n\n"
                    "## Nach dem Notruf\n\n"
                    "1. **Einweisung organisieren** — eine Person zum Eingang/Tor "
                    "schicken, um Rettungsdienst zu lotsen\n"
                    "2. **Zufahrt freihalten** — keine Privatfahrzeuge in der "
                    "Zufahrt, Lieferantentor öffnen wenn nötig\n"
                    "3. **Rettungsweg innerhalb** des Gebäudes räumen — Türen "
                    "offen, Aufzug bereithalten (wenn brandsicher)\n"
                    "4. **Mit der/dem Verletzten reden** — auch bei Bewusstlosen. "
                    "Hörsinn ist meist als letztes erhalten, Stimme beruhigt.\n\n"
                    "## Internationale Nummer + Tipps\n\n"
                    "- **112** ist die EU-weite einheitliche Notrufnummer. "
                    "Funktioniert auch ohne SIM-Karte, ohne Guthaben, ohne "
                    "PIN-Eingabe (Notruf-Taste am Sperrbildschirm).\n"
                    "- **Stumme Notrufe** (z. B. bei Bedrohung): Mit einem "
                    "modernen Smartphone Notruf wählen, dann auf der Tastatur "
                    "die Antworten eintippen — viele Leitstellen erkennen das.\n"
                    "- **Schlechter Empfang**: Etwas SMS Notruf gibt es in DE "
                    "regional, aber Anrufe sind zuverlässiger.\n"
                    "- **Notfall-Pass** auf dem Smartphone (iOS Health, Android "
                    "Notfallinfo) — Sanitäter können auch ohne deine PIN "
                    "Vorerkrankungen + Notfallkontakt sehen. **Im Voraus "
                    "ausfüllen**, hilft wenn DU mal der Verletzte bist."
                ),
            ),
            ModulDef(
                titel="Bewusstlosigkeit & Wiederbelebung",
                inhalt_md=(
                    "## Was passiert bei Herzstillstand\n\n"
                    "Bei einem Herzstillstand wird das **Hirn nicht mehr mit "
                    "Sauerstoff versorgt**. Nach **3–5 Minuten** beginnen "
                    "irreversible Hirnschäden, nach 10 Minuten ohne CPR ist "
                    "die Überlebenschance nahezu null.\n\n"
                    "**Aber:** Mit qualifizierter Herzdruckmassage (CPR) und "
                    "AED-Einsatz innerhalb von 3 Minuten überleben **bis zu "
                    "70 %** der Betroffenen ohne bleibende Schäden. Du als "
                    "Erst-Helfer bist die wichtigste Person der Rettungskette.\n\n"
                    "## Das Drei-Schritt-Schema: Prüfen — Rufen — Drücken\n\n"
                    "### Schritt 1: Prüfen (max. 10 Sekunden)\n\n"
                    "**Ansprechen**: Laut + deutlich, am besten mit Namen, "
                    "wenn bekannt. 'Hören Sie mich? Können Sie mich anschauen?'\n\n"
                    "**Schütteln**: An den Schultern, **nicht am Kopf** "
                    "(Halswirbelsäulen-Verletzung möglich).\n\n"
                    "Falls keine Reaktion → bewusstlos. **Hilfe rufen!**\n\n"
                    "**Atmung prüfen**:\n"
                    "1. Kopf vorsichtig **überstrecken** (Kinn nach oben, "
                    "Stirn runter) → Atemwege öffnen\n"
                    "2. Mit deiner Wange dicht über Mund + Nase der Person, "
                    "Blick auf den Brustkorb\n"
                    "3. **Sehen** (hebt sich der Brustkorb?), **hören** "
                    "(Atemgeräusche?), **fühlen** (warmer Atem an der Wange?)\n"
                    "4. **Maximal 10 Sekunden!**\n\n"
                    "**Schnappatmung ist KEINE normale Atmung** — sieht aus wie "
                    "vereinzelte Schluckbewegungen, ist aber bereits Herzstillstand. "
                    "→ Sofort CPR beginnen!\n\n"
                    "### Schritt 2: Rufen (Notruf + Helfer organisieren)\n\n"
                    "**112 anrufen** oder durch jemand anders rufen lassen, "
                    "Schema 5 W. Wenn allein: erst Notruf, dann CPR (Ausnahme: "
                    "Ertrinkung, Kind — dort erst 1 min CPR, dann Notruf).\n\n"
                    "**Zweiten Helfer holen** lassen — abwechselnd CPR ist "
                    "wirksamer (du wirst nach 2 min müde).\n\n"
                    "**AED holen** lassen. Bei uns gibt es einen im Erste-Hilfe-"
                    "Raum Halle 1.\n\n"
                    "### Schritt 3: Drücken (Herzdruckmassage)\n\n"
                    "**Position der Hände**: Untere Hälfte des Brustbeins, "
                    "direkt zwischen den Brustwarzen. Handballen der einen Hand, "
                    "darüber die zweite Hand, Finger verschränkt aber nicht "
                    "auf den Rippen.\n\n"
                    "**Tiefe**: **5–6 cm** beim Erwachsenen. Klingt brutal, ist "
                    "aber nötig — flacher gedrückt zirkuliert das Blut nicht.\n"
                    "Bei Kindern (1–8 J.) etwa 5 cm mit nur einer Hand, "
                    "bei Säuglingen 4 cm mit 2 Fingern.\n\n"
                    "**Frequenz**: **100–120 / Minute**. Eselsbrücke: Rhythmus "
                    "von 'Stayin' Alive' (Bee Gees) oder 'Highway to Hell' (AC/DC). "
                    "Genau dieser Beat ist die richtige Frequenz.\n\n"
                    "**30:2 oder durchgehend**: Klassisch 30 Kompressionen, "
                    "2 Beatmungen. Neue Empfehlung: **durchgehend drücken**, "
                    "Beatmung nur wenn man's gelernt hat und sich sicher fühlt. "
                    "Durchgehende Kompression rettet mehr Leben als Pausen "
                    "für unsichere Beatmung.\n\n"
                    "**Bis wann?**\n"
                    "- Rettungsdienst übernimmt\n"
                    "- Person fängt selbst wieder zu atmen an\n"
                    "- Eigene Kräfte versagen\n\n"
                    "## Stabile Seitenlage\n\n"
                    "**NUR** wenn die Person **bewusstlos** ist, **aber normal "
                    "atmet**. Wer atmet, braucht keine CPR — aber die Zunge "
                    "könnte die Atemwege blockieren.\n\n"
                    "Ablauf (kurz):\n"
                    "1. Person auf den Rücken legen, eigener Arm in 90° nach oben\n"
                    "2. Gegenüberliegenden Arm + Bein anwinkeln\n"
                    "3. Über das Knie zur Seite drehen\n"
                    "4. Kopf überstrecken, Mund Richtung Boden — Erbrochenes "
                    "kann ablaufen\n\n"
                    "**Alle 1–2 Minuten Atmung kontrollieren.**\n\n"
                    "## AED (Automatisierter Externer Defibrillator)\n\n"
                    "Der AED ist die wichtigste technische Hilfe im Erste-Hilfe-"
                    "Kasten der Industrie. Er kann **Kammerflimmern** "
                    "(häufigste Ursache eines plötzlichen Herzstillstands) durch "
                    "einen kontrollierten Stromstoß beenden.\n\n"
                    "**Wichtig:** Der AED ist **für Laien gemacht**:\n\n"
                    "1. **Einschalten** — Sprachanweisung beginnt\n"
                    "2. **Klebepads aufkleben** wie auf Geräten gezeigt "
                    "(meist rechts oben Brust + links unten Rippen)\n"
                    "3. **Niemand berührt den Patienten** — der AED analysiert\n"
                    "4. AED sagt: 'Schock empfohlen' → Knopf drücken (alle "
                    "weg!). Oder 'Kein Schock empfohlen' → CPR weiter.\n"
                    "5. **CPR fortsetzen**, AED gibt alle 2 Minuten neue "
                    "Analyse-Aufforderung\n\n"
                    "**Du kannst nichts kaputt machen.** Der AED gibt keinen "
                    "Schock, wenn keiner nötig ist. Im Zweifel: **immer "
                    "anwenden.** Falsche Anwendung gibt es praktisch nicht — "
                    "Nicht-Anwendung kostet Leben.\n\n"
                    "**Bei uns** ist der AED bei der Pförtnerei und im Erste-"
                    "Hilfe-Raum (gelb-grüne Wandhalterung mit Glasfront). "
                    "Standort merken, im Notfall ist keine Zeit zu suchen."
                ),
            ),
            ModulDef(
                titel="Wunden, Verbrennungen, Schock",
                inhalt_md=(
                    "## Blutungen — die Hierarchie der Maßnahmen\n\n"
                    "Eine **arterielle Blutung** (hellrot, spritzend) kann in "
                    "**3–5 Minuten** zum Verbluten führen. Eine **venöse Blutung** "
                    "(dunkelrot, fließend) ist meist weniger akut, aber bei "
                    "größerer Wunde ebenfalls lebensbedrohlich.\n\n"
                    "### Stufenfolge\n\n"
                    "**1. Direkter Druck:** Sterile Wundauflage auf die Wunde, "
                    "mit der Hand fest draufdrücken. Wenn keine Wundauflage zur "
                    "Hand: sauberes Tuch, T-Shirt, notfalls bloße Hand "
                    "(Einmalhandschuhe falls verfügbar — Infektionsschutz für "
                    "beide).\n\n"
                    "**2. Druckverband**: Wundauflage auf die Wunde, darüber "
                    "ein dickes Polster (z. B. zweite Mullbinde oder Päckchen), "
                    "darüber die Mullbinde fest umwickeln. Das Polster komprimiert "
                    "die Wunde, das Wickeln hält es in Position.\n\n"
                    "**3. Hochlagern**: Verletzte Extremität über Herzhöhe — "
                    "reduziert den Blutdruck im verletzten Gefäß.\n\n"
                    "**4. Wenn weiterblutet**: zweiter Druckverband über den "
                    "ersten (**nie** den ersten abnehmen — das Gerinnsel reißt ab).\n\n"
                    "**5. Notfall-Maßnahme Tourniquet:** Nur bei lebens"
                    "gefährlicher Blutung an Extremitäten, die mit Druckverband "
                    "nicht zu stoppen ist. **5–10 cm oberhalb** der Wunde, "
                    "fest abschnüren bis Blutung stoppt. **Uhrzeit notieren!** "
                    "Tourniquet darf nicht länger als **2 Stunden** liegen, "
                    "sonst dauerhafte Schäden.\n\n"
                    "### Was NICHT tun\n"
                    "- Fremdkörper aus tiefen Wunden **nicht ziehen** — sie "
                    "können das Gefäß abdichten. In Position belassen, drumherum "
                    "verbinden.\n"
                    "- Wunden nicht **mit Watte** versorgen (Fasern verkleben "
                    "in der Wunde)\n"
                    "- Keine **Hausmittel** in die Wunde — Honig, Salbe, Alkohol\n"
                    "- Wunde nicht 'auswaschen' — bei Schmutz tatsächlich gut, "
                    "bei tiefer Wunde Erstversorgung dem Arzt überlassen\n\n"
                    "## Verbrennungen\n\n"
                    "Eingeteilt in **Grade**:\n"
                    "- **Grad 1**: Rötung, schmerzhaft — wie Sonnenbrand\n"
                    "- **Grad 2**: Blasenbildung, sehr schmerzhaft\n"
                    "- **Grad 3**: Weiß/schwarze Verkohlung, kein Schmerz mehr "
                    "(Nerven zerstört)\n\n"
                    "Und nach **Ausdehnung** (9er-Regel): Handfläche der Person "
                    "= ca. 1 % Körperoberfläche. Ab 10 % Grad-2-Verbrennung "
                    "oder 5 % Grad-3 ist es ein **Notfall mit Schockgefahr** → "
                    "112.\n\n"
                    "### Erstversorgung\n\n"
                    "**Kühlen mit lauwarmem Wasser** (15–20 °C, NICHT eiskalt) "
                    "für **10–20 Minuten** — länger nur unter Aufsicht des Arztes, "
                    "weil Hypothermie-Gefahr entsteht.\n\n"
                    "**Bei großflächigen Verbrennungen (> 10 %)**: gar nicht "
                    "kühlen oder nur kurz die Hauptstelle — Unterkühlungsrisiko "
                    "überwiegt. Decke locker auflegen, 112.\n\n"
                    "**Niemals:**\n"
                    "- **Eiswasser, Eis** direkt aufs Gewebe → Erfrierung der "
                    "verbrannten Stellen\n"
                    "- **Kleidung abreißen**, die in der Wunde klebt — drum "
                    "herum schneiden, Rest lassen\n"
                    "- **Hausmittel** wie Mehl, Butter, Salbe, Zahnpasta — alles "
                    "kontraproduktiv, Infektionsrisiko, Arzt kann schlechter "
                    "behandeln\n"
                    "- **Brandblasen aufstechen** — sind eine natürliche "
                    "Wundauflage, schützen vor Infektion\n\n"
                    "### Verätzungen (Chemikalien)\n\n"
                    "Wie Verbrennungen, aber:\n"
                    "- **Pulverförmige Chemikalien erst trocken abwischen**, "
                    "dann spülen (Wasser kann mit Pulver reagieren)\n"
                    "- **Mindestens 15 Minuten** mit viel Wasser spülen\n"
                    "- **Augen-Verätzung**: Augendusche oder Wasserstrahl von "
                    "innen nach außen, **15+ Minuten**, danach Arzt\n"
                    "- Sicherheitsdatenblatt der Chemikalie mitnehmen zum Arzt\n\n"
                    "## Schock — die unsichtbare Lebensgefahr\n\n"
                    "Schock = **akutes Versagen des Kreislaufs** durch Blutverlust, "
                    "Flüssigkeitsverlust (Verbrennung!), schwere Verletzung, "
                    "Herzversagen oder Allergie (anaphylaktisch).\n\n"
                    "### Zeichen\n"
                    "- **Blasse, kalte, schweißige** Haut\n"
                    "- **Schneller, flacher** Puls (oft >100 / min)\n"
                    "- **Unruhe, Verwirrtheit** wechselt mit Apathie\n"
                    "- **Frieren**, Zittern\n"
                    "- **Übelkeit**, ggf. Erbrechen\n\n"
                    "### Erste-Hilfe-Maßnahmen\n\n"
                    "1. **Hinlegen** — bei Bewusstsein flach oder mit leicht "
                    "**hochgelagerten Beinen** (Auto-Transfusion)\n"
                    "2. **Beine nicht hoch** bei Verletzung von Bein/Bauch, "
                    "Wirbelsäule, Schädel\n"
                    "3. **Warm halten** — Rettungsdecke (silbern nach innen) "
                    "oder Jacke\n"
                    "4. **Beruhigen**, ständig ansprechen — Bewusstsein erhalten\n"
                    "5. **Kein Essen, kein Trinken** — bei OP-Bedarf gefährlich\n"
                    "6. **Atmung + Bewusstsein** alle 1–2 Minuten kontrollieren\n"
                    "7. **112**, falls noch nicht geschehen\n\n"
                    "### Anaphylaktischer Schock\n\n"
                    "Allergische Reaktion auf Insektenstich, Nahrungsmittel, "
                    "Medikament. Erkennbar an: Hautrötung, Quaddeln, Atemnot, "
                    "Halsschwellung. **Lebensgefahr** innerhalb von Minuten.\n\n"
                    "- 112 mit **Hinweis** 'anaphylaktischer Schock'\n"
                    "- Wenn die Person einen **Adrenalin-Pen** dabei hat "
                    "(EpiPen, Jext): seitliche Oberschenkelmuskulatur, durch "
                    "die Kleidung\n"
                    "- Atemwege offen halten, ggf. Reanimation"
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
                    "## Was ist GHS und warum global einheitlich?\n\n"
                    "**GHS** steht für *Globally Harmonised System of Classification "
                    "and Labelling of Chemicals* — ein UN-System, das die Kenn"
                    "zeichnung von Chemikalien weltweit standardisiert. In der EU "
                    "ist es seit 2009 verpflichtend (CLP-Verordnung 1272/2008). "
                    "Damit hat ein Bauarbeiter in Deutschland dieselben Pikto"
                    "gramme vor sich wie eine Chemikerin in Brasilien — wichtig, "
                    "weil Sprache versagen kann, Bilder aber nicht.\n\n"
                    "Wer einen Gefahrstoff in der Hand hält, MUSS die Bedeutung "
                    "der Piktogramme kennen. Jährliche Wiederholung ist Pflicht "
                    "nach § 14 GefStoffV.\n\n"
                    "## Die neun GHS-Piktogramme im Detail\n\n"
                    "Alle Piktogramme sind **rote Raute** auf weißem Grund mit "
                    "schwarzem Symbol — also weithin sichtbar.\n\n"
                    "| Code | Symbol | Bedeutung | Beispiel-Stoffe |\n"
                    "|---|---|---|---|\n"
                    "| GHS01 | Explodierende Bombe | Explosionsgefährlich | Schwarzpulver, alte Munition |\n"
                    "| GHS02 | Flamme | Entzündbar (Flüssigkeit/Gas/Feststoff) | Aceton, Benzin, Wasserstoff |\n"
                    "| GHS03 | Flamme über Kreis | Oxidierend, brandfördernd | Wasserstoffperoxid, Salpeter |\n"
                    "| GHS04 | Gasflasche | Gase unter Druck | Sauerstoff, Stickstoff, Propan |\n"
                    "| GHS05 | Ätzwirkung | Verätzt Haut + Augen | Natronlauge, Salzsäure |\n"
                    "| GHS06 | Totenkopf + Knochen | Akut giftig (auch kleine Mengen) | Cyanide, Methanol |\n"
                    "| GHS07 | Ausrufezeichen | Reizend, sensibilisierend, akut schädlich | Ammoniak (verdünnt), Lacke |\n"
                    "| GHS08 | Mensch mit Stern (CMR) | Krebserzeugend / erbgutverändernd / fortpflanzungsgefährdend | Asbest, Chrom(VI), Formaldehyd |\n"
                    "| GHS09 | Toter Fisch + Baum | Gewässer-/Umweltgefährdend | Pestizide, Schwermetall-Salze |\n\n"
                    "**Wichtig zur GHS08-Markierung (CMR-Stoffe):** Diese Stoffe "
                    "wirken oft nicht akut, sondern verursachen erst nach Monaten "
                    "oder Jahren Schäden. Hier ist die persönliche Schutzaus"
                    "rüstung (PSA) keine Option, sondern überlebenswichtig.\n\n"
                    "## H-Sätze (Hazard) — wovor warnen sie?\n\n"
                    "H-Sätze sind kurze Texte mit Code, die die **konkrete Gefahr** "
                    "benennen. Beispiele aus dem Werkstattalltag:\n\n"
                    "- **H225** Flüssigkeit und Dampf leicht entzündbar (Ethanol)\n"
                    "- **H290** Kann gegenüber Metallen korrosiv sein (Akku-Säure)\n"
                    "- **H302** Gesundheitsschädlich bei Verschlucken (Lacklöser)\n"
                    "- **H314** Verursacht schwere Verätzungen (Natronlauge)\n"
                    "- **H319** Verursacht schwere Augenreizung (Reiniger)\n"
                    "- **H332** Gesundheitsschädlich bei Einatmen (Schweißrauche)\n"
                    "- **H350** Kann Krebs erzeugen (Asbest, Formaldehyd)\n"
                    "- **H400** Sehr giftig für Wasserorganismen (Kühlschmierstoffe)\n\n"
                    "Die vollständige Liste hat über 100 H-Sätze — du musst sie "
                    "nicht auswendig kennen, aber **lesen können**, was auf der "
                    "Flasche steht.\n\n"
                    "## P-Sätze (Precautionary) — wie schützt man sich?\n\n"
                    "P-Sätze geben **konkrete Verhaltensregeln**. Beispiele:\n\n"
                    "- **P210** Von Hitze, heißen Oberflächen, Funken fernhalten\n"
                    "- **P233** Behälter dicht verschlossen halten\n"
                    "- **P260** Staub, Dampf, Nebel nicht einatmen\n"
                    "- **P280** Schutzhandschuhe + Schutzbrille tragen\n"
                    "- **P301+310** Bei Verschlucken: SOFORT Giftinformationszentrum anrufen\n"
                    "- **P305+351+338** Bei Augenkontakt: einige Minuten lang spülen, Kontaktlinsen entfernen\n"
                    "- **P391** Verschüttete Mengen auffangen\n"
                    "- **P501** Inhalt/Behälter umweltgerecht entsorgen\n\n"
                    "## Wie ein Etikett aussehen muss\n\n"
                    "Jeder Gefahrstoff-Behälter muss enthalten:\n\n"
                    "1. **Produktbezeichnung** (Handelsname)\n"
                    "2. **Inhaltsstoffe** (mindestens die gefährlichen)\n"
                    "3. **GHS-Piktogramme** (s.o.)\n"
                    "4. **Signalwort:** 'Achtung' (weniger schwer) oder 'Gefahr' "
                    "(schwerwiegend)\n"
                    "5. **Alle H-Sätze**\n"
                    "6. **Wichtigste P-Sätze** (mindestens 6, oft Auswahl)\n"
                    "7. **Lieferant** mit Adresse + Telefon\n"
                    "8. **Nominalmenge** (Volumen/Masse)\n\n"
                    "**Wenn du einen unbeschrifteten Behälter findest** (z. B. "
                    "in eine Reinigungs-Sprühflasche umgefüllt): **nicht verwenden**, "
                    "Vorgesetzte informieren. Das Umfüllen ohne neue Kennzeichnung "
                    "ist eine Ordnungswidrigkeit (§ 22 GefStoffV) und lebens"
                    "gefährlich für den nächsten User."
                ),
            ),
            ModulDef(
                titel="Sicherheitsdatenblatt (SDB) lesen",
                inhalt_md=(
                    "## Was ist ein Sicherheitsdatenblatt?\n\n"
                    "Ein **Sicherheitsdatenblatt (SDB)** ist die rechtlich "
                    "verbindliche Informations-Pflicht des Lieferanten gegenüber "
                    "dem gewerblichen Verwender (Art. 31 REACH-Verordnung). Es "
                    "enthält alle Daten, die du brauchst, um den Stoff sicher "
                    "zu lagern, zu verwenden, im Notfall richtig zu reagieren "
                    "und schließlich fachgerecht zu entsorgen.\n\n"
                    "**Pflicht des Arbeitgebers:** Für jeden Gefahrstoff im "
                    "Betrieb muss ein aktuelles SDB vorhanden + am Arbeitsplatz "
                    "zugänglich sein (Papierordner oder digital). **Spätestens "
                    "alle 3 Jahre** neu beim Lieferanten anfordern, weil sich "
                    "Klassifizierungen ändern können.\n\n"
                    "## Die 16 Abschnitte (REACH Anhang II)\n\n"
                    "Jedes SDB hat genau diese Reihenfolge. Im Notfall musst du "
                    "**schnell** den richtigen Abschnitt finden — daher hier "
                    "die Übersicht mit Praxis-Tipp je Abschnitt:\n\n"
                    "| Nr | Abschnitt | Wann brauchst du das? |\n"
                    "|---|---|---|\n"
                    "| 1 | Bezeichnung + Lieferant | Identifizieren wann angerufen werden soll |\n"
                    "| 2 | **Mögliche Gefahren** | Beim ersten Kontakt mit dem Stoff |\n"
                    "| 3 | Zusammensetzung | Bei Allergie-Verdacht prüfen |\n"
                    "| 4 | **Erste-Hilfe-Maßnahmen** | Bei Unfall sofort lesen |\n"
                    "| 5 | **Brandbekämpfung** | Welches Löschmittel ist erlaubt? |\n"
                    "| 6 | **Unbeabsichtigte Freisetzung** | Bei Leck/Verschütten |\n"
                    "| 7 | Handhabung + Lagerung | Bei Einlagerung neuer Stoffe |\n"
                    "| 8 | **Expositionsbegrenzung + PSA** | Welche Schutzkleidung? |\n"
                    "| 9 | Physikalische Eigenschaften | Bei Prozessauslegung |\n"
                    "| 10 | Stabilität + Reaktivität | Zusammenlagerungs-Verbote |\n"
                    "| 11 | Toxikologie | Bei Gesundheitsschäden / Vergiftung |\n"
                    "| 12 | Ökologie | Bei Versickerung in Erdreich |\n"
                    "| 13 | Entsorgung | Welcher Abfallschlüssel? |\n"
                    "| 14 | Transport | UN-Nummer, Gefahrgutklasse |\n"
                    "| 15 | Rechtsvorschriften | Bei Audit/Behördenanfrage |\n"
                    "| 16 | Sonstiges | Historie + Erläuterungen |\n\n"
                    "## Die fünf wichtigsten Abschnitte für Beschäftigte\n\n"
                    "Du musst nicht alle 16 Abschnitte auswendig kennen, aber "
                    "**im Notfall** musst du diese fünf finden können:\n\n"
                    "### Abschnitt 2: Mögliche Gefahren\n\n"
                    "Enthält die GHS-Piktogramme, das Signalwort (Achtung/Gefahr) "
                    "und ALLE H-Sätze. Hier siehst du sofort, wie kritisch der "
                    "Stoff ist.\n\n"
                    "### Abschnitt 4: Erste-Hilfe-Maßnahmen\n\n"
                    "Untergliedert in:\n"
                    "- Bei **Einatmen** (z. B. an die frische Luft bringen, "
                    "Notarzt bei Atemnot)\n"
                    "- Bei **Hautkontakt** (z. B. mit Wasser und Seife abwaschen "
                    "— manchmal aber explizit NICHT, z. B. bei Calciumcarbid: "
                    "trocken abkehren!)\n"
                    "- Bei **Augenkontakt** (15 min spülen, Arzt)\n"
                    "- Bei **Verschlucken** (Mund spülen, NIE Erbrechen ohne "
                    "Anweisung)\n"
                    "- **Hinweise für den Arzt** (Antidot? Spezielle Behandlung?)\n\n"
                    "### Abschnitt 5: Brandbekämpfung\n\n"
                    "Welches Löschmittel passt — und welches ist **verboten**. "
                    "Beispiel: bei manchen Metallhydriden ist Wasser tödlich.\n\n"
                    "### Abschnitt 6: Unbeabsichtigte Freisetzung\n\n"
                    "Was tun bei Verschütten? Welches Bindemittel nehmen? "
                    "Bei welchen Mengen Spezialfirma rufen?\n\n"
                    "### Abschnitt 8: Expositionsbegrenzung + PSA\n\n"
                    "**Konkret welche PSA** brauchst du beim Umgang? Welche "
                    "Handschuhe (Nitril, Butyl, Neopren — Material macht Unter"
                    "schied)? Welcher Atemschutz (FFP3, A2-Filter)? Welche "
                    "Schutzbrille (Korbbrille, Gesichtsschutz)?\n\n"
                    "Hier stehen auch **Arbeitsplatzgrenzwerte** (AGW) und "
                    "**biologische Grenzwerte** (BGW) — wichtig für die "
                    "Gefährdungsbeurteilung.\n\n"
                    "## Beim Eingang neuer Chemikalien\n\n"
                    "1. SDB **vor** der ersten Verwendung lesen\n"
                    "2. SDB in den Ordner / das System einpflegen\n"
                    "3. **Gefährdungsbeurteilung** für die geplante Tätigkeit "
                    "aktualisieren\n"
                    "4. **Betriebsanweisung** (TRGS 555) im Format DGUV-typisch "
                    "schreiben — knapper als das SDB, in der Sprache der Beschäftigten\n"
                    "5. **Beschäftigte unterweisen** — vor Beginn der Tätigkeit\n\n"
                    "**Kein Stoff darf** im Betrieb verwendet werden, ohne dass "
                    "diese Schritte abgeschlossen sind. Wer Gefahrstoffe ohne "
                    "Unterweisung benutzt, riskiert seine Gesundheit und kann "
                    "im Schadensfall persönlich haften."
                ),
            ),
            ModulDef(
                titel="Lagerung & Substitution",
                inhalt_md=(
                    "## Warum Lagerung wichtig ist\n\n"
                    "Ein großer Teil der Gefahrstoff-Unfälle passiert **nicht** "
                    "während des bestimmungsgemäßen Gebrauchs, sondern bei "
                    "Lagerung, Transport, Reinigung. Unsachgemäße Lagerung kann "
                    "zu Bränden, Explosionen, Vergiftungen und Umweltschäden "
                    "führen — manchmal **Stunden oder Tage** nach dem eigentlichen "
                    "Versäumnis (Selbstentzündung, freigesetzte Dämpfe).\n\n"
                    "**Rechtsgrundlage:** TRGS 510 (Technische Regel für Gefahr"
                    "stoffe) regelt die Lagerung mit Mengenstaffeln und Schutz"
                    "klassen.\n\n"
                    "## Die wichtigsten Lager-Grundsätze\n\n"
                    "### Zusammenlagerungs-Verbote nach TRGS 510\n\n"
                    "Bestimmte Stoffe dürfen **nicht** im selben Lager-Bereich "
                    "stehen, weil ihre Kombination im Schadensfall katastrophal "
                    "wirken kann:\n\n"
                    "| Verboten zusammen | Warum |\n"
                    "|---|---|\n"
                    "| Säuren + Laugen | Heftige Neutralisation mit Verspritzen |\n"
                    "| Säuren + Cyanide | Bildung von Blausäure-Gas, tödlich |\n"
                    "| Brennbar + Oxidierend | Spontan-Brand bei Vermischung |\n"
                    "| Brennbar + Druckgase | Explosionsgefahr im Brandfall |\n"
                    "| Giftig + Lebensmittel | Kontamination, Verwechslung |\n"
                    "| Wassergefährdend + ohne Auffangwanne | Boden-/Grundwasser-Schaden |\n\n"
                    "Bei mehreren Stoffen in einem Lager-Raum: **getrennte Schränke** "
                    "oder ausreichende räumliche Trennung. Im Zweifel TRGS 510 "
                    "Anhang 4 (Zusammenlagerungs-Matrix) konsultieren.\n\n"
                    "### Kennzeichnung am Lagerort\n\n"
                    "- **Außen** am Lager: Gefahrenkennzeichnung der größten "
                    "vorhandenen Gefahr (z. B. roter Aufkleber 'Entzündbare "
                    "Flüssigkeiten')\n"
                    "- **Innen**: jede Verpackung muss ein lesbares Original-"
                    "Etikett haben (s. Modul 1)\n"
                    "- **Bei Umfüllung** in andere Behälter: neue Kennzeichnung "
                    "ist Pflicht (§ 8 GefStoffV) — keine Reinigungslösung in "
                    "ehemalige Wasserflasche!\n\n"
                    "### Auffangwannen für Flüssigkeiten\n\n"
                    "Wassergefährdende Flüssigkeiten brauchen **doppelte Sicherung** "
                    "gegen Boden-/Grundwasser-Kontamination. Auffangwanne muss "
                    "mindestens das Volumen des **größten Einzelbehälters** "
                    "aufnehmen können (bei kleinen Mengen 10 % der Gesamtmenge).\n\n"
                    "Auffangwannen regelmäßig auf **Risse, Korrosion, Lochfraß** "
                    "prüfen und protokollieren. Defekte Wanne = Lagerverbot bis "
                    "Austausch.\n\n"
                    "### Belüftung\n\n"
                    "Bei flüchtigen Lösungsmitteln, Säuren, Ammoniak: **technische "
                    "Lüftung** erforderlich, mindestens 0,4-facher Luftwechsel "
                    "pro Stunde. In kleinen Lägern auch natürliche Lüftung "
                    "(beide Hochseiten frei) ausreichend, sofern keine Mitarbei"
                    "tenden dauerhaft anwesend.\n\n"
                    "### Zugangs-Sicherung\n\n"
                    "Stoffe der **Giftgruppe T+/T** und CMR-Stoffe (krebs"
                    "erzeugend, erbgutverändernd, fortpflanzungs"
                    "gefährdend) MÜSSEN abschließbar gelagert werden. Schlüssel-"
                    "Vergabe nur an unterwiesene Personen mit dokumentierter "
                    "Befugnis.\n\n"
                    "## Substitutionspflicht (§ 6 GefStoffV)\n\n"
                    "**Vor** dem Einsatz eines Gefahrstoffs muss der Arbeitgeber "
                    "prüfen, ob er durch einen **weniger gefährlichen Stoff oder "
                    "ein weniger gefährliches Verfahren** ersetzt werden kann. "
                    "Diese Prüfung ist **schriftlich** zu dokumentieren — auch "
                    "wenn das Ergebnis 'keine Substitution möglich' lautet.\n\n"
                    "### Beispiele erfolgreicher Substitution\n\n"
                    "- **Bremsenreiniger** auf Acetonbasis statt mit chlorierten "
                    "Kohlenwasserstoffen → reduziert CMR-Risiko\n"
                    "- **Wasserbasierte Reinigungsmittel** statt Lösungsmittel-"
                    "Reiniger → weniger Brand-/Atemwegsgefahr\n"
                    "- **Vorgemischte Beton-Fertigteile** statt Quarzstaub-"
                    "Mörtelmischung → reduziert Silikose-Risiko\n"
                    "- **HEPA-Staubsauger** statt Druckluft → kein Aufwirbeln "
                    "feinster Stäube\n"
                    "- **Cobalt-/Nickel-freie Kühlschmierstoffe** statt klassische "
                    "wassermischbare KSS → weniger Allergie-Risiko\n\n"
                    "Substitution ist kein 'nice-to-have', sondern **rechtliche "
                    "Pflicht** der Schutzhierarchie (vor PSA als letzte Schutz"
                    "stufe). Wer trotz verfügbarer Substitute weiter mit dem "
                    "gefährlicheren Stoff arbeitet, kann im Schadensfall haftbar "
                    "gemacht werden."
                ),
            ),
            ModulDef(
                titel="Verhalten im Schadensfall",
                inhalt_md=(
                    "## Vor dem Notfall: Vorbereitung\n\n"
                    "**Vor** der Arbeit mit jedem Gefahrstoff musst du wissen:\n"
                    "- Wo ist das **Sicherheitsdatenblatt** (Papierordner oder "
                    "Intranet-Link)?\n"
                    "- Wo ist die nächste **Augendusche** und **Notdusche**?\n"
                    "- Wo ist das **Bindemittel** für diesen Stoff?\n"
                    "- Welche **Telefonnummer** des Giftnotrufs gilt hier?\n"
                    "- Wo ist der **Notausschalter** für Lüftung / Maschine?\n\n"
                    "Wenn du eine dieser Fragen nicht beantworten kannst: **frag "
                    "deinen Vorgesetzten, bevor du anfängst**. Im Notfall ist "
                    "keine Zeit zum Suchen.\n\n"
                    "## Bei Hautkontakt\n\n"
                    "1. **Kontaminierte Kleidung sofort entfernen** — auch "
                    "Schuhe, Socken, Uhren. Der Stoff dringt sonst weiter durch "
                    "die Haut.\n"
                    "2. **Betroffene Haut spülen** — reichlich lauwarmes Wasser, "
                    "**mindestens 15 Minuten** (länger bei Säuren/Laugen).\n"
                    "3. **NUR seifenlos** — viele Stoffe werden durch Seife "
                    "aktiviert / besser aufgenommen.\n"
                    "4. **SDB Abschnitt 4 prüfen** — manche Stoffe wie Calcium"
                    "carbid, Phosphor dürfen NICHT mit Wasser in Kontakt kommen "
                    "(reagiert heftig)!\n"
                    "5. Bei brennbaren/giftigen Stoffen: ggf. **Notdusche** "
                    "unter Vollkleidung benutzen.\n"
                    "6. **Arzt aufsuchen** bei jeder mehr-als-banalen Verätzung. "
                    "SDB mitnehmen.\n\n"
                    "## Bei Augenkontakt\n\n"
                    "**Augen sind das verletzlichste Organ** — innerhalb "
                    "weniger Sekunden kann die Hornhaut dauerhaft geschädigt "
                    "werden, besonders durch Laugen.\n\n"
                    "1. **Sofort zur Augendusche** — Sekunden zählen\n"
                    "2. **Lider mit den Fingern aufspreizen** — Wasserstrahl "
                    "von der Nase zur Schläfe (nicht in das andere Auge)\n"
                    "3. **Mindestens 15 Minuten** spülen, bei Laugen länger "
                    "(20-30 min)\n"
                    "4. **Kontaktlinsen entfernen** (nach kurzem Spülen)\n"
                    "5. **Arzt / Augenklinik** in jedem Fall, auch wenn der "
                    "Schmerz nachlässt\n\n"
                    "## Verschütten / Leck\n\n"
                    "### Bei kleinen Mengen (< 1 l)\n\n"
                    "1. **Eigenschutz**: passende Handschuhe + Augenschutz an, "
                    "ggf. Atemschutz\n"
                    "2. **Sofort Bindemittel** aufstreuen — bei säurefester "
                    "Lagerung: säurebindendes Granulat; allgemein: Universal-"
                    "Bindemittel (z. B. Chemizorb)\n"
                    "3. **Mit Schaufel** in Gefahrstoffbehälter geben\n"
                    "4. **Vorgesetzten informieren**\n\n"
                    "### Bei großen Mengen oder unbekanntem Stoff\n\n"
                    "1. **Bereich räumen** — alle anderen aus der Halle\n"
                    "2. **Lüftung an** oder Türen offen\n"
                    "3. **Feuerwehr 112** rufen mit Hinweis 'Gefahrstoff-Unfall'\n"
                    "4. **SDB bereithalten** für die Einsatzkräfte\n"
                    "5. **Niemand betritt** den Bereich ohne Vollschutz\n\n"
                    "### Was NICHT tun\n\n"
                    "- **Niemals mit Wasser nachspülen**, ohne zu prüfen — kann "
                    "Stoff verteilen und Reaktion auslösen\n"
                    "- **Nicht zurück** zur Stelle, um 'noch was zu retten'\n"
                    "- **Nicht mit Lappen aufwischen** — Wundkontakt-Gefahr\n\n"
                    "## Ein-/Verschlucken\n\n"
                    "Selten in der Werkstatt, aber möglich (Versehen, Mund-"
                    "Spritzen):\n\n"
                    "1. **Mund mit Wasser ausspülen**, nicht schlucken\n"
                    "2. **NIE Erbrechen auslösen** ohne explizite Anweisung — "
                    "bei Säuren/Laugen würde es die Speiseröhre erneut verätzen\n"
                    "3. **Giftnotruf anrufen** (siehe unten) und Anweisungen "
                    "befolgen\n"
                    "4. **SDB Abschnitt 4** für Hinweise zum behandelnden Arzt\n"
                    "5. **Verpackung / Etikett mitnehmen** ins Krankenhaus\n\n"
                    "## Giftnotruf-Zentralen Deutschland\n\n"
                    "Erreichbar 24/7. Nimm SDB oder Etikett zur Hand bevor du "
                    "anrufst.\n\n"
                    "- **Berlin**: 030 - 19240 (für Brandenburg + Berlin)\n"
                    "- **Bonn**: 0228 - 19240 (NRW)\n"
                    "- **Mainz**: 06131 - 19240 (Hessen, RLP, Saarland)\n"
                    "- **München**: 089 - 19240 (Bayern)\n"
                    "- **Erfurt**: 0361 - 730730 (Sachsen, Sachsen-Anhalt, Thüringen)\n"
                    "- **Freiburg**: 0761 - 19240 (Baden-Württemberg)\n"
                    "- **Göttingen**: 0551 - 19240 (Niedersachsen, Bremen)\n\n"
                    "Bei **Vergiftung** kann jeder dieser Notrufe ein Antidot "
                    "(Gegengift) empfehlen oder die richtige Klinik zuweisen. "
                    "**Du musst nicht warten**, bis der Notarzt da ist."
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
                    "## Das TOP-Prinzip — PSA ist die LETZTE Schutzlinie\n\n"
                    "Bevor wir über persönliche Schutzausrüstung reden: PSA ist "
                    "**immer der letzte Ausweg**. Das deutsche Arbeitsschutzgesetz "
                    "(§ 4 ArbSchG) verlangt vom Arbeitgeber, Gefahren in dieser "
                    "Reihenfolge zu beseitigen:\n\n"
                    "1. **T**echnisch — Gefahr an der Quelle ausschalten "
                    "(geschlossene Maschinenkapselung, Absauganlage, Schalldämpfer)\n"
                    "2. **O**rganisatorisch — Gefahr räumlich/zeitlich begrenzen "
                    "(getrennte Bereiche, Schichtmodelle, Wartung außerhalb der "
                    "Produktion)\n"
                    "3. **P**ersönlich — wenn 1 + 2 nicht möglich, PSA als "
                    "individueller Schutz\n\n"
                    "Wer PSA verteilt, weil die Maschinenabsaugung zu teuer wäre, "
                    "umgeht das Gesetz. Wer als Beschäftigte:r PSA bekommt, "
                    "akzeptiert sie als **zusätzliche** Maßnahme, nicht als "
                    "Ersatz für saubere Technik.\n\n"
                    "## Die acht PSA-Kategorien im Detail\n\n"
                    "### 1. Kopfschutz (Schutzhelm)\n\n"
                    "Pflicht überall, wo herabfallende Gegenstände oder Anstoß-"
                    "gefahr besteht (Werkhalle mit Kran, Baustelle, Stahlbau). "
                    "Normen: **EN 397** (Industrie), **EN 14052** (Hochleistung). "
                    "Farbcode oft betriebsintern: gelb=Arbeiter, weiß=Vorgesetzter, "
                    "blau=Elektriker.\n\n"
                    "### 2. Augen- und Gesichtsschutz\n\n"
                    "- **Schutzbrille** (EN 166) bei mechanischer Gefahr "
                    "(Funken, Späne, Splitter)\n"
                    "- **Korbbrille** für Spritzer von Chemikalien\n"
                    "- **Gesichtsschutzschirm** bei großflächigen Spritzern + "
                    "Schweißarbeiten kombiniert mit Schweißerblende\n"
                    "- **Schweißerschutzhelm** mit Filterstufe (DIN 4647), "
                    "Stufen 9 bis 15 je nach Stromstärke\n\n"
                    "Achtung: Korrekturbrillen-Träger:innen brauchen **Über"
                    "brillen** oder Schutzbrillen mit Sehkorrektur — Arbeitgeber "
                    "muss zumindest **Zuschuss** geben.\n\n"
                    "### 3. Gehörschutz\n\n"
                    "**Bereitstellung Pflicht** ab Tages-Lärmexposition von "
                    "80 dB(A), **Tragepflicht** ab 85 dB(A) (LärmVibrationsArbSchV "
                    "§ 8). Auswahl:\n\n"
                    "- **Einweg-Stöpsel** (rolled foam) — billig, einmalige "
                    "Nutzung, Dämmung 22-32 dB\n"
                    "- **Mehrweg-Stöpsel** mit Bügel — schnelles An/Ab in/aus "
                    "Lärmzonen, Dämmung 15-25 dB\n"
                    "- **Kapselgehörschutz** — robuste Dämmung 25-35 dB, oft "
                    "mit aktivem Filter (lässt Sprache durch, dämpft Spitzen)\n"
                    "- **Otoplastiken** — individuell angefertigt, hoher Tragekomfort\n\n"
                    "### 4. Atemschutz\n\n"
                    "Eigenes Detail-Modul (siehe Modul 3) — kurze Übersicht: "
                    "**partikelfiltrierende** Halbmasken FFP1/2/3, **gasfiltrierende** "
                    "Vollmasken mit Wechselfiltern, **umluftunabhängige** Geräte "
                    "(Druckluftatmer) für Sauerstoff-Mangel-Atmosphären.\n\n"
                    "### 5. Handschutz\n\n"
                    "Material muss zum Risiko passen — falscher Handschuh kann "
                    "**gefährlicher** sein als gar keiner (z. B. wickelt sich in "
                    "rotierende Maschinenteile, durchlässig für Chemikalie):\n\n"
                    "- **Schnittschutz** (EN 388, Stufen A-F): Glas, Blech\n"
                    "- **Hitzeschutz** (EN 407): Schweißen, Ofenarbeit\n"
                    "- **Chemikalienschutz** (EN 374): jedes Material hat "
                    "Durchbruchzeit für jede Chemikalie — siehe Tabellen im SDB\n"
                    "- **Elektroisolation** (EN 60903): Arbeiten unter Spannung\n"
                    "- **Wichtig**: bei rotierenden Maschinen (Bohrer, Drehbank) "
                    "Handschuhe oft **verboten** — Einzugsgefahr!\n\n"
                    "### 6. Fußschutz\n\n"
                    "Klassifizierung nach EN ISO 20345:\n"
                    "- **S1**: Antistatik + Stahlkappe (200 J Aufprall) — Lager, "
                    "Werkstatt allgemein\n"
                    "- **S2**: S1 + Wasserabweisung — Außenarbeit, feuchte Bereiche\n"
                    "- **S3**: S2 + Durchtritts-Sicherung (Stahl-Zwischensohle) "
                    "+ Profilsohle — Bau, Recycling\n"
                    "- **ESD**: zusätzliche elektrostatische Ableitung — Elektronik\n\n"
                    "### 7. Körperschutz\n\n"
                    "- **Warnschutzkleidung** (EN ISO 20471) Klassen 1-3 — je "
                    "höher, desto sichtbarer; ab 60 km/h Verkehr Klasse 3 Pflicht\n"
                    "- **Hitzeschutz-Kleidung** für Hochofen, Gießerei\n"
                    "- **Chemikalien-Schutzanzug** Typ 1-6 je nach Permeations"
                    "anforderung\n"
                    "- **Schweißerschürze + Stulpen** aus Leder oder hitzefester "
                    "Aramid-Faser\n\n"
                    "### 8. Absturzsicherung\n\n"
                    "**Auffanggurt** (EN 361) + Verbindungsmittel mit Falldämpfer "
                    "(EN 355) ab 2 m Absturzhöhe Pflicht (DGUV 312-906). Wichtig: "
                    "Ankerpunkt MUSS 7-10 kN halten — Geländer reichen oft nicht.\n\n"
                    "## Tragepflicht — und warum 'nur kurz' nicht zählt\n\n"
                    "Wo PSA-Pflicht ausgeschildert ist (gelbe Warntafeln mit "
                    "blauem Piktogramm nach **DIN EN ISO 7010**), MUSS PSA "
                    "getragen werden. **Auch für 'nur 5 Sekunden' beim Durchgehen.**\n\n"
                    "Statistik der DGUV: über 60 % der Augenverletzungen passieren "
                    "bei 'nur kurz' nachgesehen — z. B. Kollege ohne Schweißerbrille, "
                    "der kurz reinblickt was die Schweißerin gerade macht. Folge: "
                    "Verblitzung der Hornhaut, 2 Tage starke Schmerzen.\n\n"
                    "**Wer wiederholt PSA-Pflicht ignoriert**, kann nach Abmahnung "
                    "gekündigt werden — und haftet bei Selbstverletzung gegenüber "
                    "der BG, die Leistungen kürzen darf (§ 110 SGB VII)."
                ),
            ),
            ModulDef(
                titel="Prüfung & Wartung",
                inhalt_md=(
                    "## Warum PSA-Prüfung Lebensretter ist\n\n"
                    "PSA ist die letzte Schutzlinie, oft beim akuten Schadens"
                    "ereignis. Wenn sie versagt — weil porös, gerissen, "
                    "verschlissen — gibt es nichts dahinter. Im Schweißerhandschuh "
                    "mit Loch verbrennt die Hand wie ohne Handschuh. Der Auffanggurt "
                    "mit beschädigtem Gewebeband reißt beim Fall in 80 % der Fälle. "
                    "**Vertrauen in PSA ist erlaubt — aber nur in geprüfte PSA.**\n\n"
                    "## Prüfung vor jeder Nutzung\n\n"
                    "Sichtprüfung dauert 5 Sekunden, hilft bei 90 % der "
                    "Versagensfälle:\n\n"
                    "- **Helm**: Sichtbare Risse in der Schale? UV-Bleichung? "
                    "Tropfenbildung an Innen-Polyethylen? Innenausstattung "
                    "beschädigt? → austauschen\n"
                    "- **Schutzbrille**: Kratzer im Sichtfeld? Lose Bügel? "
                    "Anti-Beschlag-Beschichtung abgenutzt? Risse in der "
                    "Rahmenfassung? → tauschen\n"
                    "- **Handschuh**: Loch (auch nadelfein!)? Versteifung durch "
                    "Chemiekontakt? Verfärbung (Indikator für Permeation)? "
                    "Fingerspitzen abgerieben? → tauschen\n"
                    "- **Sicherheitsschuh**: Sohle abgelaufen (Profiltiefe "
                    "<1.6 mm)? Risse im Schaft? Stahlkappe verformt nach "
                    "Aufprall? → tauschen\n"
                    "- **Gehörschutz-Kapsel**: Dichtkissen porös oder hart? "
                    "Bügel locker? → tauschen\n"
                    "- **Atemmaske**: Ausatemventil klebt? Filter abgelaufen "
                    "(Datum prüfen!)? Bänder elastisch? Dichtkante intakt?\n\n"
                    "## Wiederkehrende Prüfung durch Sachkundige\n\n"
                    "Manche PSA muss zusätzlich periodisch von qualifizierten "
                    "Personen geprüft werden — geht über bloße Sichtprüfung "
                    "hinaus:\n\n"
                    "| PSA | Intervall | Wer prüft |\n"
                    "|---|---|---|\n"
                    "| Schutzhelm | alle 4-5 Jahre tauschen (Herstellerdatum) | — |\n"
                    "| Auffanggurt + Verbindungsmittel | **jährlich** | Sachkundige (z. B. DGUV-312-906) |\n"
                    "| Atemschutz Vollmaske / Pressluft | **jährlich + nach jedem Einsatz** | Geräteträger:in + Sachkundige |\n"
                    "| Schweißerschutz | nach Bedarf | Sicherheitsfachkraft |\n"
                    "| Industrie-Schutzhandschuhe Klasse 3 | **alle 6 Monate** | Spezialfirma |\n"
                    "| Sicherheits-/Rettungswesten | **jährlich** | Hersteller-Service |\n\n"
                    "**Dokumentation Pflicht:** Jede Prüfung wird mit Datum, "
                    "Prüfername und Ergebnis in einem Prüfbuch festgehalten. "
                    "Keine Eintragung = keine gültige Prüfung = keine Verwendung.\n\n"
                    "## Lagerung und Hygiene\n\n"
                    "### Lagerung\n\n"
                    "- **Trocken, kühl, dunkel** — UV verändert Kunststoff-Eigen"
                    "schaften (Helm wird brüchig, Brillenglas vergilbt)\n"
                    "- **Atemmaske** in Vorratstasche oder verschließbarem Schrank, "
                    "nicht offen in der Werkstatt\n"
                    "- **Auffanggurt** hängend lagern (nicht knicken, nicht auf "
                    "ölverschmiertem Boden)\n"
                    "- **Sicherheitsschuhe** trocknen lassen vor dem nächsten "
                    "Tragen (Schweiß zerstört das Innenleder)\n\n"
                    "### Hygiene — PSA ist persönlich!\n\n"
                    "Geteilte PSA überträgt Hautpilze, Bakterien, Viren. Daher:\n\n"
                    "- **Eigene** Atemmaske, eigene Schutzbrille, eigener Helm "
                    "(mit Initialen markiert)\n"
                    "- **Geliehene** Maschinenführerhandschuhe (z. B. Gast"
                    "fahrer:innen): nach Gebrauch desinfizieren\n"
                    "- **Mehrweg-Atemmaske**: nach Gebrauch mit lauwarmem Wasser + "
                    "milder Seife reinigen, mit Desinfektionsmittel abwischen "
                    "(Hersteller-Empfehlung beachten), gut trocknen\n"
                    "- **Brillen-Reinigung** mit speziellem Tuch, nicht mit "
                    "Papier (Mikrokratzer!)\n"
                    "- **Helm-Schweißband** alle 6 Monate austauschen\n\n"
                    "## Wenn PSA versagt\n\n"
                    "1. **Sofort melden** — auch wenn keine Verletzung passierte\n"
                    "2. **PSA aussondern** (kein Weitergebrauch trotz 'sieht "
                    "wieder gut aus')\n"
                    "3. **Hersteller informieren** bei systemischem Versagen "
                    "(könnte Charge sein → andere Träger:innen warnen)\n"
                    "4. **Eintrag im Verbandbuch**, wenn nahe Verletzung"
                ),
            ),
            ModulDef(
                titel="Atemschutz im Detail",
                inhalt_md=(
                    "## Warum Atemschutz besonders heikel ist\n\n"
                    "Die Lunge nimmt Stoffe direkt in den Blutkreislauf auf. "
                    "Bereits **wenige Atemzüge** in einer kontaminierten Atmosphäre "
                    "können kritisch sein. Falscher Atemschutz oder Sauerstoff-"
                    "Mangel-Atmosphäre kann zum Erstickungstod führen — und das "
                    "innerhalb von 2-3 Minuten ohne Vorwarnung.\n\n"
                    "Vor jedem Einsatz von Atemschutz: **Sauerstoffgehalt prüfen** "
                    "(O2-Sensor) und die richtige Geräteklasse wählen. **Im "
                    "Zweifel** zur sichereren Variante greifen.\n\n"
                    "## Filtergeräte vs. umluftunabhängige Geräte\n\n"
                    "Zwei grundsätzlich verschiedene Konzepte:\n\n"
                    "### Filtergeräte (filtrierende Atemschutzgeräte)\n\n"
                    "Reinigen die Umgebungsluft, bevor sie eingeatmet wird. "
                    "Nutzbar **nur bei mindestens 17 % Restsauerstoff** in der "
                    "Atemluft (Normal: 20.9 %).\n\n"
                    "- Halbmasken FFP1/2/3 (Partikelfilter)\n"
                    "- Vollmasken mit Wechselfiltern (Partikel + Gas)\n"
                    "- Druckgebläseunterstützte Hauben\n\n"
                    "### Umluftunabhängige Atemschutzgeräte\n\n"
                    "Bringen eigene Luft mit, unabhängig von der Umgebung. **Pflicht** "
                    "bei:\n\n"
                    "- Sauerstoffgehalt < 17 %\n"
                    "- Unbekannter / wechselnder Schadstoff-Konzentration\n"
                    "- Schadstoffen ohne wirksamen Filter (CO, Methan)\n"
                    "- Engen Räumen (Tank, Silo, Kanal)\n\n"
                    "Typen:\n"
                    "- **Druckluft-Schlauchgerät** (Atemluft kommt vom Kompressor "
                    "via Schlauch — geringes Gewicht, aber an Schlauch gefesselt)\n"
                    "- **Pressluftatmer** (Stahlflasche auf dem Rücken, ca. 30 min "
                    "Vorrat bei normalem Arbeitsverbrauch)\n"
                    "- **Regenerationsgerät** (Atemluft wird chemisch gereinigt + "
                    "wiederverwendet, sehr lang einsetzbar — für Bergrettung)\n\n"
                    "## Partikelfilter — FFP-Klassen\n\n"
                    "FFP = *Filtering Face Piece*. Filterleistung gegen flüssige "
                    "+ feste Partikel:\n\n"
                    "| Klasse | Filterleistung | Geeignet gegen |\n"
                    "|---|---|---|\n"
                    "| FFP1 | 80 % | Inerte Stäube (Mehl, Kalk, Holzstaub <12% Bindemittel) |\n"
                    "| FFP2 | 94 % | Gesundheitsschädliche Stäube (Metallschleifstaub, Quarzfeinstaub, Bakterien) |\n"
                    "| FFP3 | 99 % | Krebserzeugend (Asbest, Holzhartstaub, Chrom-Schweißrauch), Viren |\n\n"
                    "**WICHTIG**: FFP-Masken schützen nur, wenn sie **dicht am "
                    "Gesicht** sitzen. Bart, lange Koteletten oder unsachgemäßes "
                    "Anlegen reduzieren die Filterleistung auf nahe Null.\n"
                    "**Dichtsitzprüfung** vor jedem Einsatz: Hand vor das Ausatemventil, "
                    "kräftig ausatmen — keine Luft am Rand spürbar? Dann sitzt sie.\n\n"
                    "## Gasfilter — die Farb-Codes\n\n"
                    "Vollmasken mit Wechselfiltern. Farb-Codierung internat. "
                    "standardisiert:\n\n"
                    "| Farbe | Typ | Schutz gegen |\n"
                    "|---|---|---|\n"
                    "| **Braun (A)** | Organische Dämpfe | Lösungsmittel, Lacke, Kraftstoffe |\n"
                    "| **Grau (B)** | Anorganische Gase | Chlor, H2S, Brom, HCN |\n"
                    "| **Gelb (E)** | Saure Gase | SO2, HCl |\n"
                    "| **Grün (K)** | Ammoniak | NH3 |\n"
                    "| **Schwarz (CO)** | Kohlenstoffmonoxid | (sehr begrenzte Schutzdauer) |\n"
                    "| **Blau (NO)** | Nitrose Gase | Schweißrauche-Anteile |\n"
                    "| **Rot (Hg-P3)** | Quecksilberdampf | Labor, ZSB-Recycling |\n"
                    "| **Weiß (P)** | Partikel | (zusätzlich kombinierbar) |\n\n"
                    "Schutzklassen 1-3 zeigen die Aufnahmekapazität an (1 = "
                    "klein/Halbmaske, 2/3 = Vollmaske).\n\n"
                    "**Kombi-Filter** (z. B. A2B2E2K1-P3) gegen mehrere Stoffgruppen "
                    "gleichzeitig — universell, aber teurer.\n\n"
                    "## Filter-Standzeit und Wechsel-Indikator\n\n"
                    "Filter haben eine begrenzte Aufnahmekapazität. Wechseln bei:\n"
                    "- **Geruchsschwellen-Wahrnehmung** durch die Maske "
                    "(Filter erschöpft)\n"
                    "- **Atemwiderstand spürbar erhöht** (Partikelfilter zugesetzt)\n"
                    "- **Herstellerangabe** zur Maximal-Tragezeit überschritten "
                    "(meist 8-40 h reine Tragezeit)\n"
                    "- **Verfallsdatum** auf dem Filter erreicht\n"
                    "- **Verdacht** auf Kontamination (Stoß, Spritzer auf Filter)\n\n"
                    "Filter sind **nicht regenerierbar** durch Auswaschen — bei "
                    "Zweifel: tauschen.\n\n"
                    "## In engen Räumen — Tank, Silo, Kanal\n\n"
                    "Hier ist Atemschutz **immer** umluftunabhängig zu wählen, "
                    "weil:\n\n"
                    "- Sauerstoffmangel durch Korrosion, Gärung, Schweißarbeit\n"
                    "- Anreicherung schwerer Gase am Boden (CO2, H2S)\n"
                    "- Kein zweiter Fluchtweg meist\n\n"
                    "**Vorgehen:**\n"
                    "1. **Freimessung** mit Multi-Gas-Messgerät (O2, EX, CO, H2S)\n"
                    "2. **Belüftung** anlegen, wenn Gase vorhanden\n"
                    "3. **Sicherungsposten** außerhalb mit Sichtkontakt + Funk\n"
                    "4. **Rückzug-Geschirr** + Bergesystem vorbereiten\n"
                    "5. **Erlaubnisschein** vom Sicherheitsbeauftragten\n\n"
                    "Verstöße kosten regelmäßig Menschenleben — DGUV statistisch "
                    "8-12 Tote pro Jahr in Deutschland durch Erstickung in "
                    "Behältern."
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
                    "## Warum jede Maschine Schutzeinrichtungen braucht\n\n"
                    "Die **Betriebssicherheitsverordnung (BetrSichV)** verlangt, "
                    "dass Maschinen sicher betrieben werden — und zwar nicht "
                    "nur 'sicher genug für den Idealfall', sondern auch bei "
                    "Unachtsamkeit, Eile, Müdigkeit und Wartung. Schutz"
                    "einrichtungen sind die **technische Antwort** auf das "
                    "Restrisiko, das nach Konstruktion und Aufstellung übrig "
                    "bleibt.\n\n"
                    "Statistik der DGUV: über **30 % der schweren Arbeits"
                    "unfälle** in Industrie und Handwerk passieren an Maschinen "
                    "ohne / mit manipulierten Schutzeinrichtungen. Die häufigste "
                    "Folge: Amputation oder Quetschung an Händen/Armen.\n\n"
                    "## Trennende Schutzeinrichtungen\n\n"
                    "**Feste Verkleidung** schließt den Gefahrenbereich physisch "
                    "ab. Sie kann nur mit Werkzeug entfernt werden — z. B. die "
                    "Verkleidung um eine Zahnriemen-Welle, die mit Schrauben "
                    "befestigt ist.\n\n"
                    "**Bewegliche Schutztür mit Verriegelung** öffnet zur "
                    "Einrichtung/Wartung. Solange sie offen ist, läuft die "
                    "Maschine nicht — Verriegelung ist Sicherheits-Bauteil "
                    "(Performance Level je nach Risiko, EN ISO 13849).\n\n"
                    "**Schutzzäune** im Bereich von Robotern, Pressen, großen "
                    "Maschinen. Eintritt über Pendelklappe oder per Schlüssel"
                    "transfer-System.\n\n"
                    "## Nichttrennende Schutzeinrichtungen\n\n"
                    "Wo eine physische Trennung nicht praktikabel ist, kommen "
                    "**Sensoren** zum Einsatz, die einen Gefahrenbereich überwachen "
                    "und bei Eindringen die gefährliche Bewegung stoppen:\n\n"
                    "- **Lichtgitter / Lichtvorhänge**: senkrechtes Feld aus "
                    "Lichtstrahlen vor der Maschine; Unterbrechung → Stopp\n"
                    "- **Sicherheits-Laserscanner**: 2D-Flächenüberwachung um "
                    "die Maschine herum, oft mit Vorwarn- + Stopzone\n"
                    "- **Trittmatte**: Drucksensor-Matte vor der Maschine\n"
                    "- **Zweihandschaltung**: beide Hände müssen gleichzeitig "
                    "Buttons drücken — verhindert, dass eine Hand im Gefahren"
                    "bereich ist während die andere startet\n"
                    "- **Sicherheits-Schalter** an Hauben/Türen (Reihenschalter)\n\n"
                    "## NIEMALS — die roten Linien\n\n"
                    "**1. Schutzeinrichtungen überbrücken oder manipulieren**\n\n"
                    "Klassiker: Schutztür mit Klebeband fixieren, damit die "
                    "Maschine schneller läuft. Lichtgitter mit Pappkarton "
                    "abdecken. Zweihandschaltung mit zwei Schrauben fest"
                    "klemmen, damit eine Hand frei bleibt. **Alles strafbar.**\n\n"
                    "**2. Festgeklemmte oder dauerhaft offene Schutzeinrichtungen**\n\n"
                    "Wer eine Sicherheits-Tür mit Holzkeil offen hält, weil "
                    "sie immer wieder zufällt und stört, riskiert seinen + "
                    "anderen Leben — und verstößt gegen § 23 BetrSichV.\n\n"
                    "**3. Weiterbetrieb mit defekter Schutzeinrichtung**\n\n"
                    "Sicherheits-Lichtgitter fällt aus → Maschine **muss "
                    "stillgesetzt** werden, bis repariert. Behebung ist "
                    "Aufgabe der Instandhaltung, NICHT der Produktion. Wer "
                    "trotzdem produziert, haftet bei Unfall persönlich.\n\n"
                    "## Konsequenzen bei Verstoß\n\n"
                    "§ 23 BetrSichV: **Bußgeld bis 30.000 €** für Beschäftigte, "
                    "die Schutzeinrichtungen manipulieren. In **schweren Fällen** "
                    "(Verletzung von Personen, vorsätzliches Handeln) Frei"
                    "heitsstrafe bis zu **5 Jahren** (§ 26 BetrSichV i.V.m. "
                    "§§ 222, 229 StGB — fahrlässige Tötung oder Körper"
                    "verletzung).\n\n"
                    "Praxisfall (rechtskräftig 2020): Schichtleiter eines Press"
                    "werks hatte die Sicherheits-Tür einer 250-Tonnen-Presse "
                    "permanent blockiert, um Ausschuss-Zeiten zu reduzieren. "
                    "Eine Mitarbeiterin verlor beim Eingriff in den Pressbereich "
                    "drei Finger. Schichtleiter: 9 Monate auf Bewährung + "
                    "15.000 € Geldstrafe. Arbeitgeber: 250.000 € BG-Regress.\n\n"
                    "## Was DU tun musst\n\n"
                    "- **Jede Schutzeinrichtung vor Schichtbeginn** auf "
                    "Funktion prüfen (Lichtgitter mit Hand testen, Schutztür "
                    "öffnen → Maschine stoppt?)\n"
                    "- **Defekte sofort melden** + Maschine stillsetzen\n"
                    "- **Niemals 'Workarounds'** ausprobieren, auch wenn die "
                    "Schicht-Quote droht\n"
                    "- **Manipulationsverdacht** bei Kollegen → der/dem "
                    "Sicherheitsbeauftragten melden. Stille Mitwisserschaft "
                    "ist auch eine Form der Verantwortung."
                ),
            ),
            ModulDef(
                titel="Lockout-Tagout (LOTO)",
                inhalt_md=(
                    "## Was ist Lockout-Tagout?\n\n"
                    "**Lockout-Tagout (LOTO)** ist das standardisierte Verfahren, "
                    "eine Maschine oder Anlage **garantiert energiefrei** zu "
                    "machen, bevor an ihr gearbeitet wird — Wartung, Reinigung, "
                    "Störungsbeseitigung, Werkzeug-Wechsel. Es wurde in den USA "
                    "(OSHA Standard 1910.147) entwickelt und ist heute auch in "
                    "Deutschland Industrie-Standard (DGUV-Information 209-093).\n\n"
                    "Der Begriff:\n"
                    "- **Lock-out** = abschließen (Vorhängeschloss am Hauptschalter)\n"
                    "- **Tag-out** = beschildern (Schild 'Nicht einschalten — wird gewartet')\n\n"
                    "## Warum LOTO Leben rettet\n\n"
                    "Die häufigste Todesursache in der Instandhaltung ist das "
                    "**unbeabsichtigte Wiedereinschalten** während der Arbeit. "
                    "Statistik: in Deutschland sterben jährlich ca. 15-25 Instand"
                    "haltende durch versehentliches Anlaufen einer Maschine, "
                    "an der sie gerade arbeiten. Die meisten Fälle: jemand "
                    "anderes drückt den Startknopf, weil er die Wartung nicht "
                    "wahrgenommen hat.\n\n"
                    "LOTO ist die einzige Methode, die das **systematisch "
                    "ausschließt**.\n\n"
                    "## Die sechs Schritte von LOTO\n\n"
                    "### 1. Vorbereitung — alle Energiequellen ermitteln\n\n"
                    "Maschinen haben oft **mehr Energiequellen als gedacht**:\n\n"
                    "- Elektrische Energie (Hauptanschluss, Hilfsspannungen, "
                    "Batterie, Kondensator-Reststrom)\n"
                    "- Pneumatik (Druckluft im System, auch nach Abschalten)\n"
                    "- Hydraulik (Restdruck in Akkumulatoren)\n"
                    "- Mechanisch (Federn unter Spannung, Schwungrad, hoch"
                    "gefahrenes Werkzeug, Schwerkraft)\n"
                    "- Thermisch (heißes Öl, Dampf, glühende Werkstücke)\n"
                    "- Chemisch (Restgas im Tank, Lauge in der Leitung)\n\n"
                    "**Quelle für die Übersicht:** Maschinen-Dokumentation, "
                    "EPA-Plan (Energy Plan & Analysis), Erfahrungen früherer "
                    "Wartungen.\n\n"
                    "### 2. Abschalten\n\n"
                    "Maschine über die **normalen Bedienelemente** stilllegen "
                    "(Stop-Taster, geordnetes Herunterfahren). Nicht direkt "
                    "Notaus — das verlässt die Maschine in undefiniertem Zustand.\n\n"
                    "### 3. Trennen aller Energiequellen\n\n"
                    "- **Hauptschalter aus** (mechanisch in Aus-Position bringen)\n"
                    "- **Druckluft-Hauptventil schließen + Leitung entlüften**\n"
                    "- **Hydraulik-Druck ablassen** an dafür vorgesehenen Ventilen\n"
                    "- **Hochgefahrenes Werkzeug** mechanisch abstützen oder "
                    "absenken\n"
                    "- **Federn entspannen** wo möglich, sonst markieren + "
                    "Notiz\n"
                    "- **Kondensatoren entladen** (Zeitintervall laut Herstel"
                    "ler, oft 5+ min Wartezeit)\n\n"
                    "### 4. Verschließen (Lockout)\n\n"
                    "**Persönliches Vorhängeschloss** am Hauptschalter "
                    "anbringen. Jede:r Mitarbeitende hat **eigenes Schloss + "
                    "eigenen Schlüssel** — niemand sonst kann den Schalter "
                    "öffnen.\n\n"
                    "Bei Schaltern, an denen mehrere Schlösser nicht passen: "
                    "**Multi-Lock-Hasp** (Stahlbügel mit mehreren Schloss"
                    "ösen, bis 6 Personen).\n\n"
                    "### 5. Kennzeichnen (Tagout)\n\n"
                    "Schild am Schalter mit:\n"
                    "- **Name** der ausführenden Person\n"
                    "- **Datum + Uhrzeit** des Verschlusses\n"
                    "- **Grund** (z. B. 'Wartung Förderband 03')\n"
                    "- **Telefonnummer** für Rückfragen\n\n"
                    "### 6. Wirkungsprüfung — der Probelauf-Versuch\n\n"
                    "**Wichtigster Schritt.** Vor Beginn der Arbeit testen:\n\n"
                    "1. Start-Taster drücken → Maschine darf NICHT anlaufen\n"
                    "2. Spannung am Maschinenanschluss messen → muss 0 V sein\n"
                    "3. Pneumatik-Manometer prüfen → muss 0 bar zeigen\n\n"
                    "Erst wenn diese **konkrete physische Bestätigung** vorliegt, "
                    "darf die Arbeit beginnen. 'Müsste eigentlich aus sein' "
                    "ist kein Beweis.\n\n"
                    "## Mehrere Wartende — jede:r ihr/sein Schloss\n\n"
                    "Wenn mehrere Personen an derselben Maschine arbeiten: "
                    "**jede:r bringt sein eigenes Schloss** an der Multi-Hasp "
                    "an. Erst wenn der **letzte** das Schloss entfernt, kann "
                    "die Maschine wieder anlaufen.\n\n"
                    "**Beispiel:** Elektriker, Schlosser, Programmiererin "
                    "arbeiten parallel an einer CNC. Elektriker ist fertig, "
                    "geht raus → entfernt sein Schloss. Aber Schlosser und "
                    "Programmiererin haben ihre noch dran → Maschine bleibt "
                    "stillgesetzt. **Diese Trennung verhindert Tote.**\n\n"
                    "## Schlüssel-Diszipline\n\n"
                    "- **Nie zwei Schlüssel** zum gleichen Schloss — Risiko, "
                    "dass jemand das Schloss vergisst aber Kollege schlüssel"
                    "berechtigt ist\n"
                    "- **Kein Hauptschlüssel beim Schichtleiter** für 'Notfall'\n"
                    "- **Bei Verlust des Schlüssels**: Schloss zerstören "
                    "(Bolzenschneider), schriftliches Protokoll mit der/dem "
                    "Sicherheitsbeauftragten\n"
                    "- **Schlüssel im persönlichen Spind** zwischen Schichten — "
                    "nicht offen in der Werkstatt liegen lassen"
                ),
            ),
            ModulDef(
                titel="Wartung & Störungsbeseitigung sicher",
                inhalt_md=(
                    "## Die fünf Phasen einer sicheren Wartung\n\n"
                    "### 1. Planung — vor dem ersten Werkzeug\n\n"
                    "- **Wartungsplan** des Herstellers einsehen — Schritt-für-"
                    "Schritt-Anweisung\n"
                    "- **EPA-Plan** (Energy Plan & Analysis) zur Maschine — "
                    "welche Energiequellen müssen abgeschaltet werden?\n"
                    "- **Ersatzteile + Werkzeuge** bereitlegen, damit keine "
                    "Pause während der Wartung mit teilweise zerlegter Maschine "
                    "entsteht\n"
                    "- **PSA-Auswahl** je Tätigkeit (Helm? Schweißerschutz? "
                    "Säurefeste Handschuhe?)\n"
                    "- **Erlaubnisschein** für Sonderarbeiten (Heißarbeiten, "
                    "enge Räume, Arbeit unter Spannung)\n\n"
                    "### 2. Stilllegen — LOTO durchführen\n\n"
                    "Siehe Modul 2 (LOTO). Niemals abkürzen.\n\n"
                    "### 3. Restenergien beachten\n\n"
                    "Auch nach LOTO sind **gespeicherte Energien** noch da:\n\n"
                    "**Federkraft** — Pneumatik-Aktoren mit Notrückstellfeder, "
                    "Spannfedern in Stanzen, Schließfedern an Ventilen. Beim "
                    "Lösen mechanisch sichern (Bolzen, Kette).\n\n"
                    "**Schwerkraft** — hochgefahrene Pressentische, Hochreg"
                    "alzangen, hängende Werkzeuge. **Mechanisch abstützen** "
                    "(Stützbock, Spanngurt) oder vorher kontrolliert absenken. "
                    "Hydrauliköl kühlt ab → Stempel sinkt langsam → Verletzungs"
                    "gefahr Stunden später.\n\n"
                    "**Restdruck** in pneumatischen Leitungen — auch nach "
                    "Absperrung. Vor dem Lösen einer Verschraubung: am dafür "
                    "vorgesehenen **Entlüftungsventil** Druck ablassen, Manometer "
                    "auf 0 prüfen.\n\n"
                    "**Restladung** in Kondensatoren — z. B. Frequenzumrichter "
                    "haben Zwischenkreis-Kondensatoren, die nach Abschaltung "
                    "noch **5-10 Minuten** lebensgefährlich geladen sind. "
                    "Herstellerangaben einhalten, mit Multimeter messen.\n\n"
                    "**Thermische Energie** — heiße Maschinenteile, Öl, "
                    "Werkstücke. Abkühlzeit beachten oder Hitzeschutz-PSA.\n\n"
                    "### 4. Wartung durchführen\n\n"
                    "- **Saubere Arbeitsweise** — Verschraubungen mit Drehmoment-"
                    "Schlüssel anziehen, nicht 'so fest wie möglich'\n"
                    "- **Kein Verbiegen** von Sicherheitseinrichtungen, kein "
                    "'Anpassen' von Lichtgittern\n"
                    "- **Werkzeuge zählen** — kein vergessener Schraubenschlüssel "
                    "im Antrieb (häufige Crash-Ursache)\n"
                    "- **Dokumentation** durchgeführter Arbeiten im Wartungs"
                    "protokoll\n\n"
                    "### 5. Wiederinbetriebnahme\n\n"
                    "Reihenfolge **nie umkehren**:\n\n"
                    "1. **Werkzeuge entfernen** und kontrollieren (vollzählig?)\n"
                    "2. **Schutzeinrichtungen wieder anbringen** — alle Schrauben, "
                    "alle Hauben, alle Verkleidungen\n"
                    "3. **Funktionsprüfung der Schutzeinrichtungen** — Lichtgitter, "
                    "Türsensoren, Notaus drücken: lösen sie aus?\n"
                    "4. **LOTO aufheben** — jede Person nimmt ihr eigenes "
                    "Schloss ab. Die letzte Person bestätigt: Maschine frei?\n"
                    "5. **Probelauf in gesichertem Bereich** — Niemand im "
                    "Gefahrenbereich, langsam hochfahren, beobachten\n"
                    "6. **Übergabe an Produktion** mit Hinweis 'gewartet, "
                    "freigegeben' im Schichtbuch\n\n"
                    "## Sondersituation: Eingriff bei laufender Maschine\n\n"
                    "Manche Tätigkeiten erfordern Beobachtung der **laufenden** "
                    "Maschine (Justierung, Fehlersuche im Betrieb). Dafür gibt "
                    "es spezielle **Sondermodi**:\n\n"
                    "- **Tipp-Betrieb** mit reduzierter Geschwindigkeit + Zustimm"
                    "taster (3-Stufen-Taster: lose = Stopp, mittel = läuft, "
                    "stark gedrückt = Stopp → totmann-Funktion)\n"
                    "- **Service-Schlüsselschalter** muss aktiviert sein — "
                    "geht nur durch autorisierte Personen\n"
                    "- **Reduzierte Maximalgeschwindigkeit** im Service-Mode\n\n"
                    "**Niemals** mit dem normalen Bedien-Mode in den Gefahren"
                    "bereich greifen, auch nicht 'nur kurz'. Wer das tut, "
                    "verliert Hände — buchstäblich.\n\n"
                    "## Persönliche Sicherheit der Wartenden\n\n"
                    "- **Nie alleine** bei riskanten Wartungsarbeiten (Hoch"
                    "spannung, enge Räume, Höhe)\n"
                    "- **Funk- oder Sichtkontakt** zur Schichtleitung halten\n"
                    "- **Bei Unwohlsein** sofort raus aus dem Gefahrenbereich\n"
                    "- **Niemals Routine-Wartungen unter Zeitdruck** — wenn "
                    "die Schicht-Pause nicht reicht, lieber unterbrechen, "
                    "Maschine im sicheren Zustand belassen, später fortsetzen"
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
                    "## Warum Lärm so unterschätzt wird\n\n"
                    "**Lärmschwerhörigkeit ist die häufigste Berufskrankheit** "
                    "in Deutschland. Über 50.000 Fälle werden jährlich neu "
                    "angezeigt — und das sind nur die offiziell anerkannten. "
                    "Das Tückische: Lärmschäden sind **irreversibel** und "
                    "**schleichend**. Wer mit 30 jahrelang in 90 dB(A) arbeitet "
                    "ohne Schutz, merkt mit 50 plötzlich, dass er Gespräche "
                    "in lauten Umgebungen nicht mehr versteht. Da sind die "
                    "Haarzellen im Innenohr längst zerstört, dauerhaft.\n\n"
                    "Im Industrie-Mittelstand sind typische Lärmquellen:\n"
                    "- CNC-Fräsen (90-100 dB)\n"
                    "- Druckluft-Werkzeuge, Schlagschrauber (95-110 dB)\n"
                    "- Pressen, Stanzen (100-120 dB)\n"
                    "- Flex / Trennschleifer (100-115 dB)\n"
                    "- Hammerschläge auf Blech, Schmiede (120-140 dB Spitze)\n\n"
                    "## Auslösewerte nach LärmVibrationsArbSchV § 6\n\n"
                    "Die deutsche Lärm- und Vibrations-Arbeitsschutz-Verordnung "
                    "definiert **drei Schwellen** für Tages-Lärmexposition "
                    "(LEX,8h — auf 8 Stunden normiert) und Spitzenpegel:\n\n"
                    "| Wert | Konsequenz für Arbeitgeber + Beschäftigte |\n"
                    "|---|---|\n"
                    "| **80 dB(A)** (Unterer Auslösewert) | Bereitstellung Gehörschutz, Unterweisung jährlich, G20-Untersuchung **angeboten** |\n"
                    "| **85 dB(A)** (Oberer Auslösewert) | **Tragepflicht** Gehörschutz, Bereich als Lärmbereich kennzeichnen, G20 angeboten |\n"
                    "| **90 dB(A)** + Spitzenpegel **137 dB(C)** | Sofortmaßnahmen, technische Lärmminderung Pflicht (Kapselung, Aufstellung trennen) |\n"
                    "| **Grenzwert 87 dB(A)** unter Gehörschutz | Darf nie überschritten werden — Gehörschutz muss soweit dämpfen |\n\n"
                    "**Wichtig zur dB-Skala**: 3 dB mehr = doppelte Schall"
                    "energie (logarithmische Skala). 90 dB ist also nicht ein "
                    "bisschen mehr als 87 dB, sondern doppelt so viel Energie. "
                    "Auch die zulässige Expositionszeit halbiert sich pro +3 dB.\n\n"
                    "## Vibration — die unsichtbare Gefahr\n\n"
                    "Während Lärm man hört, ist Vibration oft beim Stand der "
                    "Technik kaum spürbar — aber die Langzeitschäden sind "
                    "schwerwiegend.\n\n"
                    "### Hand-Arm-Vibration\n\n"
                    "Durch Hand-geführte Werkzeuge (Bohrhammer, Schlag"
                    "schrauber, Schwingschleifer). Schwingungen >300 Hz "
                    "schädigen die feinen Blutgefäße in den Fingerkuppen.\n\n"
                    "- **Auslösewert**: 2,5 m/s² (auf 8 h normiert) — ab hier "
                    "Unterweisung + G46-Vorsorge anbieten\n"
                    "- **Grenzwert**: 5,0 m/s² — darf nicht überschritten werden, "
                    "sonst technische Maßnahmen oder Expositionszeit-Reduktion\n\n"
                    "### Ganzkörper-Vibration\n\n"
                    "Sitz-Schwingungen bei Stapler-, Bagger-, LKW-Fahrer:innen. "
                    "Niedrige Frequenzen (1-80 Hz) schädigen Bandscheiben.\n\n"
                    "- **Auslösewert**: 0,5 m/s²\n"
                    "- **Grenzwert**: 1,15 m/s²\n\n"
                    "## Gesundheitliche Folgen — was wirklich passiert\n\n"
                    "### Lärmschwerhörigkeit\n\n"
                    "Die Sinneshärchen (Haarzellen) im Innenohr werden zerstört. "
                    "Wenn sie weg sind, bleiben sie weg — keine Regeneration. "
                    "Erste Schäden im Hochtonbereich (4 kHz, das ist genau der "
                    "Frequenzbereich von Konsonanten in der Sprache). Daher "
                    "auch das Symptom: Vokale (tieffrequent) hört man noch, "
                    "Konsonanten nicht — Gespräche werden 'undeutlich'.\n\n"
                    "### Tinnitus\n\n"
                    "Dauerhaftes Klingeln, Pfeifen oder Rauschen im Ohr, "
                    "**ohne externe Schallquelle**. Tinnitus ist meist nicht "
                    "heilbar, kann massiv die Lebensqualität reduzieren "
                    "(Schlaflosigkeit, Konzentrationsstörung, in Extremfällen "
                    "Depression).\n\n"
                    "### Bluthochdruck und Stress\n\n"
                    "Lärm aktiviert das vegetative Nervensystem (Stressreaktion). "
                    "Langzeitwirkung: erhöhtes Herzinfarkt- und Schlaganfall-"
                    "Risiko, auch wenn das Gehör selbst noch intakt scheint.\n\n"
                    "### Weißfingerkrankheit (HAV-Syndrom)\n\n"
                    "Durch jahrelange Hand-Arm-Vibration: Durchblutungsstörung "
                    "der Finger. Kalte Hände → finger werden weiß, taub, "
                    "schmerzhaft. Bei fortgeschrittenem Stadium auch bei "
                    "moderater Kälte. Anerkannte Berufskrankheit BK 2104.\n\n"
                    "### Bandscheibenschäden\n\n"
                    "Durch Ganzkörper-Vibration in Verbindung mit Sitzhaltung. "
                    "Frühe Verschleißerscheinungen, Bandscheibenvorfall, chronische "
                    "Rückenschmerzen. BK 2110.\n\n"
                    "## Pflichten der Beschäftigten\n\n"
                    "- **Gehörschutz tragen** wo angeordnet — auch bei 'nur kurz' "
                    "in den Lärmbereich gehen\n"
                    "- **Vibrationswerte nicht überschreiten** durch Pausen oder "
                    "Werkzeugwechsel\n"
                    "- **G20-/G46-Untersuchung** annehmen, wenn angeboten "
                    "(kostenlos für dich, hilft bei Früherkennung)\n"
                    "- **Defekte Schutzeinrichtungen melden** (z. B. Kapselung "
                    "an Maschine löst sich)\n"
                    "- **Symptome melden** (Pfeifen im Ohr nach Schicht, "
                    "Taubheit in den Fingern) — möglicherweise Hinweis auf "
                    "beginnenden Schaden, der noch reversibel ist."
                ),
            ),
            ModulDef(
                titel="Gehörschutz in der Praxis",
                inhalt_md=(
                    "## Die richtige Auswahl — Dämmung passend zum Lärm\n\n"
                    "Es gibt nicht 'den' Gehörschutz — die Wahl hängt von "
                    "Lärmpegel, Frequenzspektrum, Trage-Komfort und Kommuni"
                    "kations-Anforderungen ab. Jeder Gehörschutz hat einen "
                    "**SNR-Wert** (Single Number Rating) — wie viele dB er "
                    "im Mittel dämpft. Auch H/M/L-Werte für hohe/mittlere/"
                    "tiefe Frequenzen sind auf der Verpackung.\n\n"
                    "### Stöpsel (Ohrstöpsel)\n\n"
                    "**Dämmung 22-35 dB** je nach Typ.\n\n"
                    "- **Einweg-Schaumstoff** (Roll-Stöpsel) — billig, hoher SNR "
                    "(bis 37 dB), aber Hygiene-Aspekt: nicht wiederverwendbar\n"
                    "- **Mehrweg-Lamellen** aus Silikon — waschbar, gut für "
                    "viele Schichten\n"
                    "- **Bügelstöpsel** (zwei Stöpsel an Plastikbügel) — sehr "
                    "schnell auf-/absetzen, gut für kurze Aufenthalte in "
                    "Lärmbereich\n\n"
                    "**Richtig anlegen** (entscheidet 90 % über Wirksamkeit):\n"
                    "1. Schaumstoff-Stöpsel zwischen Daumen + Zeigefinger zu "
                    "dünner Rolle drücken\n"
                    "2. **Ohr nach oben + hinten ziehen** mit der anderen Hand "
                    "(begradigt den Gehörgang)\n"
                    "3. Stöpsel **tief** einführen — er sollte nicht 'aufstehen'\n"
                    "4. Mit dem Finger **20-30 Sekunden festhalten**, bis "
                    "Schaumstoff sich entfaltet hat\n"
                    "5. Test: eigene Stimme klingt dumpfer + lauter (wegen "
                    "Schädelresonanz) — dann sitzt er richtig\n\n"
                    "### Kapsel-Gehörschutz\n\n"
                    "**Dämmung 25-37 dB**.\n\n"
                    "- Bügel über den Kopf oder am Helm befestigt\n"
                    "- Schnell auf-/absetzen — gut für Tätigkeiten mit "
                    "wechselnden Lärmphasen\n"
                    "- **Aktiv-Kapseln** lassen Sprache durch (verstärken "
                    "leise Sprache, dämpfen Spitzen) — gut für Teams\n"
                    "- **Mit Funk-Modul** für Kommunikation in Lärmzonen\n\n"
                    "**Probleme**:\n"
                    "- **Brille + Kapsel** → Brillen-Bügel unter Dichtkissen "
                    "= Schallleck = bis zu 10 dB weniger Wirkung\n"
                    "- **Schweißband, lange Haare, dichter Bart** unter Dicht"
                    "kissen = Wirkungsverlust\n"
                    "- **Hitze**: nach 30 min Kapseltragen schwitzt der Kopf — "
                    "Disziplin nötig\n\n"
                    "### Otoplastik (individuell angepasst)\n\n"
                    "**Dämmung 15-30 dB**, je nach Filter.\n\n"
                    "- Vom Audiologen aus Ohrabdruck gefertigt\n"
                    "- Höchster Trage-Komfort, perfekter Sitz\n"
                    "- Mit auswechselbarem Filter — Dämmung lässt sich pro "
                    "Tätigkeit anpassen\n"
                    "- **Teurer** (200-500 € pro Paar), aber Lebensdauer "
                    "5-10 Jahre\n"
                    "- Empfohlen bei dauerhafter Lärmexposition (z. B. CNC-"
                    "Bediener:in 8h/Tag)\n\n"
                    "## Das Paradox: zu viel Dämmung ist auch schlecht\n\n"
                    "Wenn der Restpegel am Ohr unter **65 dB(A)** fällt:\n"
                    "- Warnsignale (Hupe, Notruf, Stapler-Rückwarner) werden "
                    "überhört\n"
                    "- Kommunikation mit Kollegen unmöglich\n"
                    "- Isolations-Gefühl, Müdigkeit\n\n"
                    "**Optimum**: Restpegel 70-80 dB(A) am Ohr. Im Lärmschutz-"
                    "Bereichsfestlegung wird das berechnet (Lärmpegel minus "
                    "SNR plus Korrektur). Faustregel: bei 95 dB im Bereich "
                    "→ Gehörschutz mit SNR 20-25 dB wählen.\n\n"
                    "## Tragezeit-Disziplin\n\n"
                    "**Das wichtigste:** Konsequent tragen, auch kurze Aus"
                    "zeiten zerstören die Schutzwirkung. Eine Stunde Gehör"
                    "schutz tragen + 5 Minuten ohne in 95 dB(A) = effektiver "
                    "Schutz **nur noch wie ohne Gehörschutz**, weil die kurze "
                    "Spitzenbelastung in Schadensbereich liegt.\n\n"
                    "Berechnungsbeispiel für 8h:\n"
                    "- 7,5 h mit 25 dB Gehörschutz bei 95 dB → 70 dB am Ohr "
                    "→ Schaden-Bereich nicht erreicht\n"
                    "- 7,5 h mit + 0,5 h ohne → effektiver Mittelwert ca. "
                    "84 dB am Ohr → fast schon Schadenbereich\n\n"
                    "## Hygiene und Pflege\n\n"
                    "- **Stöpsel** vor Einsetzen: Hände waschen\n"
                    "- **Mehrweg-Stöpsel** nach jeder Schicht mit milder Seife "
                    "+ Wasser reinigen, trocknen lassen\n"
                    "- **Kapseln** Dichtkissen wöchentlich abwischen, alle "
                    "6 Monate Dichtkissen + Schwamm tauschen\n"
                    "- **Otoplastik** alle 4-6 Wochen mit speziellem Reiniger "
                    "+ Bürste\n\n"
                    "## Lärmpause als zusätzlicher Schutz\n\n"
                    "Über den Tag verteilt mindestens **30 Minuten** in einem "
                    "Raum unter 70 dB(A) verbringen — Pausenraum, Büro, "
                    "Sozialraum. Das Innenohr braucht Erholung."
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
                    "## Definition und gesetzliche Grundlagen\n\n"
                    "**Korruption** ist der **Missbrauch einer anvertrauten "
                    "Stellung** zum privaten Vorteil oder zum Vorteil eines "
                    "Dritten. Sie schädigt den Wettbewerb, untergräbt das "
                    "Vertrauen in Märkte und kann ein Unternehmen wirtschaftlich "
                    "ruinieren.\n\n"
                    "Die zentralen Strafnormen im deutschen Recht:\n\n"
                    "| Paragraph | Was wird bestraft | Strafmaß |\n"
                    "|---|---|---|\n"
                    "| **§ 299 StGB** | Bestechlichkeit/Bestechung im geschäftlichen Verkehr (Privatwirtschaft) | bis 3 J., in schweren Fällen 5 J. |\n"
                    "| **§ 300 StGB** | Schwerer Fall der Bestechung | 3 Mon. bis 5 J. |\n"
                    "| **§ 331-335 StGB** | Vorteilsannahme + Bestechung von Amtsträgern | 1 J. bis 10 J. |\n"
                    "| **§ 266 StGB** | Untreue (vermögensrechtlicher Pflichten-Verstoß) | bis 5 J., schwere Fälle 10 J. |\n"
                    "| **§ 30 OWiG** | Verbandsgeldbuße gegen das Unternehmen | bis 10 Mio. € |\n\n"
                    "Außerdem strafbar nach internationalen Normen: **OECD-"
                    "Antibestechungs-Übereinkommen**, **US-FCPA** (für "
                    "US-Geschäfte), **UK Bribery Act 2010** (für UK-Geschäfte). "
                    "Letztere gilt **extraterritorial** und kann auch deutsche "
                    "Firmen treffen.\n\n"
                    "## Zwei Seiten der Korruption\n\n"
                    "### Aktive Korruption (Bestechen)\n\n"
                    "Du **gibst** einer Person etwas, um sie zu einer bestimmten "
                    "Handlung zu bewegen. Beispiele:\n"
                    "- Du zahlst dem Einkäufer eines Kunden 'Provision', "
                    "damit er deinen Auftrag bevorzugt\n"
                    "- Du schenkst dem Bauamts-Sachbearbeiter ein iPhone, "
                    "damit die Baugenehmigung schneller läuft\n"
                    "- Du finanzierst dem Geschäftsführer einer Behörde "
                    "einen Wellness-Urlaub\n\n"
                    "### Passive Korruption (Bestechlichkeit)\n\n"
                    "Du **nimmst** etwas, um eine Handlung zu unterlassen oder "
                    "auszuführen, die deine Pflichten verletzt. Beispiele:\n"
                    "- Als Einkäufer bekommst du eine 'Provision' von einem "
                    "Lieferanten\n"
                    "- Als Schichtleiter wirst du von einem Subunternehmer "
                    "eingeladen, damit du seine Mitarbeiter bevorzugt einsetzt\n"
                    "- Als Vertriebsmitarbeiter bekommst du eine 'Bonus-"
                    "Reise', wenn der Kunde mehr abnimmt\n\n"
                    "**Beide Seiten** sind strafbar. Auch das **Anbieten** bzw. "
                    "**Fordern** einer Zuwendung ist bereits strafbar, "
                    "unabhängig vom Erfolg.\n\n"
                    "## Konkrete Beispiele aus dem Industrie-Mittelstand\n\n"
                    "**1. Schmiergeld bei Auftragsvergabe** — der Einkäufer "
                    "eines Großkunden bekommt vor dem Vertragsabschluss eine "
                    "anonyme Bargeld-Übergabe oder 'Sonder-Bonus'. Beispiel"
                    "haft realer Fall (Siemens 2008): 1,3 Mrd. € Bußgeld in "
                    "Deutschland + USA.\n\n"
                    "**2. Schein-Beratungsverträge** — 'Beratungshonorar' für "
                    "eine Person, die keine reale Leistung erbringt. Oft "
                    "Verwandter eines Entscheidungsträgers. Steuerlich "
                    "abgesetzt → zusätzlich Steuerhinterziehung.\n\n"
                    "**3. Lieferanten-Reisen** — Vertriebsleiter eines "
                    "Lieferanten lädt Einkäufer auf 'Werksbesichtigung' "
                    "Mallorca, dort hauptsächlich Strand. Wenn nicht "
                    "berufliche Notwendigkeit überwiegt → Vorteilsannahme.\n\n"
                    "**4. Facilitation Payments** ('Erleichterungs-Zahlungen') "
                    "— kleine 'Trinkgelder' an Beamte, damit eine ohnehin "
                    "rechtmäßige Handlung schneller läuft. In Deutschland + "
                    "Großbritannien IMMER strafbar, auch wenn in manchen "
                    "Ländern üblich.\n\n"
                    "**5. Schwarzgeld-Kasse** — illegale Finanzmittel "
                    "außerhalb der Buchhaltung, oft für 'Anbahnungskosten'. "
                    "Gleichzeitig Bilanzfälschung, Untreue, Steuerhinterziehung.\n\n"
                    "## Folgen für alle Beteiligten\n\n"
                    "### Für die handelnde Person\n"
                    "- **Freiheitsstrafe** bis 5 Jahre (Privatwirtschaft) "
                    "bzw. 10 Jahre (Amtsträger)\n"
                    "- **Eintrag im Bundeszentralregister** → Beruf weg, "
                    "kaum noch Einstellungschancen\n"
                    "- **Persönliche Haftung** für Schäden\n"
                    "- **Steuerliche Folgen** (Zuwendungen nicht absetzbar)\n\n"
                    "### Für das Unternehmen\n"
                    "- **Verbandsgeldbuße bis 10 Mio. €** (§ 30 OWiG) — oft "
                    "deutlich mehr, weil der erzielte Gewinn aus der Tat zusätzlich abgeschöpft wird\n"
                    "- **Ausschluss von öffentlichen Vergaben** (3-5 Jahre)\n"
                    "- **Reputationsschaden** — Kunden ziehen sich zurück\n"
                    "- **Erhöhte Compliance-Kosten** durch behördliche Aufsicht\n\n"
                    "### Volkswirtschaftlich\n"
                    "- Wettbewerb wird verzerrt — der Beste gewinnt nicht, "
                    "sondern der mit den besten Beziehungen\n"
                    "- Schäden für Verbraucher (höhere Preise, schlechtere "
                    "Qualität)\n"
                    "- Vertrauensverlust in Märkte und Institutionen\n\n"
                    "**Im Zweifel: keine Geschenke geben/nehmen.** Bei jedem "
                    "Restzweifel: Compliance-Beauftragte:n fragen, **vor** "
                    "der Handlung."
                ),
            ),
            ModulDef(
                titel="Zuwendungen — was ist erlaubt?",
                inhalt_md=(
                    "## Das Grundproblem: Wo ist die Grenze?\n\n"
                    "Geschäftsleben kommt selten ohne soziale Gesten aus — "
                    "eine Tasse Kaffee, ein gemeinsames Mittagessen, ein "
                    "Werbekugelschreiber. Niemand erwartet von dir, dass du "
                    "alle Sozialkontakte abbrichst. Aber zwischen 'üblicher "
                    "Höflichkeit' und 'unerlaubter Vorteilsnahme' liegt eine "
                    "Grauzone, die du kennen musst.\n\n"
                    "## Die vier Kriterien für erlaubte Zuwendungen\n\n"
                    "Eine Zuwendung ist in der **Privatwirtschaft** in der "
                    "Regel erlaubt, wenn ALLE vier Kriterien erfüllt sind:\n\n"
                    "### 1. Geringwertig\n\n"
                    "Praktischer Schwellenwert in den meisten Unternehmens-"
                    "Codes: **50 € pro Anlass und Person und Kalenderjahr**. "
                    "Manche Konzerne setzen die Grenze niedriger (25-35 €).\n\n"
                    "Bei wiederholten Zuwendungen vom selben Partner: **Summe "
                    "über das Jahr** zählt. Kollege A bekommt vom Lieferanten "
                    "X jeden Monat ein 5-€-Schokoladenpaket → 60 €/Jahr → "
                    "kritisch.\n\n"
                    "### 2. Anlassbezogen\n\n"
                    "Es muss einen **konkreten Anlass** geben:\n"
                    "- Weihnachten / Neujahr\n"
                    "- Firmenjubiläum / Geschäftsjubiläum\n"
                    "- Vertragsabschluss (NACH Vertragsunterzeichnung, nicht vor)\n"
                    "- Geburtstag, Hochzeit, Geburt (eher privat)\n"
                    "- Eröffnung eines neuen Werks\n\n"
                    "Werbegeschenke ohne Anlass (z. B. eine teure Uhr 'einfach so') "
                    "sind eher problematisch.\n\n"
                    "### 3. Transparent\n\n"
                    "Du musst die Zuwendung **offenlegen**:\n"
                    "- Vorgesetzte:r informieren\n"
                    "- Ggf. Eintrag im **Geschenke-Register** des Unternehmens\n"
                    "- Bei Wertgrenzen-Überschreitung: schriftliche Genehmigung "
                    "der Compliance-Funktion\n\n"
                    "Faustregel: **Würdest du es offen am schwarzen Brett "
                    "anschlagen?** Wenn nein → Problem.\n\n"
                    "### 4. Nicht beeinflussend\n\n"
                    "Die Zuwendung darf nicht in zeitlichem oder sachlichem "
                    "Zusammenhang mit einer Entscheidung stehen. Beispiel: "
                    "Lieferant X gibt dir während der Angebotsphase ein "
                    "Tablet — **immer problematisch**, auch bei niedrigem Wert. "
                    "Nach Vertragsabschluss zum Jahresende ein Kalender + Pralinen — "
                    "OK.\n\n"
                    "## Eher problematische Zuwendungs-Arten\n\n"
                    "### Bargeld + Gutscheine\n\n"
                    "Bar und Universal-Gutscheine (Amazon, Galeria) sind **immer "
                    "kritisch**, weil sie nicht zweckgebunden sind. Praktisch "
                    "wie Geld. Auch bei niedrigem Wert: **ablehnen**.\n\n"
                    "### Reisen, Hotels, Eintrittskarten\n\n"
                    "- **Konferenz-Teilnahme** beim Lieferanten: nur OK wenn "
                    "der **fachliche Anteil überwiegt** (mindestens 50 %), "
                    "Reise + Unterkunft im üblichen Rahmen, **Begleitperson "
                    "selbst zahlen**\n"
                    "- **Pure Vergnügungsreise** (Wellness-Wochenende auf "
                    "Mallorca): IMMER problematisch\n"
                    "- **Konzert-/Sport-Tickets**: nur OK, wenn der Lieferant "
                    "selbst mitkommt + Geschäftsbezug überwiegt\n\n"
                    "### Wiederholte Zuwendungen\n\n"
                    "Ein Pralinenpaket zu Weihnachten = OK. Jeden Monat ein "
                    "Pralinenpaket + zusätzlich zu Geburtstag, Hochzeitstag, "
                    "Schulanfang der Kinder = **Schmiergeld auf Raten**.\n\n"
                    "### Geschenke an Familienmitglieder\n\n"
                    "Wenn Lieferant deinem Kind zum Geburtstag eine Spielkonsole "
                    "schenkt, ist das **dir** als Vorteil zurechenbar. Wenn "
                    "Lieferant Sponsoring für die Schule deines Kindes bietet — "
                    "kritisch prüfen.\n\n"
                    "### Zuwendung während laufender Vergabe\n\n"
                    "**Absolutes No-Go**: Du bist im Vergabe-Prozess, ein "
                    "Anbieter schickt 'zur Erinnerung an unser Gespräch' eine "
                    "Flasche Wein. **Sofort zurücksenden + Compliance "
                    "informieren**, auch wenn nur 15 € Wert. Der Anschein "
                    "der Beeinflussung kann den Vergabeprozess kippen.\n\n"
                    "## Gegenüber Amtsträgern — verschärftes Regime\n\n"
                    "Bei Amtsträgern (Beamte, Bürgermeister, Polizei, Richter, "
                    "auch Mitarbeitende staatlicher GmbHs) gelten **deutlich "
                    "strengere** Regeln. Bereits **kleine** Zuwendungen können "
                    "strafbar sein (§ 331 StGB Vorteilsannahme — Ausnahme für "
                    "'Allgemeine Anerkennung' wie ein Kaffee bei der Behörde).\n\n"
                    "**Praktisch**: Gegenüber Amtsträgern **keine Geschenke** "
                    "geben oder nehmen, auch nicht eine Flasche Wein. Nur "
                    "Werbeartikel im einstelligen Eurobereich (Kugelschreiber, "
                    "Notizblock mit Logo).\n\n"
                    "## Wenn dir was angeboten wird, das du nicht annehmen kannst\n\n"
                    "1. **Freundlich aber bestimmt ablehnen**: 'Unser Unternehmens-"
                    "Code lässt das leider nicht zu, ich bitte um Verständnis'\n"
                    "2. Bei aufgedrängten Zuwendungen (Paket per Post): "
                    "**zurücksenden** mit kurzer Notiz\n"
                    "3. **Vorgang dokumentieren** + Vorgesetzte:n + Compliance "
                    "informieren\n"
                    "4. **Nicht auf später vertrösten** ('später vielleicht') — "
                    "das wäre Akzeptanz\n\n"
                    "Im Zweifel zu Compliance gehen, **bevor** du annimmst oder "
                    "ablehnst. Die meisten Compliance-Funktionen haben "
                    "vorgefertigte Höflichkeits-Antworten."
                ),
            ),
            ModulDef(
                titel="Lieferanten- und Kundenbeziehungen",
                inhalt_md=(
                    "## Geschäftsessen und Bewirtungen\n\n"
                    "Ein gemeinsames Mittagessen mit einem Geschäftspartner "
                    "gehört zur **normalen Geschäftspflege** und ist erlaubt — "
                    "innerhalb angemessener Grenzen.\n\n"
                    "**Faustregeln:**\n"
                    "- **Übliches Geschäftsessen**: Mittagsmenü, Brauerei-"
                    "Restaurant, regionale Küche — unproblematisch\n"
                    "- **Sterne-Restaurant + Begleitperson**: schon kritisch, "
                    "weil deutlich überdurchschnittlich\n"
                    "- **Wer einlädt, zahlt — wer eingeladen wird, isst**: "
                    "ist das Geschäftsessen vom Lieferanten ausgehend, darfst "
                    "du teilnehmen, aber dokumentiere es\n"
                    "- **Bei wiederholten Einladungen** vom selben Partner: "
                    "abwechseln (du lädst beim nächsten Mal ein, auf "
                    "Firmenrechnung)\n"
                    "- **Reisekosten** zum Geschäftsessen: jeder zahlt sein eigenes\n\n"
                    "## Einladungen zu Veranstaltungen\n\n"
                    "### Erlaubt mit Dokumentation\n\n"
                    "- **Fachveranstaltungen** mit klarem geschäftlichen Bezug "
                    "(Werksbesichtigung, Produktvorstellung, Industriemesse-"
                    "Auftritt, Fachkonferenz)\n"
                    "- **Kunden-Events** mit überwiegend fachlichem Inhalt "
                    "(z. B. Anwender-Konferenz mit Workshops, Lieferanten-Tag)\n"
                    "- **Übliche Bewirtung** im Rahmen einer Veranstaltung "
                    "(Sektempfang, Buffet)\n\n"
                    "### Sportevents und Kulturveranstaltungen\n\n"
                    "Die Klassiker — Bundesliga-Loge, Bayreuth-Festspiele, "
                    "Salzburger Festspiele. Hier ist die Grenze besonders fein:\n\n"
                    "- **Erlaubt**, wenn der Lieferant/Kunde anwesend ist + "
                    "Geschäftsbezug überwiegt (z. B. Verhandlungen am Rande)\n"
                    "- **Wert der Karte** sollte mit der Schwellenregel "
                    "kompatibel sein\n"
                    "- **Begleitperson** (Ehepartner:in) zahlt selbst oder "
                    "wird zu Hause gelassen — sonst Beeinflussungsanschein\n"
                    "- **Übernachtung + Reise**: nicht vom Geschäftspartner "
                    "bezahlt\n\n"
                    "### Klar nicht erlaubt\n\n"
                    "- **Familien-Wochenende** auf Firmenkosten des Lieferanten "
                    "(z. B. Skiurlaub im Lieferanten-Chalet mit Familie)\n"
                    "- **Reine Vergnügungsreisen** ohne Geschäftsbezug\n"
                    "- **Goldene Visitenkarten** und Statussymbole (teure "
                    "Uhren, Schmuck, Autos)\n"
                    "- **Lieferanten als 'Sponsor' privater Veranstaltungen** "
                    "(eigene Hochzeit, runde Geburtstag)\n\n"
                    "## Sponsoring und Spenden\n\n"
                    "Wenn dein Unternehmen Sponsoring oder Spenden vergibt — "
                    "z. B. Sportverein, Kulturveranstaltung, sozial — sind "
                    "diese **rechtmäßig**, aber nur unter strengen Bedingungen:\n\n"
                    "1. **Transparent dokumentiert** in der Buchhaltung\n"
                    "2. **Schriftlich genehmigt** durch die Geschäftsleitung "
                    "(nicht durch einen einzelnen Vertriebsmitarbeiter)\n"
                    "3. **Konkrete Gegenleistung** (Logo am Vereinstrikot, "
                    "Werbeplakat am Veranstaltungsort)\n"
                    "4. **Keine zeitliche/sachliche Nähe** zu einer behördlichen "
                    "Genehmigung oder Auftragsvergabe\n"
                    "5. **Empfänger** ist nicht persönlich an einer Entscheidung "
                    "über deine Firma beteiligt\n\n"
                    "**Niemals**: Spenden an die Lieblings-Wohltätigkeitsorganisation "
                    "eines Entscheidungsträgers in der Hoffnung, dass er sich "
                    "erkenntlich zeigt. Das ist verschleierte Korruption.\n\n"
                    "## Provisionen und Vermittler\n\n"
                    "Wer Aufträge in Auslandsmärkte vermittelt, arbeitet oft "
                    "mit lokalen **Vertretern** auf Provisions-Basis. Hier "
                    "lauern Korruptions-Risiken:\n\n"
                    "- **Provisionshöhe** muss marktüblich sein (typisch 2-10 %, "
                    "abhängig von Branche). Über 15 % ist verdächtig.\n"
                    "- **Schriftlicher Vertrag** mit klarer Leistungsbeschreibung\n"
                    "- **Zahlung auf Firmen-Konto**, nicht auf Privat-Konto\n"
                    "- **Compliance-Check** des Vertreters (Sanktionslisten, "
                    "PEP-Listen, Reputation)\n"
                    "- **Kein 'success-only' Bonus** für 'Verbindungen' ohne "
                    "konkrete Leistung\n\n"
                    "## Meldewege bei Verdacht\n\n"
                    "Wenn du einen Verdacht hast — auf eigene Kollegen, "
                    "Vorgesetzte, Lieferanten:\n\n"
                    "### Interner Meldekanal\n\n"
                    "**Anonymes Hinweisgeberportal** (HinSchG-Kanal) auf "
                    "`hinweise.app.vaeren.de` oder direkt an die Compliance-"
                    "Beauftragte. Das HinSchG (seit Juli 2023) schützt "
                    "Hinweisgeber explizit:\n\n"
                    "- **Identitätsschutz** — deine Identität bleibt vertraulich\n"
                    "- **Repressalien sind verboten** (§ 36 HinSchG) — keine "
                    "Kündigung, Versetzung, Lohnkürzung wegen einer Meldung\n"
                    "- **Beweislastumkehr** — bei zeitlichem Zusammenhang "
                    "muss der Arbeitgeber beweisen, dass eine Sanktion "
                    "NICHT wegen der Meldung erfolgte\n"
                    "- **Schadenersatz** bei nachgewiesener Repressalie\n\n"
                    "### Externe Meldekanäle\n\n"
                    "Wenn die interne Meldung nicht zu Maßnahmen führt oder "
                    "der Verdacht gegen die Geschäftsführung gerichtet ist:\n"
                    "- **Bundesamt für Justiz** (BfJ) — Hauptkanal nach HinSchG\n"
                    "- **BaFin** bei finanziellen Verstößen\n"
                    "- **Staatsanwaltschaft** bei Straftaten\n\n"
                    "### Was nicht melden bedeutet\n\n"
                    "Wer nachweislich von Korruption weiß und schweigt, kann "
                    "selbst der **Strafvereitelung** (§ 258 StGB) oder "
                    "**Beihilfe** (§ 27 StGB) bezichtigt werden. Schweigen "
                    "ist keine sichere Option."
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
