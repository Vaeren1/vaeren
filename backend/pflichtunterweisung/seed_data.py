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
        "Grundbegriffe, Betroffenenrechte, Umgang mit Datenpannen, "
        "technisch-organisatorische Maßnahmen (TOMs).",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Grundbegriffe & Schutzziele",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Wer im Mittelstand arbeitet, verarbeitet jeden Tag personenbezogene Daten: "
                    "Bewerbungs-Unterlagen im HR-Postfach, Kunden-Adressen im CRM, Liefer-"
                    "Ansprechpartner im ERP, Foto vom Werkstor in der WhatsApp-Gruppe. Die "
                    "Datenschutz-Grundverordnung (DSGVO) regelt, wann das erlaubt ist, wie es "
                    "dokumentiert werden muss und welche Schutzziele gelten. Du lernst, was "
                    "*personenbezogene Daten* genau sind, welche Rechtsgrundlagen für die "
                    "Verarbeitung in Frage kommen und welche sechs Schutzziele jede "
                    "Verarbeitung erfüllen muss.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 4 DSGVO** — Begriffsbestimmungen (personenbezogene Daten, Verarbeitung, Verantwortlicher)\n"
                    "- **Art. 5 DSGVO** — Grundsätze für die Verarbeitung personenbezogener Daten\n"
                    "- **Art. 6 DSGVO** — Rechtmäßigkeit der Verarbeitung (sechs Erlaubnis-Tatbestände)\n"
                    "- **Art. 9 DSGVO** — Besondere Kategorien personenbezogener Daten\n"
                    "- **§ 26 BDSG** — Datenverarbeitung im Beschäftigungsverhältnis\n\n"
                    "## Was musst du wissen\n\n"
                    "**Personenbezogene Daten** sind alle Informationen, die sich auf eine "
                    "identifizierte oder identifizierbare Person beziehen (Art. 4 Nr. 1 DSGVO). "
                    "Dazu gehören nicht nur Name und Adresse, sondern auch Kfz-Kennzeichen, "
                    "IP-Adresse, Personalnummer, Foto, Stimme im Voicemail-Postfach und sogar "
                    "die Kombination harmloser Einzeldaten, wenn sie eine Person eindeutig "
                    "identifizieren (z.B. Abteilung + Geburtsjahr + Schuhgröße).\n\n"
                    "**Besondere Kategorien** nach Art. 9 DSGVO sind streng geschützt: "
                    "Gesundheits-, Religions-, Gewerkschafts-, biometrische und sexuelle "
                    "Daten. Diese dürfen nur unter engen Voraussetzungen verarbeitet werden "
                    "(z.B. Krankschreibung in HR — Datenminimierungs-Pflicht).\n\n"
                    "Eine **Verarbeitung** ist jeder Vorgang mit Daten — erheben, speichern, "
                    "ändern, ansehen, weitergeben, löschen. Bereits das Öffnen einer "
                    "Kunden-Mail ist eine Verarbeitung. Jede Verarbeitung braucht eine "
                    "Rechtsgrundlage nach Art. 6 DSGVO:\n\n"
                    "| Buchst. | Rechtsgrundlage | Typischer Anwendungsfall |\n"
                    "|---|---|---|\n"
                    "| a | Einwilligung | Newsletter-Anmeldung, Mitarbeiter-Foto auf Webseite |\n"
                    "| b | Vertragserfüllung | Kundenauftrag, Arbeitsvertrag, Lieferschein |\n"
                    "| c | Rechtliche Pflicht | Lohnsteuer-Meldung, Aufbewahrungspflichten HGB/AO |\n"
                    "| d | Lebenswichtige Interessen | Notfall-Kontakt eines Verunglückten |\n"
                    "| e | Öffentliche Aufgabe | meist Behörden, selten Mittelstand |\n"
                    "| f | Berechtigtes Interesse | IT-Sicherheit, Video-Überwachung am Werkstor |\n\n"
                    "Die sechs **Grundsätze** nach Art. 5 DSGVO sind: Rechtmäßigkeit, "
                    "Zweckbindung, Datenminimierung, Richtigkeit, Speicherbegrenzung sowie "
                    "Integrität und Vertraulichkeit. Jede Verarbeitung muss alle sechs "
                    "gleichzeitig erfüllen. Der Verantwortliche muss das nachweisen können — "
                    "das ist die **Rechenschaftspflicht** (Art. 5 Abs. 2 DSGVO).\n\n"
                    "## Was musst du tun\n\n"
                    "Im Arbeitsalltag gilt:\n\n"
                    "1. Frage vor jeder neuen Datenverarbeitung deinen Vorgesetzten oder die "
                    "Datenschutz-Koordination, ob eine Rechtsgrundlage existiert\n"
                    "2. Verarbeite nie mehr Daten als für den Zweck nötig — eine "
                    "Lieferadresse braucht kein Geburtsdatum\n"
                    "3. Gib Daten niemals an externe Stellen weiter, ohne dass ein "
                    "Auftragsverarbeitungs-Vertrag (AV-Vertrag) vorliegt\n"
                    "4. Lege keine privaten Listen mit Kollegen- oder Kundendaten an "
                    "(z.B. Excel auf dem Desktop, Notizen im Handy)\n"
                    "5. Lösche oder anonymisiere Daten, sobald der Zweck entfallen ist "
                    "und keine Aufbewahrungs-Pflicht mehr greift\n\n"
                    "## Praxisbeispiel\n\n"
                    "Im Vertrieb eines Maschinenbauers will der Außendienst auf dem privaten "
                    "iPhone eine Excel-Liste mit 800 Kunden-Ansprechpartnern führen — schneller "
                    "Zugriff bei Kundenbesuchen. Rechtlich falsch: kein berechtigtes Interesse "
                    "ohne Schutzmaßnahmen, keine Verschlüsselung, keine zentrale Löschung bei "
                    "Kündigung des Mitarbeiters, keine Trennung von privaten Kontakten. "
                    "Lösung: das CRM auf dem Firmen-Smartphone mit MDM (Mobile Device Management), "
                    "Offline-Sync nur für die nächsten zwei Termine, Remote-Wipe bei Verlust. "
                    "Damit ist Art. 5 Abs. 1 lit. f (Integrität/Vertraulichkeit) erfüllt und "
                    "Art. 32 (TOMs) dokumentiert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DSGVO (Verordnung EU 2016/679, Art. 4, 5, 6, 9), "
                    "BDSG 2018 (§ 26) sowie DSK-Kurzpapier Nr. 1 *Verzeichnis von Verarbeitungs"
                    "tätigkeiten* und EDPB-Leitlinien 04/2019 zu Art. 25 DSGVO."
                ),
            ),
            ModulDef(
                titel="Betroffenenrechte",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Die DSGVO gibt jedem Menschen — Kunde, Bewerber, Mitarbeiter, Lieferant — "
                    "konkrete Rechte gegenüber dem Unternehmen, das seine Daten verarbeitet. "
                    "Diese Rechte sind nicht freiwillig, sondern einklagbar. Wenn ein "
                    "Bewerber per Mail fragt 'welche Daten habt ihr von mir' und das "
                    "Unternehmen ignoriert oder nach acht Wochen antwortet, droht ein Bußgeld "
                    "der Aufsichtsbehörde (im Mittelstand typisch 5.000 bis 50.000 Euro). "
                    "Du lernst, welche sechs Rechte existieren, welche Fristen gelten und "
                    "wie du eine Anfrage richtig weiterleitest.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 12 DSGVO** — Transparente Information und Modalitäten\n"
                    "- **Art. 13, 14 DSGVO** — Informationspflichten bei Erhebung\n"
                    "- **Art. 15 DSGVO** — Auskunftsrecht\n"
                    "- **Art. 16 DSGVO** — Recht auf Berichtigung\n"
                    "- **Art. 17 DSGVO** — Recht auf Löschung ('Recht auf Vergessenwerden')\n"
                    "- **Art. 18 DSGVO** — Recht auf Einschränkung der Verarbeitung\n"
                    "- **Art. 20 DSGVO** — Recht auf Datenübertragbarkeit\n"
                    "- **Art. 21 DSGVO** — Widerspruchsrecht\n"
                    "- **Art. 22 DSGVO** — Schutz vor automatisierten Entscheidungen\n\n"
                    "## Was musst du wissen\n\n"
                    "Die wichtigsten Rechte und ihre Fristen:\n\n"
                    "| Recht | Inhalt | Frist |\n"
                    "|---|---|---|\n"
                    "| Auskunft (Art. 15) | Welche Daten werden zu welchem Zweck verarbeitet | 1 Monat, +2 Monate Verlängerung möglich |\n"
                    "| Berichtigung (Art. 16) | Unrichtige Daten korrigieren | unverzüglich |\n"
                    "| Löschung (Art. 17) | Daten ohne Rechtsgrundlage müssen weg | 1 Monat |\n"
                    "| Einschränkung (Art. 18) | Daten dürfen nur noch gespeichert, nicht genutzt werden | unverzüglich |\n"
                    "| Datenübertragbarkeit (Art. 20) | Daten in maschinenlesbarem Format aushändigen | 1 Monat |\n"
                    "| Widerspruch (Art. 21) | Verarbeitung stoppen, wenn schutzwürdige Gründe überwiegen | unverzüglich prüfen |\n\n"
                    "Das **Auskunftsrecht** (Art. 15) ist im Alltag am wichtigsten. Der "
                    "Betroffene bekommt eine Kopie aller seiner Daten plus Information über "
                    "Zwecke, Empfänger, Speicherdauer und seine weiteren Rechte. Wichtige "
                    "Sonderregel: Auskunft an Mitarbeiter umfasst auch interne Notizen, "
                    "Bewertungen im Personalbogen und E-Mails über die Person (BAG 2023).\n\n"
                    "Das **Recht auf Löschung** ist nicht absolut. Eine Löschung wird durch "
                    "**Aufbewahrungs-Pflichten** überlagert — z.B. 10 Jahre für Buchhaltungs-"
                    "Belege nach § 147 AO, 6 Jahre für Handels-Briefe nach § 257 HGB. Hier "
                    "wird statt gelöscht *eingeschränkt*: die Daten werden gesperrt und sind "
                    "nur noch für den Aufbewahrungs-Zweck verfügbar.\n\n"
                    "Eine Anfrage ist **formfrei**: per Mail, per Telefon, persönlich am "
                    "Empfang. Sie muss nicht das Wort 'DSGVO' enthalten — wenn jemand fragt "
                    "'was wisst ihr alles über mich', ist das eine Auskunftsanfrage.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn dich eine Anfrage erreicht:\n\n"
                    "1. Bestätige den Eingang noch am selben Tag mit Empfangsbestätigung\n"
                    "2. Leite die Anfrage sofort an die Datenschutz-Koordination oder den "
                    "Datenschutzbeauftragten weiter — nicht selbst beantworten\n"
                    "3. Notiere Eingangs-Datum, Absender und Inhalt im Ticket-System (Frist läuft!)\n"
                    "4. Identifiziere den Anfragenden bei Zweifeln über Ausweis-Kopie oder "
                    "Sicherheits-Frage — Auskunft an falsche Person ist eine Datenpanne\n"
                    "5. Lösche, sperre oder berichtige keine Daten in Eigenregie, bevor "
                    "geklärt ist, was die korrekte Reaktion ist\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein ehemaliger Mitarbeiter im Vertrieb schreibt nach drei Monaten an "
                    "info@-Postfach: 'Bitte alle meine Daten herausgeben und löschen.' Die "
                    "Empfangs-Mitarbeiterin leitet die Mail intern weiter und antwortet mit "
                    "Eingangsbestätigung. Die HR-Abteilung sammelt: Personalakte, "
                    "Lohnabrechnungen, Schulungs-Zertifikate, CRM-Notizen aus seiner Vertriebs"
                    "tätigkeit, E-Mails im gemeinsamen Postfach. Auskunft erfolgt nach 23 "
                    "Tagen als PDF-Paket per verschlüsseltem Download-Link. Gelöscht werden "
                    "nur die CRM-Notizen und sein Profil-Foto — Lohn- und Steuerunterlagen "
                    "bleiben gesperrt bis zur 10-Jahres-Frist nach § 147 AO. Der Mitarbeiter "
                    "wird in der Antwort über die Aufbewahrungs-Pflichten informiert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DSGVO Art. 12 bis 22, BDSG § 34 (Auskunft) und "
                    "§ 35 (Löschung), DSK-Kurzpapier Nr. 6 *Auskunftsrecht* sowie "
                    "EDPB-Leitlinien 01/2022 zu den Betroffenenrechten (Art. 15 DSGVO)."
                ),
            ),
            ModulDef(
                titel="Datenpannen erkennen und melden",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Eine **Datenpanne** ist nicht nur der Hackerangriff aus dem Fernsehen. "
                    "Der USB-Stick mit der Lohnliste, den der Kollege im Zug liegen lässt, "
                    "ist eine Datenpanne. Die Mail mit 200 Kunden im CC statt BCC ist eine. "
                    "Das Notebook mit dem Bewerbungs-Ordner, das aus dem Auto gestohlen wird, "
                    "ist eine. Und alle drei haben eine harte 72-Stunden-Meldefrist an die "
                    "Aufsichtsbehörde. Du lernst, was eine Datenpanne ist, wie du sie sofort "
                    "erkennst und welche internen Schritte in den ersten Minuten zählen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 4 Nr. 12 DSGVO** — Definition der Verletzung des Schutzes personenbezogener Daten\n"
                    "- **Art. 33 DSGVO** — Meldepflicht an die Aufsichtsbehörde binnen 72 Stunden\n"
                    "- **Art. 34 DSGVO** — Benachrichtigung der Betroffenen bei hohem Risiko\n"
                    "- **Art. 83 DSGVO** — Bußgeld bis 20 Mio. € oder 4 % des Jahresumsatzes\n"
                    "- **§ 42, 43 BDSG** — Strafbarkeit und Ordnungswidrigkeiten\n\n"
                    "## Was musst du wissen\n\n"
                    "Eine Datenpanne liegt nach Art. 4 Nr. 12 DSGVO immer dann vor, wenn "
                    "eines der drei Schutzziele verletzt ist:\n\n"
                    "- **Vertraulichkeit** — Unbefugte haben Zugriff erlangt (verlorener USB-Stick, "
                    "Mail an Falschen, Diebstahl)\n"
                    "- **Integrität** — Daten wurden unbefugt verändert oder verfälscht "
                    "(Manipulation, Ransomware)\n"
                    "- **Verfügbarkeit** — Daten sind verloren oder vernichtet (gelöschter "
                    "Backup, defekte Festplatte ohne Sicherung)\n\n"
                    "Typische Vorfälle im Mittelstand:\n\n"
                    "| Vorfall | Verletztes Schutzziel | Meldepflicht? |\n"
                    "|---|---|---|\n"
                    "| USB-Stick mit Mitarbeiterliste verloren | Vertraulichkeit | Ja, wenn unverschlüsselt |\n"
                    "| 50 Kundenadressen im offenen CC | Vertraulichkeit | Ja, wenn sensible Daten |\n"
                    "| Phishing-Mail geklickt, Passwort eingegeben | Vertraulichkeit + Integrität | Ja |\n"
                    "| Ransomware verschlüsselt Datei-Server | Verfügbarkeit + Integrität | Ja |\n"
                    "| Notebook mit verschlüsselter Festplatte gestohlen | gering | meist Nein, dokumentieren |\n"
                    "| Falsche Lohnabrechnung an Kollege geschickt | Vertraulichkeit | Ja |\n\n"
                    "Die **72-Stunden-Frist** nach Art. 33 DSGVO beginnt mit dem Moment, in "
                    "dem das Unternehmen vom Vorfall *Kenntnis* erhält — nicht erst, wenn "
                    "alle Details geklärt sind. Eine *unvollständige Erstmeldung* mit Nachreichung "
                    "weiterer Informationen ist ausdrücklich vorgesehen.\n\n"
                    "Bei *hohem Risiko* für die Betroffenen (sensible Daten, Identitäts"
                    "diebstahl, finanzieller Schaden) müssen zusätzlich die Betroffenen "
                    "selbst informiert werden — in klarer, einfacher Sprache (Art. 34).\n\n"
                    "Eine **Verschlüsselung** nach Stand der Technik (z.B. BitLocker-FDE, "
                    "GPG-Mail) ist der wichtigste Risiko-Reduzierer: ein verlorener "
                    "verschlüsselter Stick ist meist keine meldepflichtige Panne, weil "
                    "Unbefugte nicht zugreifen können (EDPB-Leitlinien 9/2022).\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du eine Panne bemerkst oder vermutest:\n\n"
                    "1. Sofort die IT und die Datenschutz-Koordination informieren — "
                    "nicht warten, nicht erst recherchieren\n"
                    "2. Nichts vertuschen, nichts löschen, keine 'schnelle Reparatur' "
                    "ohne Rücksprache (Beweise könnten zerstört werden)\n"
                    "3. Notiere Uhrzeit der Entdeckung, was passiert ist, wer beteiligt "
                    "war und welche Daten betroffen sind\n"
                    "4. Bei verlorenem Gerät: sofortiges Remote-Wipe veranlassen, "
                    "Zugänge sperren, Passwörter ändern lassen\n"
                    "5. Keine Auskünfte an Dritte oder Presse — Kommunikation erfolgt "
                    "ausschließlich über die Geschäftsführung\n\n"
                    "Es gilt: lieber zu früh melden als zu spät. Eine harmlose Panne intern "
                    "zu eskalieren kostet nichts. Eine verschwiegene Panne kann das "
                    "Unternehmen 4 % des Jahresumsatzes kosten.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine HR-Mitarbeiterin schickt versehentlich die Liste mit 230 Mitarbeitern "
                    "inklusive Geburtsdatum und Schwerbehindertenstatus per Mail an einen "
                    "externen Steuerberater, der eigentlich nur die Lohnsumme bekommen sollte. "
                    "Sie bemerkt den Fehler 15 Minuten später. Richtige Reaktion: anrufen, "
                    "Löschung schriftlich bestätigen lassen, ihre Vorgesetzte informieren, "
                    "Datenschutz-Koordination einbinden. Die Geschäftsführung meldet binnen "
                    "24 Stunden an die Aufsichtsbehörde (Vertraulichkeitsverletzung mit "
                    "sensiblen Daten nach Art. 9). Die Betroffenen werden in einer "
                    "Sammel-Mail informiert. Folge: kein Bußgeld, weil schnell gemeldet, "
                    "schnell eingedämmt, dokumentierte TOMs vorhanden.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DSGVO Art. 4 Nr. 12, Art. 33, Art. 34, Art. 83, "
                    "BDSG §§ 42 und 43, DSK-Kurzpapier Nr. 18 *Risiko für die Rechte und "
                    "Freiheiten natürlicher Personen* sowie EDPB-Leitlinien 9/2022 zu "
                    "Beispielen für Datenpannen-Meldungen."
                ),
            ),
            ModulDef(
                titel="Technisch-organisatorische Maßnahmen (TOMs)",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "**TOMs** (technisch-organisatorische Maßnahmen) sind alles, was ein "
                    "Unternehmen tut, um Daten vor Verlust, Diebstahl und unbefugtem Zugriff "
                    "zu schützen — von der Tür mit Code-Schloss am Server-Raum bis zur "
                    "Cloud-Backup-Verschlüsselung. Art. 32 DSGVO verlangt sie ausdrücklich, "
                    "und sie sind das, was die Aufsichtsbehörde im Fall einer Datenpanne als "
                    "erstes prüft. Du lernst die fünf Säulen der TOMs, was du selbst dazu "
                    "beitragen kannst und wie die zentralen Maßnahmen im Mittelstand "
                    "aussehen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 24 DSGVO** — Verantwortung des Verantwortlichen\n"
                    "- **Art. 25 DSGVO** — Datenschutz durch Technikgestaltung und Voreinstellungen\n"
                    "- **Art. 32 DSGVO** — Sicherheit der Verarbeitung (Stand der Technik)\n"
                    "- **Art. 30 DSGVO** — Verzeichnis von Verarbeitungstätigkeiten (VVT)\n"
                    "- **BSI-Grundschutz** — Empfohlener Maßnahmen-Katalog für deutsche Unternehmen\n\n"
                    "## Was musst du wissen\n\n"
                    "TOMs folgen einer Risiko-Bewertung: je sensibler die Daten, desto "
                    "höher die Anforderungen. Die fünf Säulen nach EDPB-Praxis:\n\n"
                    "| Säule | Beispiel-Maßnahmen |\n"
                    "|---|---|\n"
                    "| Zutritt | Schließanlage, Besucherausweis, Server-Raum mit Code-Schloss |\n"
                    "| Zugang | Passwort-Richtlinie, MFA, Single-Sign-On, Bildschirm-Sperre |\n"
                    "| Zugriff | Rollen-/Rechte-Konzept, Need-to-know, Berechtigungs-Review |\n"
                    "| Weitergabe | Mail-Verschlüsselung, VPN, AV-Verträge, Schwärzung |\n"
                    "| Verfügbarkeit | Backup, USV, Notfall-Plan, Restore-Tests |\n\n"
                    "**Passwörter** sind das schwächste Glied. BSI-Empfehlung 2024: "
                    "mindestens 12 Zeichen, einzigartig pro Dienst, in einem Passwort-Manager "
                    "verwaltet (z.B. KeePass, Bitwarden). Mehr-Faktor-Authentifizierung "
                    "(MFA) auf allen Cloud-Diensten und auf dem VPN ist Pflicht — ein "
                    "geleaktes Passwort allein reicht dann nicht für den Zugriff.\n\n"
                    "**Verschlüsselung** unterscheidet drei Zustände: at-rest (Festplatte), "
                    "in-transit (Mail, Web) und in-use (selten). Notebooks und externe "
                    "Datenträger müssen at-rest verschlüsselt sein (BitLocker, FileVault, "
                    "VeraCrypt). Mail-Anhänge mit sensiblen Inhalten gehen nur über "
                    "verschlüsselte Mail (S/MIME, PGP) oder einen passwortgeschützten "
                    "Download-Link.\n\n"
                    "**Cloud-Backups** müssen ebenfalls verschlüsselt und nach dem 3-2-1-Prinzip "
                    "abgelegt werden: 3 Kopien, 2 Medien, 1 davon außer Haus. Ein "
                    "unverschlüsseltes Cloud-Backup mit Personalakten ist ein Bußgeld-Magnet.\n\n"
                    "**Auftragsverarbeiter** (AV) sind alle Dienstleister, die in deinem "
                    "Auftrag Daten verarbeiten: Cloud-CRM, Steuerberater, Lohnbüro, "
                    "Cloud-Mail-Provider, Speditions-Software. Jeder AV braucht einen "
                    "schriftlichen Vertrag nach Art. 28 DSGVO, sonst ist die Verarbeitung "
                    "unrechtmäßig.\n\n"
                    "## Was musst du tun\n\n"
                    "Deine eigenen TOMs im Arbeitsalltag:\n\n"
                    "1. Sperre den Bildschirm bei jedem Verlassen des Arbeitsplatzes "
                    "(Windows-Taste + L, Cmd+Ctrl+Q)\n"
                    "2. Nutze niemals dasselbe Passwort für mehrere Systeme und benutze "
                    "den vom Unternehmen vorgegebenen Passwort-Manager\n"
                    "3. Schicke sensible Daten nie unverschlüsselt per Mail oder über "
                    "private Cloud-Dienste (WeTransfer, Dropbox, WhatsApp)\n"
                    "4. Lass keine USB-Sticks oder Notebooks im Auto, in der Bahn oder im "
                    "Hotelzimmer ohne Verschlüsselung liegen\n"
                    "5. Melde verdächtige Mails (Phishing) sofort an die IT und klicke "
                    "weder auf Links noch öffne Anhänge\n"
                    "6. Drucke nur, wenn nötig, und hole Ausdrucke sofort am Drucker ab — "
                    "*Clean-Desk-Prinzip*\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Vertriebsmitarbeiter verliert auf einer Messe sein Firmen-Notebook "
                    "mit 1.200 Kundenkontakten und Angebots-PDFs. Weil das Gerät mit "
                    "BitLocker und PIN-Pflicht beim Start verschlüsselt ist, hat der Finder "
                    "keinen Zugriff auf Inhalte. Die IT setzt per Intune Remote-Wipe und "
                    "sperrt das Microsoft-365-Konto innerhalb von 20 Minuten. Die "
                    "Datenschutz-Koordination dokumentiert den Vorfall als 'Vorfall mit "
                    "geringem Risiko' im internen Register — eine Meldung an die "
                    "Aufsichtsbehörde nach Art. 33 ist nicht erforderlich, weil die TOMs "
                    "(Verschlüsselung at-rest plus Remote-Wipe) den Zugriff verhindert "
                    "haben. Ohne BitLocker hätte derselbe Vorfall eine 72-Stunden-Meldung, "
                    "Information aller 1.200 Kunden und potenziell 50.000 Euro Bußgeld "
                    "ausgelöst.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DSGVO Art. 24, 25, 28, 30, 32, "
                    "BSI-Grundschutz-Kompendium (Edition 2023), DSK-Kurzpapier Nr. 1 "
                    "*Verzeichnis von Verarbeitungstätigkeiten* und EDPB-Leitlinien 4/2019 "
                    "zu Datenschutz durch Technikgestaltung."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche der folgenden Informationen ist KEIN personenbezogenes Datum nach Art. 4 Nr. 1 DSGVO?",
                erklaerung="Eine anonymisierte Statistik ohne Re-Identifikationsmöglichkeit "
                "ist nicht personenbezogen. IP-Adresse, Personalnummer und Kfz-Kennzeichen "
                "sind personenbezogene Daten — sie lassen sich auf eine Person zurückführen.",
                optionen=_opts(
                    ("IP-Adresse eines Webseiten-Besuchers", False),
                    ("Personalnummer eines Mitarbeiters", False),
                    ("Anonymisierte Statistik 'Wir haben 230 Mitarbeiter'", True),
                    ("Kfz-Kennzeichen auf einem Firmenparkplatz", False),
                ),
            ),
            FrageDef(
                text="Du willst eine Newsletter-Liste für Marketing-Mails aufbauen. Welche Rechtsgrundlage nach Art. 6 DSGVO ist hier richtig?",
                erklaerung="Werbe-Mails an Privatpersonen brauchen eine ausdrückliche "
                "Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO plus § 7 UWG. "
                "Berechtigtes Interesse reicht hier nicht.",
                optionen=_opts(
                    ("Art. 6 Abs. 1 lit. b — Vertragserfüllung", False),
                    ("Art. 6 Abs. 1 lit. a — Einwilligung", True),
                    ("Art. 6 Abs. 1 lit. c — Rechtliche Pflicht", False),
                    ("Art. 6 Abs. 1 lit. f — Berechtigtes Interesse", False),
                ),
            ),
            FrageDef(
                text="Wie lange hat ein Unternehmen Zeit, eine Auskunfts-Anfrage nach Art. 15 DSGVO zu beantworten?",
                erklaerung="Die Frist nach Art. 12 Abs. 3 DSGVO ist ein Monat. Sie kann "
                "bei komplexen Anfragen um zwei weitere Monate verlängert werden — der "
                "Betroffene muss dann begründet informiert werden.",
                optionen=_opts(
                    ("72 Stunden", False),
                    ("7 Tage", False),
                    ("1 Monat (mit Verlängerung max. 3 Monate)", True),
                    ("6 Monate", False),
                ),
            ),
            FrageDef(
                text="Welche Aufbewahrungs-Frist gilt typischerweise für Lohnabrechnungen und Buchhaltungs-Belege?",
                erklaerung="§ 147 AO und § 257 HGB schreiben 10 Jahre Aufbewahrung für "
                "Buchungs-Belege, Bilanzen und Lohnunterlagen vor. Eine Löschung nach "
                "Art. 17 DSGVO ist erst nach Ablauf dieser Frist möglich.",
                optionen=_opts(
                    ("3 Jahre nach § 195 BGB", False),
                    ("10 Jahre nach § 147 AO und § 257 HGB", True),
                    ("Sofort nach Beendigung des Arbeitsverhältnisses", False),
                    ("30 Jahre wie bei Notariats-Akten", False),
                ),
            ),
            FrageDef(
                text="Welche Frist gilt nach Art. 33 DSGVO für die Meldung einer Datenpanne an die Aufsichtsbehörde?",
                erklaerung="Die Frist ist 72 Stunden ab Kenntnis. Sie beginnt nicht erst, "
                "wenn alle Details geklärt sind — eine unvollständige Erstmeldung mit "
                "Nachreichung ist ausdrücklich erlaubt.",
                optionen=_opts(
                    ("24 Stunden", False),
                    ("72 Stunden", True),
                    ("7 Werktage", False),
                    ("Eine Frist gibt es nicht, nur Empfehlung 'unverzüglich'", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'besondere Kategorie personenbezogener Daten' nach Art. 9 DSGVO?",
                erklaerung="Art. 9 DSGVO listet Gesundheits-, Religions-, Gewerkschafts-, "
                "biometrische, genetische und sexuelle Daten als besonders schützenswert. "
                "Sie dürfen nur unter engen Ausnahmen verarbeitet werden.",
                optionen=_opts(
                    ("Kfz-Kennzeichen und Telefonnummern", False),
                    ("Bankverbindung und Personalnummer", False),
                    ("Gesundheits-, Religions-, Gewerkschafts-, biometrische Daten", True),
                    ("Alle Daten, die mehr als drei Jahre gespeichert sind", False),
                ),
            ),
            FrageDef(
                text="Welche Strafhöhe sieht Art. 83 DSGVO bei besonders schweren Verstößen vor?",
                erklaerung="Bis zu 20 Mio. € oder 4 % des weltweiten Jahresumsatzes — je "
                "nachdem, welcher Betrag höher ist. Im Mittelstand sind reale Bußgelder "
                "meist 5.000 bis 100.000 €, in Konzernen Millionen.",
                optionen=_opts(
                    ("Bis 5.000 € pauschal", False),
                    ("Bis 250.000 € unabhängig vom Umsatz", False),
                    ("Bis 20 Mio. € oder 4 % des Jahresumsatzes — je nachdem was höher ist", True),
                    ("Nur Verwarnung beim ersten Verstoß", False),
                ),
            ),
            FrageDef(
                text="Du bekommst per Mail eine Anfrage 'Bitte sendet mir alle Daten, die ihr über mich habt'. Was tust du zuerst?",
                erklaerung="Eingang sofort bestätigen, Frist beginnt zu laufen, "
                "Anfrage an die zuständige Stelle weiterleiten. Selbst beantworten ohne "
                "Rücksprache ist riskant — unvollständige Auskunft ist Verstoß.",
                optionen=_opts(
                    ("Selbst alle Daten zusammensuchen und antworten", False),
                    ("Eingang bestätigen und Anfrage an Datenschutz-Koordination weiterleiten", True),
                    ("Ignorieren, bis der Anfragende erneut schreibt", False),
                    ("Den Anfragenden bitten, das Wort 'DSGVO' zu verwenden", False),
                ),
            ),
            FrageDef(
                text="Eine Kollegin schickt versehentlich eine Mail mit 80 Kunden-Adressen im offenen CC statt BCC. Ist das eine Datenpanne?",
                erklaerung="Ja — Vertraulichkeitsverletzung, weil alle Empfänger die "
                "Adressen aller anderen sehen. Bei sensiblen Empfänger-Gruppen "
                "(z.B. Kunden einer Anwaltskanzlei, Patienten) ist Meldung Art. 33 fällig.",
                optionen=_opts(
                    ("Nein, das ist nur ein technischer Fehler ohne Datenschutz-Bezug", False),
                    ("Ja, Vertraulichkeitsverletzung — sofort Datenschutz und IT informieren", True),
                    ("Nur dann, wenn ein Kunde sich beschwert", False),
                    ("Nein, weil keine 'sensiblen' Daten betroffen sind", False),
                ),
            ),
            FrageDef(
                text="Du verlierst einen USB-Stick mit Mitarbeiter-Listen. Was unterscheidet eine meldepflichtige von einer nicht-meldepflichtigen Panne?",
                erklaerung="Eine starke Verschlüsselung nach Stand der Technik (z.B. "
                "VeraCrypt mit langem Passwort) macht den Zugriff für Finder praktisch "
                "unmöglich — meldepflichtig ist meist nur der unverschlüsselte Verlust.",
                optionen=_opts(
                    ("Die Größe des USB-Sticks in GB", False),
                    ("Ob der Stick verschlüsselt war oder nicht", True),
                    ("Ob der Verlust am Wochenende passiert ist", False),
                    ("Ob mehr als 100 Personen betroffen sind", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Aktionen ist nach Art. 5 DSGVO als 'Verarbeitung' zu werten?",
                erklaerung="Art. 4 Nr. 2 DSGVO definiert Verarbeitung extrem breit: jeder "
                "Vorgang mit Daten — erheben, ansehen, speichern, weiterleiten. Schon das "
                "Öffnen einer Kunden-Mail erfüllt den Tatbestand.",
                optionen=_opts(
                    ("Eine Kunden-Mail im Posteingang öffnen und lesen", True),
                    ("Ein Bild eines Sonnenuntergangs anschauen", False),
                    ("Eine anonymisierte Statistik in einer Zeitung lesen", False),
                    ("Im Schaufenster die Auslage betrachten", False),
                ),
            ),
            FrageDef(
                text="Welche Pflicht trifft das Unternehmen nach Art. 30 DSGVO?",
                erklaerung="Das Verzeichnis von Verarbeitungstätigkeiten (VVT) ist Pflicht "
                "für jedes Unternehmen mit regelmäßiger Verarbeitung oder besonderen "
                "Kategorien. Es muss bei Anfrage der Aufsichtsbehörde vorgelegt werden.",
                optionen=_opts(
                    ("Veröffentlichung aller Daten im Internet", False),
                    ("Führung eines Verzeichnisses von Verarbeitungstätigkeiten (VVT)", True),
                    ("Tägliche Berichterstattung an die Aufsichtsbehörde", False),
                    ("Anmeldung jedes Mitarbeiters beim BfDI", False),
                ),
            ),
            FrageDef(
                text="Welche Mindest-Anforderung gilt nach BSI-Empfehlung 2024 für sichere Passwörter?",
                erklaerung="Mindestens 12 Zeichen, einzigartig pro Dienst, in einem "
                "Passwort-Manager verwaltet. Komplexitäts-Regeln wie 'mit Sonderzeichen' "
                "sind weniger wichtig als Länge und Einzigartigkeit.",
                optionen=_opts(
                    ("8 Zeichen, ein Sonderzeichen, alle 30 Tage wechseln", False),
                    ("Mindestens 12 Zeichen, einzigartig pro Dienst, im Passwort-Manager", True),
                    ("Beliebige Länge, Hauptsache der Nutzer kann es sich merken", False),
                    ("Mindestens 4 Zeichen für interne Systeme", False),
                ),
            ),
            FrageDef(
                text="Was tust du, wenn du eine verdächtige Phishing-Mail mit Link erhältst?",
                erklaerung="Nicht klicken, keinen Anhang öffnen — sofort an die IT melden. "
                "Phishing-Mails sind die häufigste Ursache von Datenpannen im Mittelstand "
                "(BSI-Lagebericht 2023).",
                optionen=_opts(
                    ("Den Link öffnen, um zu prüfen ob er echt ist", False),
                    ("Nicht klicken, nicht beantworten, sofort an die IT melden", True),
                    ("Die Mail löschen und niemandem davon erzählen", False),
                    ("An Kollegen weiterleiten, um zu warnen", False),
                ),
            ),
            FrageDef(
                text="Du willst eine Kunden-Liste an einen externen Steuerberater schicken. Was brauchst du dafür mindestens?",
                erklaerung="Ein Auftragsverarbeitungs-Vertrag (AV-Vertrag) nach Art. 28 "
                "DSGVO ist Pflicht für jeden Dienstleister, der in deinem Auftrag "
                "personenbezogene Daten verarbeitet. Ohne AV-Vertrag ist die Weitergabe "
                "unrechtmäßig.",
                optionen=_opts(
                    ("Nur die Einwilligung des Geschäftsführers", False),
                    ("Einen Auftragsverarbeitungs-Vertrag nach Art. 28 DSGVO", True),
                    ("Eine mündliche Zusage des Steuerberaters", False),
                    ("Nichts — Steuerberater sind als Berufsgeheimnis-Träger ausgenommen", False),
                ),
            ),
            FrageDef(
                text="Welcher der folgenden Cloud-Dienste darf NICHT für sensible Firmendaten verwendet werden, ohne dass weitere Schutzmaßnahmen getroffen sind?",
                erklaerung="Private Cloud-Konten und Verbraucher-Dienste haben keinen "
                "AV-Vertrag und keine geprüften TOMs. Sensible Firmendaten gehören in "
                "freigegebene Firmen-Cloud-Dienste mit AV-Vertrag und Verschlüsselung.",
                optionen=_opts(
                    ("Persönliches WhatsApp / Dropbox / privater Gmail-Account", True),
                    ("Vom Unternehmen freigegebenes Microsoft 365 mit AV-Vertrag", False),
                    ("Vom Unternehmen freigegebenes SharePoint mit Rechte-Konzept", False),
                    ("Vom Unternehmen freigegebene Nextcloud auf eigenem Server", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Maßnahmen zählt NICHT zu den TOMs nach Art. 32 DSGVO?",
                erklaerung="Werbe-Mail an Bestandskunden ist Marketing-Aktivität, keine "
                "Schutzmaßnahme. Schließanlage, MFA und Backups sind klassische TOMs nach "
                "Zugang, Zugriff und Verfügbarkeit.",
                optionen=_opts(
                    ("Schließanlage am Server-Raum (Zutritt)", False),
                    ("Mehr-Faktor-Authentifizierung im VPN (Zugang)", False),
                    ("Regelmäßige Werbe-Mails an Bestandskunden", True),
                    ("Tägliches verschlüsseltes Backup (Verfügbarkeit)", False),
                ),
            ),
            FrageDef(
                text="Ein Mitarbeiter verlangt, dass sein Foto im Intranet sofort entfernt wird. Wie reagierst du?",
                erklaerung="Das Foto ist personenbezogenes Datum, Grundlage ist meist "
                "Einwilligung nach Art. 6 Abs. 1 lit. a — diese ist jederzeit widerrufbar. "
                "Foto unverzüglich entfernen und Widerruf dokumentieren.",
                optionen=_opts(
                    ("Foto bleibt drin, da es schon veröffentlicht ist", False),
                    ("Widerruf der Einwilligung akzeptieren, Foto entfernen, dokumentieren", True),
                    ("Mitarbeiter muss eine schriftliche Begründung liefern", False),
                    ("Foto bleibt drin bis zur Kündigung", False),
                ),
            ),
            FrageDef(
                text="Welche Rolle hat der Datenschutzbeauftragte (DSB) nach Art. 39 DSGVO?",
                erklaerung="Der DSB berät, schult und überwacht — er ist nicht für die "
                "Einhaltung der DSGVO verantwortlich, das bleibt die Geschäftsführung. "
                "Er ist Ansprechpartner für Aufsichtsbehörde und Betroffene.",
                optionen=_opts(
                    ("Er übernimmt die Haftung für alle Datenpannen", False),
                    ("Er beratet die Geschäftsleitung, schult und ist Ansprechpartner für Behörden und Betroffene", True),
                    ("Er muss persönlich jede Mail mit Kundendaten freigeben", False),
                    ("Er hat die Rolle eines internen Staatsanwalts", False),
                ),
            ),
            FrageDef(
                text="Du findest eine ausgedruckte Lohnliste mit allen Gehältern in der Kaffee-Küche. Was tust du?",
                erklaerung="Vertraulichkeitsbruch — sofort handeln. Liste sichern, "
                "Vorgesetzte und Datenschutz-Koordination informieren. Mitarbeiter selbst "
                "zu konfrontieren ist nicht deine Aufgabe — das übernimmt HR.",
                optionen=_opts(
                    ("Ignorieren, ist nicht meine Aufgabe", False),
                    ("Liste mitnehmen, Vorgesetzte und Datenschutz sofort informieren", True),
                    ("Foto machen und in der Team-Chat-Gruppe teilen", False),
                    ("Die Liste lesen und am Drucker liegen lassen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #2
    KursDef(
        titel="IT-Security & Phishing-Erkennung",
        beschreibung="Cyber-Security-Pflichtbasiskurs nach DSGVO Art. 32 + ISO 27001. "
        "Passwörter, MFA, Phishing-Erkennung, mobiles Arbeiten, Verhalten bei Sicherheitsvorfällen.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Passwörter & Multi-Faktor-Authentifizierung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein geknacktes Passwort ist 2025 der häufigste Einstiegsweg für Angreifer "
                    "ins Firmennetz — vor Schadsoftware, vor Sicherheitslücken, vor Innentätern. "
                    "Ein 8-stelliges Passwort aus Kleinbuchstaben knackt eine handelsübliche "
                    "Grafikkarte heute in Sekunden. Du lernst, wie ein modernes Passwort aussieht, "
                    "warum das alte Ritual des monatlichen Wechselns inzwischen als kontraproduktiv "
                    "gilt und warum ohne **Multi-Faktor-Authentifizierung (MFA)** kein "
                    "geschäftskritisches Konto mehr betrieben werden darf.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 32 DSGVO** — technisch-organisatorische Maßnahmen, Stand der Technik\n"
                    "- **§ 64 BDSG** — sichere Authentisierung bei der Verarbeitung personenbezogener Daten\n"
                    "- **ISO/IEC 27001:2022 Annex A.5.17** — Authentication information\n"
                    "- **BSI IT-Grundschutz ORP.4** — Identitäts- und Berechtigungsmanagement (Edition 2023)\n"
                    "- **NIS-2-Richtlinie / NIS2UmsuCG** — MFA-Pflicht für wesentliche und wichtige Einrichtungen ab 2025\n\n"
                    "## Was musst du wissen\n\n"
                    "Das BSI hat seine Passwort-Empfehlung 2020 grundlegend überarbeitet und im "
                    "Januar 2025 erneut bekräftigt: nicht mehr regelmäßig wechseln, sondern *lang "
                    "und stark einmal setzen* — und MFA dazuschalten. Der Grund: erzwungene "
                    "Wechselzyklen führen nachweislich zu schwächeren Passwörtern (Pa$$wort1, "
                    "Pa$$wort2, Pa$$wort3 ...), die Angreifer mit einfacher Iteration knacken.\n\n"
                    "Die aktuellen Mindestanforderungen nach BSI und NIST SP 800-63B:\n\n"
                    "| Szenario | Mindestlänge | Zeichenarten | Wechsel |\n"
                    "|---|---|---|---|\n"
                    "| Komplexes Passwort | 8-12 Zeichen | 4 (Groß, klein, Ziffer, Sonderzeichen) | nur bei Verdacht auf Kompromittierung |\n"
                    "| Passphrase | 20-25 Zeichen | 2 (zwei Wortarten reichen) | nur bei Verdacht auf Kompromittierung |\n"
                    "| Arbeitsplatz-PC (BSI) | 20 Zeichen empfohlen | gemischt | nur bei Verdacht |\n"
                    "| WLAN-Schlüssel | mindestens 20 Zeichen | gemischt | bei Personalwechsel |\n\n"
                    "Eine **Passphrase** ist ein Satz oder eine Wortkette wie 'Roter-Bagger-tanzt-im-Werkstattregal-77' "
                    "— leichter zu merken und kryptografisch stärker als 'X8!q.Pz#'. Das Verfahren "
                    "**Diceware** würfelt vier bis sechs zufällige Wörter aus einer 7776 Wörter "
                    "langen Liste — sechs Wörter ergeben rund 77 Bit Entropie, mehr als jedes "
                    "8-stellige Sonderzeichen-Passwort.\n\n"
                    "**Passwort-Manager** sind heute Pflichtwerkzeug. Bitwarden, KeePassXC oder 1Password "
                    "erzeugen für jeden Dienst ein einzigartiges, langes Zufallspasswort und füllen "
                    "es automatisch aus. Ein einziges starkes Master-Passwort plus MFA schützt "
                    "den ganzen Tresor.\n\n"
                    "**MFA** verlangt einen zweiten Faktor zusätzlich zum Passwort:\n\n"
                    "- **Wissen** — was du weißt (Passwort, PIN)\n"
                    "- **Besitz** — was du hast (Smartphone-App, Hardware-Token, Yubikey)\n"
                    "- **Inhärenz** — was du bist (Fingerabdruck, Gesicht)\n\n"
                    "TOTP-Apps wie Microsoft Authenticator, Aegis oder Google Authenticator sind "
                    "Standard. SMS-Codes gelten als unsicher (SIM-Swapping). Phishing-resistent "
                    "sind nur Hardware-Schlüssel nach **FIDO2/WebAuthn** und neuerdings **Passkeys**, "
                    "die das Passwort komplett ersetzen.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Nutze für jeden Dienst ein eigenes, mindestens 12-stelliges Passwort oder eine 20-Zeichen-Passphrase\n"
                    "2. Speichere alle Passwörter im Firmen-Passwort-Manager, niemals in Browser, Excel-Tabelle oder Klebezettel\n"
                    "3. Aktiviere MFA für jeden Dienst, der es anbietet — Mail, Microsoft 365, ERP, VPN, Cloud-Speicher\n"
                    "4. Wechsle dein Passwort nur, wenn du den Verdacht hast, dass es kompromittiert wurde (z. B. Datenleak-Meldung)\n"
                    "5. Teile dein Passwort mit niemandem — auch nicht mit der IT, auch nicht mit dem Chef\n"
                    "6. Bei Verdacht auf Kompromittierung: sofort Passwort ändern und die IT informieren\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Einkäufer in einem Maschinenbau-Zulieferer nutzt seit Jahren das Passwort "
                    "'Werkstatt2019!' für sein SAP-Login. Bei einem Datenleak eines Hotel-Buchungs"
                    "portals taucht eine ähnliche Variante in einer Leak-Datenbank auf. Ein Angreifer "
                    "probiert die Mail-Adresse mit dem geleakten Passwort am Firmen-VPN — Treffer, "
                    "weil der Einkäufer überall Varianten desselben Passworts nutzte. MFA war nicht "
                    "aktiv. Innerhalb von zwei Stunden lädt der Angreifer Lieferantenstammdaten "
                    "und Konstruktionszeichnungen herunter. Nach dem Vorfall führt das Unternehmen "
                    "Passwort-Manager, 20-Zeichen-Passphrasen und MFA per Yubikey für alle "
                    "VPN-Zugänge ein. Die Versicherung übernimmt nur 60 Prozent des Schadens, weil "
                    "der Stand der Technik nach Art. 32 DSGVO nicht eingehalten war.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BSI-Empfehlungen *Sichere Passwörter erstellen* (Pressemitteilung "
                    "Januar 2025), BSI IT-Grundschutz-Kompendium Baustein **ORP.4** *Identitäts- und "
                    "Berechtigungsmanagement* (Edition 2023), NIST SP 800-63B *Digital Identity Guidelines* "
                    "sowie Art. 32 DSGVO."
                ),
            ),
            ModulDef(
                titel="Phishing erkennen",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Phishing ist die Methode Nummer eins für Cyberangriffe auf den deutschen "
                    "Mittelstand. Über 90 Prozent aller erfolgreichen Ransomware-Vorfälle "
                    "beginnen mit einer Phishing-Mail. Du lernst, woran du gefälschte Mails, "
                    "Links und Login-Seiten erkennst, welche Maschen besonders gut auf "
                    "Mittelständler abzielen — gefälschte Lieferanten-Rechnungen, CEO-Fraud, "
                    "Microsoft-365-Login-Fallen — und wie du im Zweifel reagierst, ohne dass "
                    "ein einziger Klick reicht, um die Firma lahmzulegen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 32 DSGVO** — Schutz vor unberechtigtem Zugriff durch organisatorische Maßnahmen\n"
                    "- **§ 202a, § 202b, § 263a StGB** — Ausspähen von Daten, Abfangen, Computerbetrug\n"
                    "- **ISO/IEC 27001:2022 Annex A.6.3** — Information security awareness, education and training\n"
                    "- **BSI IT-Grundschutz ORP.3** — Sensibilisierung und Schulung\n\n"
                    "## Was musst du wissen\n\n"
                    "**Phishing** ist der Versuch, dich per gefälschter Mail, SMS oder Anruf dazu "
                    "zu bringen, Zugangsdaten preiszugeben, einen schädlichen Anhang zu öffnen "
                    "oder Geld zu überweisen. Drei Varianten sind im Mittelstand verbreitet:\n\n"
                    "Die **gefälschte Lieferanten-Rechnung** kommt scheinbar vom langjährigen "
                    "Stahllieferanten, hat eine PDF-Anlage mit eingebettetem Makro oder einen "
                    "Link auf eine OneDrive-Seite. Klick aufs PDF startet einen Trojaner, der "
                    "Banking-Zugänge ausliest und Verschlüsselungs-Schadcode nachlädt.\n\n"
                    "Der **CEO-Fraud** (auch *Chef-Masche* oder *Business E-Mail Compromise*) "
                    "kommt scheinbar vom Geschäftsführer an die Buchhaltung: 'Hallo Frau Meier, "
                    "ich bin auf einer wichtigen Verhandlung, brauchen Sie mir bitte 47.000 EUR auf "
                    "folgendes Konto zu überweisen, eilig, melden Sie sich nicht per Telefon.' "
                    "Schäden im Mittelstand: regelmäßig 50.000 bis 500.000 Euro pro Vorfall.\n\n"
                    "Die **gefälschte Microsoft-365-Login-Seite** kommt als Mail 'Ihr Postfach "
                    "läuft über, klicken Sie hier zum Aufräumen'. Der Link führt auf eine "
                    "pixelgenau nachgebaute Login-Maske. Wer Mail-Adresse und Passwort eingibt, "
                    "übergibt beides direkt an den Angreifer. Selbst die MFA-Eingabe wird in "
                    "Echtzeit mitgelesen (*Adversary-in-the-Middle*).\n\n"
                    "Typische Erkennungs-Merkmale einer Phishing-Mail:\n\n"
                    "| Merkmal | Beispiel | Warum verdächtig |\n"
                    "|---|---|---|\n"
                    "| Absenderadresse | rechnung@mueller-stahl.co (statt .de) | Look-alike-Domain |\n"
                    "| Anrede | Sehr geehrter Kunde | Bei echtem Lieferanten kennt man dich namentlich |\n"
                    "| Dringlichkeit | Heute noch! 24 Stunden! Sonst Sperrung! | Druck soll Nachdenken verhindern |\n"
                    "| Rechtschreibung | KI-Mails sind heute fehlerfrei | Fehler-Argument zählt nicht mehr |\n"
                    "| Link-Ziel | Mouseover zeigt fremde Domain | Anker-Text und URL passen nicht zusammen |\n"
                    "| Anhang | Rechnung.pdf.exe oder .zip mit Makro | Doppelte Endung, ungewöhnliches Format |\n"
                    "| Antwort-Adresse | reply-to weicht vom Absender ab | Antworten landen woanders |\n\n"
                    "**KI-gestütztes Phishing** hat seit 2024 die Spielregeln verändert: Rechtschreib"
                    "fehler sind verschwunden, der Tonfall passt zur Branche, die Mail nimmt Bezug "
                    "auf echte Projekte aus LinkedIn. Verlass dich nicht mehr auf 'die Mail klingt "
                    "komisch' — prüfe immer Absender und Links technisch.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor jedem Klick auf einen Link mit der Maus drüberfahren, das echte Link-Ziel unten links im Browser ablesen\n"
                    "2. Bei Zahlungsaufforderungen vom Chef oder einem Lieferanten immer per separatem Kanal rückversichern (Telefonanruf an die bekannte Nummer, nicht an die in der Mail)\n"
                    "3. Anhänge nur öffnen, wenn du sie erwartest — bei Zweifel die IT vor dem Öffnen fragen\n"
                    "4. Niemals Mail-Adresse plus Passwort auf einer Seite eingeben, die du nicht selbst über Lesezeichen oder direkte URL aufgerufen hast\n"
                    "5. Verdächtige Mails NICHT löschen, sondern an die IT (z. B. phishing@firma.de) weiterleiten — die forensische Auswertung hilft, weitere Kollegen zu schützen\n"
                    "6. Wenn du gerade trotzdem geklickt oder Daten eingegeben hast: SOFORT die IT informieren, Passwort ändern, betroffenes Konto sperren lassen — Zeit ist Schaden\n\n"
                    "## Praxisbeispiel\n\n"
                    "Die Buchhaltung eines Automotive-Zulieferers bekommt freitags um 16:45 Uhr "
                    "eine Mail vom Geschäftsführer, der laut Footer 'unterwegs im Auto' schreibt: "
                    "ein neuer chinesischer Lieferant brauche dringend eine Anzahlung von 38.000 "
                    "Euro, das Konto stehe in der Anlage, die Überweisung müsse heute raus sonst "
                    "platze der Deal. Die Sachbearbeiterin will am Telefon rückfragen, der echte "
                    "Geschäftsführer ist aber im Flugzeug nicht erreichbar. Statt wie früher zu "
                    "überweisen, ruft sie laut Vier-Augen-Prozess die Assistenz des Geschäfts"
                    "führers an. Die bestätigt: keine solche Anweisung, der Chef ist seit Tagen "
                    "im Inland. Die Mail wird an die IT eskaliert. Forensik ergibt: Absender war "
                    "*geschaeftsfuehrung@firma-zulieferer.com* statt *.de*, der echte Footer kam "
                    "aus der LinkedIn-Signatur. Der Vorfall wird im nächsten Newsletter anonymisiert "
                    "geteilt, alle Kollegen sind sensibilisiert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BSI-Themenseite *Spam, Phishing & Co.*, BSI-Lagebericht "
                    "zur IT-Sicherheit in Deutschland 2024, BSI IT-Grundschutz-Kompendium Baustein "
                    "**ORP.3** *Sensibilisierung und Schulung* (Edition 2023) sowie "
                    "Polizeiliche Kriminalprävention der Länder und des Bundes *Phishing-Radar*."
                ),
            ),
            ModulDef(
                titel="Mobiles Arbeiten & BYOD",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Außendienstmonteure mit dem Werkstatt-Notebook im Hotel-WLAN, der Vertrieb "
                    "mit dem privaten iPhone für Firmenmails, der Geschäftsführer mit seinem "
                    "MacBook im Café — mobiles Arbeiten ist heute Alltag im Mittelstand, "
                    "vergrößert aber die Angriffsfläche der Firma erheblich. Du lernst, welche "
                    "Regeln für Firmen-Geräte unterwegs gelten, was *Bring Your Own Device* "
                    "(**BYOD**) bedeutet und welche Vorsichtsmaßnahmen unverzichtbar sind, wenn "
                    "Firmendaten das geschützte Firmennetz verlassen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Art. 32 DSGVO** — angemessene technische Maßnahmen, auch außerhalb der Firma\n"
                    "- **§ 26 BDSG** — Beschäftigtendatenschutz auch bei privaten Geräten\n"
                    "- **ISO/IEC 27001:2022 Annex A.6.7 + A.8.1** — Remote working und User endpoint devices\n"
                    "- **BSI IT-Grundschutz OPS.1.2.5** — Fernwartung (für Remote-Zugriffe)\n"
                    "- **BSI IT-Grundschutz SYS.3.2.1** — Mobile Devices, allgemeine Anforderungen\n\n"
                    "## Was musst du wissen\n\n"
                    "Unterwegs gelten dieselben Datenschutz-Pflichten wie im Büro — nur unter "
                    "schlechteren Bedingungen. Offene WLANs in Hotels, Cafés und Flughäfen sind "
                    "potenzielle **Man-in-the-Middle-Fallen**: ein Angreifer im selben WLAN kann "
                    "deinen unverschlüsselten Traffic mitlesen oder gefälschte Hotspots betreiben "
                    "(*Evil Twin*). Pflicht ist deshalb immer **VPN**: dein Notebook baut zuerst "
                    "einen verschlüsselten Tunnel ins Firmennetz auf, dann erst läuft Surfen, Mail, "
                    "Cloud darüber.\n\n"
                    "**BYOD** (Bring Your Own Device) bezeichnet die geschäftliche Nutzung privater "
                    "Smartphones, Tablets oder Laptops. Im Mittelstand verbreitet, weil bequem — "
                    "rechtlich aber anspruchsvoll. Ohne klare Regelung verschwimmen Privates und "
                    "Firmendaten, im Schadensfall haftet der Arbeitgeber für Datenschutzverstöße, "
                    "kann aber das Privatgerät nicht ohne Weiteres durchsuchen oder löschen.\n\n"
                    "Was Firmen-Geräte unterwegs zwingend brauchen:\n\n"
                    "| Maßnahme | Zweck | Konkret |\n"
                    "|---|---|---|\n"
                    "| Festplatten-Verschlüsselung | Schutz bei Diebstahl | BitLocker, FileVault, LUKS aktiviert |\n"
                    "| Bildschirm-Sperre | Schutz im Café | automatisch nach 5 Min, Passwort beim Aufwachen |\n"
                    "| VPN | Schutz im fremden WLAN | Pflicht, bevor Mail oder Cloud genutzt wird |\n"
                    "| MDM | Fernlöschung bei Verlust | zentrale Verwaltung durch die IT |\n"
                    "| aktuelle Updates | Schutz vor bekannten Lücken | nicht aufschieben, regelmäßig neu starten |\n"
                    "| Endpoint-Schutz | Schutz vor Malware | Antivirus + EDR, niemals deaktivieren |\n\n"
                    "**Sichtschutz** ist die einfachste Maßnahme: im ICE oder im Café sieht der "
                    "Sitznachbar auf einem 15-Zoll-Bildschirm Kundenstammdaten, Konstruktionsdaten "
                    "oder Lohnzahlen. Eine **Privacy-Folie** (Blickschutz) macht den Bildschirm "
                    "von der Seite unleserlich und kostet 20 Euro. Im offenen Großraum, in der "
                    "Bahn und im Flugzeug ist sie Pflicht.\n\n"
                    "**Werkstatt-Außendienst** hat eigene Risiken: Notebooks und Tablets liegen im "
                    "Servicewagen, kommen mit Öl und Spänen in Berührung, werden zwischen Kunden "
                    "weitergereicht. Hier gilt zusätzlich: Gerät niemals im Fahrzeug sichtbar "
                    "liegen lassen (Einbruchsmagnet), nach jedem Kundeneinsatz Bildschirm sperren, "
                    "USB-Sticks vom Kunden niemals direkt einstecken — die IT prüft sie zentral.\n\n"
                    "Bei **Verlust oder Diebstahl** zählt jede Minute. Eine Fernsperre und "
                    "Fernlöschung über das **MDM** (Mobile Device Management) ist nur wirksam, "
                    "wenn das Gerät noch eingeschaltet ist und Netz hat. Spätestens nach 24 Stunden "
                    "muss zusätzlich eine Datenschutz-Meldung nach Art. 33 DSGVO geprüft werden.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Im fremden WLAN immer zuerst das Firmen-VPN starten, dann erst Mail und Cloud aufrufen\n"
                    "2. Notebook beim Verlassen des Platzes immer sperren — Win+L, Cmd+Ctrl+Q, kein 'nur kurz weg'\n"
                    "3. Sichtschutzfolie nutzen, sobald du in der Bahn, im Flieger oder im Café arbeitest\n"
                    "4. Firmendaten ausschließlich in den vom Arbeitgeber freigegebenen Speichern ablegen, niemals auf private Cloud-Konten oder Wechseldatenträger\n"
                    "5. Fremde USB-Sticks, SD-Karten oder Ladekabel niemals an Firmen-Geräte anstecken — Kundengeräte über die IT freigeben lassen\n"
                    "6. Bei Verlust, Diebstahl oder Verdacht auf Kompromittierung: SOFORT die IT-Notfallnummer anrufen, auch nachts und am Wochenende\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Servicemonteur eines Maschinenbauers reist montags zu einem Kunden in "
                    "Polen. Im Hotel-WLAN öffnet er reflexartig sein Mail-Programm, das VPN ist "
                    "noch nicht gestartet. Eine als Microsoft-365-Sicherheitswarnung getarnte "
                    "Phishing-Seite öffnet sich in einem Tab, er gibt Zugangsdaten und MFA-Code "
                    "ein. Eine Stunde später laufen Anmelde-Versuche an seinem Konto aus drei "
                    "Ländern. Die EDR-Software meldet die Auffälligkeit, die IT sperrt das Konto, "
                    "das Notebook wird remote in Quarantäne genommen. Schaden: zwei Tage Stillstand "
                    "des Monteurs, vier Stunden Forensik, neue Hardware. Konsequenz im Unternehmen: "
                    "VPN wird per MDM als *Always-On* konfiguriert, Phishing-resistente Hardware-"
                    "Tokens (Yubikey) ersetzen die TOTP-App. Beim nächsten ähnlichen Versuch ein "
                    "halbes Jahr später kann der Angreifer mit den geklauten Daten nichts anfangen, "
                    "weil der zweite Faktor an die richtige Domain gebunden ist.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BSI IT-Grundschutz-Kompendium Baustein **SYS.3.2.1** "
                    "*Mobile Devices* und **OPS.1.2.5** *Fernwartung* (Edition 2023), "
                    "ISO/IEC 27001:2022 Annex A.6.7 (Remote working) und A.8.1 (User endpoint devices) "
                    "sowie Art. 32 DSGVO."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was empfiehlt das BSI seit 2020 (bestätigt 2025) zum Passwort-Wechsel-Rhythmus?",
                erklaerung="Das BSI hat das anlassunabhängige Wechseln als kontraproduktiv eingestuft "
                "— es führt zu schwächeren Passwörtern. Gewechselt wird nur noch bei konkretem Verdacht.",
                optionen=_opts(
                    ("Monatlich", False),
                    ("Alle 90 Tage wie früher in ISO 27001", False),
                    ("Nur bei konkretem Verdacht auf Kompromittierung", True),
                    ("Alle 6 Monate", False),
                ),
            ),
            FrageDef(
                text="Welche Mindestlänge empfiehlt das BSI für eine Passphrase mit nur zwei Zeichenarten?",
                erklaerung="20-25 Zeichen mit zwei Zeichenarten sind laut BSI ähnlich stark wie ein "
                "kurzes komplexes Passwort mit vier Zeichenarten — bei besserer Merkbarkeit.",
                optionen=_opts(
                    ("8 Zeichen", False),
                    ("12 Zeichen", False),
                    ("16 Zeichen", False),
                    ("20-25 Zeichen", True),
                ),
            ),
            FrageDef(
                text="Welche Norm beschreibt im BSI IT-Grundschutz das Identitäts- und Berechtigungsmanagement?",
                erklaerung="Der Baustein ORP.4 (Organisation und Personal) deckt Identitäts- und "
                "Berechtigungsmanagement ab, inklusive Passwort- und Authentifizierungs-Anforderungen.",
                optionen=_opts(
                    ("ORP.4 Identitäts- und Berechtigungsmanagement", True),
                    ("SYS.3.2.1 Mobile Devices", False),
                    ("OPS.1.2.5 Fernwartung", False),
                    ("CON.2 Datenschutz", False),
                ),
            ),
            FrageDef(
                text="Welcher zweite Faktor gilt als phishing-resistent?",
                erklaerung="FIDO2/WebAuthn-Hardware-Token (Yubikey, Titan, Passkeys) sind an die "
                "Domain gebunden und können von gefälschten Login-Seiten nicht abgegriffen werden.",
                optionen=_opts(
                    ("SMS-Code", False),
                    ("E-Mail-Code", False),
                    ("FIDO2/WebAuthn-Hardware-Token bzw. Passkey", True),
                    ("Sicherheitsfrage", False),
                ),
            ),
            FrageDef(
                text="Du erhältst eine Mail vom Geschäftsführer, der dich bittet, 42.000 EUR an einen neuen Lieferanten zu überweisen — eilig, bitte keine Rückfrage. Was tust du?",
                erklaerung="CEO-Fraud lebt von Zeitdruck und Geheimhaltung. Pflicht ist immer eine "
                "Rückbestätigung über einen separaten, verifizierten Kanal (Anruf an die bekannte Nummer).",
                optionen=_opts(
                    ("Überweisen, der Chef wird wissen warum", False),
                    ("Per Antwort-Mail beim Chef rückfragen", False),
                    ("Anruf an die bekannte Telefonnummer des Geschäftsführers — niemals an die Nummer aus der Mail", True),
                    ("Eine Woche warten, dann überweisen", False),
                ),
            ),
            FrageDef(
                text="Wie erkennst du, wohin ein Link in einer Mail wirklich führt — bevor du klickst?",
                erklaerung="Mit der Maus darüberfahren (ohne Klicken) zeigt im Browser oder Mail-Programm "
                "unten links das tatsächliche Link-Ziel. Im Handy: lang draufdrücken (ohne loszulassen).",
                optionen=_opts(
                    ("Mit der Maus darüberfahren und das Ziel unten links ablesen", True),
                    ("Auf den Link klicken und schnell wieder schließen", False),
                    ("Den Anker-Text laut vorlesen", False),
                    ("Den Absender googeln", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu Passwort-Managern stimmt?",
                erklaerung="Ein Passwort-Manager generiert lange Zufallspasswörter, speichert sie "
                "verschlüsselt und füllt sie automatisch aus — ein einziges Master-Passwort plus MFA "
                "schützt den gesamten Tresor.",
                optionen=_opts(
                    ("Passwort-Manager sind unsicher, weil alle Passwörter an einem Ort liegen", False),
                    ("Browser-gespeicherte Passwörter sind genauso sicher wie ein dedizierter Manager", False),
                    ("Sie erlauben für jeden Dienst ein eigenes starkes Zufallspasswort bei nur einem zu merkenden Master-Passwort", True),
                    ("Sie ersetzen die Notwendigkeit von MFA", False),
                ),
            ),
            FrageDef(
                text="Du gibst auf einer Phishing-Seite versehentlich Mail-Adresse und Passwort ein. Was ist deine erste Pflicht?",
                erklaerung="Zeit ist Schaden: je früher die IT informiert ist, desto schneller kann "
                "das Konto gesperrt und das Passwort zurückgesetzt werden, bevor der Angreifer es nutzt.",
                optionen=_opts(
                    ("Erst mal abwarten, vielleicht passiert nichts", False),
                    ("Sofort die IT informieren und das Passwort ändern", True),
                    ("Den Browser-Cache löschen und weiterarbeiten", False),
                    ("Das Passwort beim nächsten regulären Wechsel ersetzen", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet die Abkürzung BYOD?",
                erklaerung="BYOD = Bring Your Own Device. Geschäftliche Nutzung privater Geräte "
                "(Smartphone, Tablet, Laptop). Rechtlich anspruchsvoll wegen vermischter Datenhoheit.",
                optionen=_opts(
                    ("Backup Your Office Data", False),
                    ("Bring Your Own Device — geschäftliche Nutzung privater Geräte", True),
                    ("Business Year Operation Disclosure", False),
                    ("Build Your Online Defence", False),
                ),
            ),
            FrageDef(
                text="Warum ist die Nutzung des Firmen-VPN im Hotel-WLAN Pflicht?",
                erklaerung="Offene WLANs erlauben Man-in-the-Middle-Angriffe — Mitlesen oder gefälschte "
                "Hotspots (Evil Twin). VPN verschlüsselt den Tunnel ins Firmennetz und schützt davor.",
                optionen=_opts(
                    ("VPN ist schneller als das Hotel-WLAN", False),
                    ("VPN umgeht die Hotel-Filterregeln", False),
                    ("VPN verschlüsselt den Verkehr und schützt vor Mithören und Evil-Twin-Hotspots", True),
                    ("VPN spart Mobilfunk-Datenvolumen", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Maßnahmen ist KEINE empfohlene Vorkehrung für Firmen-Notebooks unterwegs?",
                erklaerung="Endpoint-Schutz (Antivirus, EDR) ist Pflicht, nicht optional. Festplatten"
                "verschlüsselung, automatische Bildschirm-Sperre und VPN gehören ebenfalls zum Standard.",
                optionen=_opts(
                    ("Festplatten-Verschlüsselung mit BitLocker oder FileVault", False),
                    ("Bildschirm-Sperre automatisch nach 5 Minuten", False),
                    ("Endpoint-Schutz dauerhaft deaktivieren, um Updates schneller zu machen", True),
                    ("VPN vor Nutzung fremder WLANs starten", False),
                ),
            ),
            FrageDef(
                text="Eine Mail kommt scheinbar von deinem langjährigen Lieferanten, hat aber die Endung .co statt .de. Was ist das?",
                erklaerung="Eine Look-alike-Domain: optisch ähnlich zur echten, aber von Angreifern "
                "registriert. Klassische Methode für gefälschte Lieferanten-Rechnungen und CEO-Fraud.",
                optionen=_opts(
                    ("Eine harmlose Tippvariante ohne Bedeutung", False),
                    ("Eine Look-alike-Domain — Verdacht auf Phishing oder Lieferantenfälschung", True),
                    ("Eine internationale Variante des Lieferanten für Exportgeschäfte", False),
                    ("Eine versehentlich falsch konfigurierte Mailserver-Domain", False),
                ),
            ),
            FrageDef(
                text="Welcher Faktor zählt im Sinne der Multi-Faktor-Authentifizierung NICHT als eigenständiger zweiter Faktor zusätzlich zu deinem Passwort?",
                erklaerung="MFA verlangt einen unabhängigen zweiten Faktor (Besitz oder Inhärenz). "
                "Eine Sicherheitsfrage ist 'Wissen' — derselbe Faktor wie das Passwort, daher kein "
                "echter zweiter Faktor.",
                optionen=_opts(
                    ("Smartphone-App mit TOTP-Code", False),
                    ("Hardware-Token (Yubikey)", False),
                    ("Sicherheitsfrage 'Mädchenname der Mutter'", True),
                    ("Fingerabdruck-Scanner", False),
                ),
            ),
            FrageDef(
                text="Welcher Mindeststandard gilt nach Art. 32 DSGVO für die Authentisierung beim Zugriff auf personenbezogene Daten?",
                erklaerung="Art. 32 DSGVO verlangt 'angemessene Maßnahmen nach dem Stand der Technik'. "
                "Aktuell heißt das: starkes Passwort plus MFA, mindestens für administrative und "
                "extern erreichbare Zugänge.",
                optionen=_opts(
                    ("8-stelliges numerisches Passwort", False),
                    ("Starkes Passwort plus Multi-Faktor-Authentifizierung nach Stand der Technik", True),
                    ("Reine Mail-Bestätigung", False),
                    ("Klartext-Passwort, regelmäßig per Mail versendet", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege fragt dich nach deinem Passwort, weil er für dich einen Vorgang im System abschließen will. Wie reagierst du?",
                erklaerung="Passwörter sind grundsätzlich persönlich. Auch IT, Vorgesetzte und Kollegen "
                "haben kein Recht auf dein Passwort. Vertretungen werden über eigene Konten oder "
                "Berechtigungen gelöst.",
                optionen=_opts(
                    ("Ihm das Passwort nennen, kurz ist okay", False),
                    ("Ihm das Passwort per Chat schicken", False),
                    ("Ablehnen — Passwörter sind persönlich; bei Bedarf Vertretung über die IT klären", True),
                    ("Ein einfacheres Passwort als Vertretung mitteilen", False),
                ),
            ),
            FrageDef(
                text="Du findest auf dem Firmenparkplatz einen USB-Stick mit Aufschrift 'Gehälter 2025'. Was tust du?",
                erklaerung="Klassischer USB-Drop-Angriff: präparierte Sticks werden absichtlich verloren, "
                "Neugier öffnet sie, Schadcode startet automatisch. Nie einstecken — abgeben bei der IT.",
                optionen=_opts(
                    ("Am eigenen PC einstecken, um den Besitzer zu finden", False),
                    ("Nicht einstecken, sondern bei der IT abgeben", True),
                    ("Inhalt erst auf einem Privatgerät prüfen", False),
                    ("Wegwerfen, damit nichts passiert", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu Phishing-Mails mit guter Rechtschreibung stimmt heute (2025)?",
                erklaerung="KI-gestütztes Phishing erzeugt seit 2024 fehlerfreie, kontextgenaue Mails. "
                "Das Argument 'die Mail ist fehlerfrei, also echt' ist veraltet — technische Prüfung "
                "von Absender und Links ist Pflicht.",
                optionen=_opts(
                    ("Fehlerfreie Mails sind immer echt — Angreifer machen immer Tippfehler", False),
                    ("KI-generiertes Phishing ist seit 2024 fehlerfrei; Rechtschreibung ist kein verlässliches Erkennungsmerkmal mehr", True),
                    ("Nur Mails mit Anhang können Phishing sein", False),
                    ("Mails von .de-Domains sind grundsätzlich unbedenklich", False),
                ),
            ),
            FrageDef(
                text="Dein Firmen-Notebook wird auf einer Dienstreise gestohlen. Welche Sofortmaßnahme ist die wichtigste?",
                erklaerung="Sofortmeldung an die IT — diese kann das Gerät per MDM remote sperren oder "
                "löschen (solange es noch online ist) und betroffene Konten sperren. Außerdem ist nach "
                "Art. 33 DSGVO ggf. eine 72-Stunden-Meldung an die Aufsichtsbehörde zu prüfen.",
                optionen=_opts(
                    ("Polizei in Ruhe am nächsten Werktag informieren", False),
                    ("Erst die Heimkehr abwarten, dann der IT melden", False),
                    ("Sofort die IT-Notfallnummer anrufen (auch nachts/Wochenende), Konten sperren lassen, Diebstahl bei Polizei anzeigen", True),
                    ("Versuchen, das Gerät per privater Find-My-Device-App selbst zu orten", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'Adversary-in-the-Middle'-Phishing-Attacke?",
                erklaerung="Eine moderne Phishing-Variante, die auch MFA-Codes in Echtzeit mitliest und "
                "an die echte Seite weitergibt. Schützt nur noch phishing-resistente MFA (FIDO2/Passkey).",
                optionen=_opts(
                    ("Ein physischer Lauschangriff im Büro", False),
                    ("Eine Phishing-Seite, die zwischen dir und dem echten Dienst sitzt und auch MFA-Codes mitliest", True),
                    ("Ein DDoS-Angriff auf einen Lieferanten", False),
                    ("Eine Werbeanzeige, die als Mail getarnt ist", False),
                ),
            ),
            FrageDef(
                text="In welcher Reihenfolge gehst du beim Arbeiten im Hotel-WLAN korrekt vor?",
                erklaerung="VPN zuerst — solange kein verschlüsselter Tunnel steht, ist jeder Mail- oder "
                "Cloud-Aufruf für Angreifer im selben WLAN sichtbar.",
                optionen=_opts(
                    ("Mail öffnen, dann VPN starten, dann Cloud", False),
                    ("Cloud öffnen, dann VPN, zuletzt Mail", False),
                    ("VPN starten, dann erst Mail, Cloud und Browser nutzen", True),
                    ("VPN ist im Hotel-WLAN nicht nötig, weil das Hotel selbst verschlüsselt", False),
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
                        "## Worum geht's?\n\n"
                        "Arbeitsschutz ist keine freiwillige Wohltat des Arbeitgebers, sondern "
                        "ein gesetzliches Pflichtenprogramm mit zwei Adressaten: dem Unternehmen "
                        "und dir als Beschäftigte:r. Wer die Pflichten kennt, kann seine Rechte "
                        "einfordern und weiß auch, wann ein Vorgesetzter ihn nicht zu einer "
                        "gefährlichen Handlung zwingen darf. Du lernst, wer im Betrieb welche "
                        "Verantwortung trägt und welche Rolle die Sicherheitsbeauftragten und die "
                        "Fachkraft für Arbeitssicherheit haben.\n\n"
                        "## Rechtsgrundlage\n\n"
                        "- **§ 3 ArbSchG** — Grundpflichten des Arbeitgebers (Maßnahmen treffen, "
                        "Wirksamkeit prüfen, an Veränderungen anpassen)\n"
                        "- **§ 12 ArbSchG** — Pflicht zur Unterweisung bei Einstellung, "
                        "Veränderung, mindestens jährlich\n"
                        "- **§§ 15-17 ArbSchG** — Pflichten der Beschäftigten (Sorgfalt, Meldung, "
                        "Vorschlagsrecht)\n"
                        "- **§ 4 DGUV Vorschrift 1** — Konkretisierung der Unterweisungspflicht\n"
                        "- **§ 22 SGB VII** — Sicherheitsbeauftragte ab 21 Beschäftigten\n"
                        "- **ASiG (Arbeitssicherheitsgesetz)** — Pflicht zur Bestellung einer "
                        "Fachkraft für Arbeitssicherheit und eines Betriebsarztes\n\n"
                        "## Was musst du wissen\n\n"
                        "Der Arbeitgeber trägt nach § 3 ArbSchG die rechtliche Hauptverantwortung. "
                        "Er muss alle Gefährdungen ermitteln, geeignete Schutzmaßnahmen treffen, "
                        "die Wirksamkeit prüfen und das Schutzniveau verbessern, sobald neue "
                        "Erkenntnisse oder Veränderungen es nötig machen. Diese Pflicht ist nicht "
                        "delegierbar — auch wenn der Geschäftsführer Aufgaben an Führungskräfte "
                        "überträgt, bleibt er strafrechtlich verantwortlich.\n\n"
                        "Im Betrieb gibt es drei zentrale Rollen rund um den Arbeitsschutz:\n\n"
                        "| Rolle | Bestellung ab | Aufgabe |\n"
                        "|---|---|---|\n"
                        "| Fachkraft für Arbeitssicherheit (**Sifa**) | jedem Betrieb (ASiG § 5) | berät, prüft Anlagen, untersucht Unfälle |\n"
                        "| Betriebsarzt | jedem Betrieb (ASiG § 2) | arbeitsmedizinische Vorsorge, Beratung |\n"
                        "| Sicherheitsbeauftragte:r (**SiBe**) | ab 21 Beschäftigten (§ 22 SGB VII) | Ansprechpartner im Team, meldet Mängel, ehrenamtlich |\n\n"
                        "Sifa und Betriebsarzt sind beratend tätig, sie haben kein Weisungsrecht "
                        "gegenüber dir. Sicherheitsbeauftragte sind keine Aufseher, sondern "
                        "Kollegen aus der eigenen Schicht, die ein Auge auf Mängel haben und "
                        "diese an die Führungskraft melden.\n\n"
                        "Als Beschäftigte:r hast du eigene Pflichten nach §§ 15-16 ArbSchG: "
                        "Schutzeinrichtungen bestimmungsgemäß verwenden, persönliche Schutzausrüstung "
                        "tragen, Gefahren und Mängel unverzüglich melden, an Unterweisungen "
                        "teilnehmen und die arbeitsmedizinische Vorsorge wahrnehmen.\n\n"
                        "Du hast aber auch ein Recht nach § 17 ArbSchG: bei unmittelbarer "
                        "erheblicher Gefahr darfst du die Arbeit niederlegen, ohne dass dir "
                        "daraus arbeitsrechtliche Nachteile entstehen.\n\n"
                        "## Was musst du tun\n\n"
                        "1. Trage die vorgeschriebene PSA bestimmungsgemäß, auch für kurze Wege\n"
                        "2. Melde Mängel, Beinaheunfälle und Schäden sofort an deine Führungskraft "
                        "oder den Sicherheitsbeauftragten\n"
                        "3. Nimm an der jährlichen Unterweisung und an arbeitsmedizinischen "
                        "Vorsorgeterminen teil\n"
                        "4. Bediene Maschinen nur, wenn du dafür unterwiesen und befugt bist\n"
                        "5. Bei unmittelbarer Gefahr für Leben oder Gesundheit: Arbeit "
                        "niederlegen und die Lage melden (§ 17 ArbSchG)\n\n"
                        "## Praxisbeispiel\n\n"
                        "In einer Metallbau-Halle bemerkt ein Schlosser, dass die Schutzhaube an "
                        "der Tafelschere klemmt und sich nicht mehr automatisch absenkt. Sein "
                        "Vorgesetzter winkt ab: 'Mach erstmal weiter, das reparieren wir Montag.' "
                        "Der Schlosser kennt aber § 16 ArbSchG und das Recht aus § 17. Er stellt "
                        "die Maschine ab, hängt einen Sperrzettel an den Hauptschalter, informiert "
                        "den Sicherheitsbeauftragten der Schicht und dokumentiert den Vorfall im "
                        "Mängelbuch. Die Sifa wird einbezogen, die Schere bleibt bis zur Reparatur "
                        "gesperrt. Hätte er weitergearbeitet und wäre ein Finger zerquetscht "
                        "worden, hätte ihm die Berufsgenossenschaft ein Mitverschulden vorwerfen "
                        "können — und der Geschäftsführer hätte sich wegen fahrlässiger "
                        "Körperverletzung verantworten müssen.\n\n"
                        "## Quelle\n\n"
                        "Inhalte gestützt auf ArbSchG §§ 3-17 (Stand 2025), "
                        "DGUV Vorschrift 1 *Grundsätze der Prävention* (Ausgabe 2014, akt. 2023) "
                        "und ASiG *Arbeitssicherheitsgesetz* (Stand 2024)."
                    ),
                ),
                ModulDef(
                    titel="Gefährdungsbeurteilung",
                    inhalt_md=(
                        "## Worum geht's?\n\n"
                        "Die Gefährdungsbeurteilung ist das Herzstück des deutschen Arbeitsschutzes. "
                        "Sie ist die systematische Antwort auf die Frage: Wo kann an meinem "
                        "Arbeitsplatz jemand zu Schaden kommen, und was tue ich dagegen? Ohne eine "
                        "aktuelle, dokumentierte Gefährdungsbeurteilung ist jede Maschinenanschaffung "
                        "und jede neue Tätigkeit rechtlich angreifbar. Du lernst die sieben "
                        "Schritte der Methode und wie das STOP-Prinzip die Reihenfolge der "
                        "Maßnahmen vorgibt.\n\n"
                        "## Rechtsgrundlage\n\n"
                        "- **§ 5 ArbSchG** — Pflicht zur Beurteilung der Arbeitsbedingungen\n"
                        "- **§ 6 ArbSchG** — Pflicht zur Dokumentation der Ergebnisse\n"
                        "- **§ 3 BetrSichV** — Gefährdungsbeurteilung für Arbeitsmittel und "
                        "überwachungsbedürftige Anlagen\n"
                        "- **§ 6 GefStoffV** — Beurteilung bei Tätigkeiten mit Gefahrstoffen\n"
                        "- **DGUV Information 211-039** — *Gefährdungsbeurteilung — 7-Schritte-Methode*\n\n"
                        "## Was musst du wissen\n\n"
                        "Die Gefährdungsbeurteilung läuft in sieben Schritten nach der "
                        "**BAuA-Methodik**:\n\n"
                        "1. Tätigkeiten erfassen\n"
                        "2. Gefährdungen ermitteln\n"
                        "3. Gefährdungen beurteilen (Schwere x Eintrittswahrscheinlichkeit)\n"
                        "4. Maßnahmen festlegen\n"
                        "5. Maßnahmen umsetzen\n"
                        "6. Wirksamkeit prüfen\n"
                        "7. Fortschreiben und dokumentieren\n\n"
                        "Bei den Maßnahmen gilt das **STOP-Prinzip** — Maßnahmen müssen in dieser "
                        "Reihenfolge bevorzugt werden, je weiter oben, desto wirksamer:\n\n"
                        "| Stufe | Bedeutung | Beispiel |\n"
                        "|---|---|---|\n"
                        "| S | Substitution | Toluol durch Wasserlack ersetzen |\n"
                        "| T | Technische Maßnahmen | Absaugung, Schutzhaube, Lichtgitter |\n"
                        "| O | Organisatorische Maßnahmen | Schichtbegrenzung, Zugangsbeschränkung |\n"
                        "| P | Personenbezogen (PSA) | Schutzbrille, Gehörschutz, Sicherheitsschuhe |\n\n"
                        "PSA ist also die letzte Stufe, nicht die erste. Wer Sicherheit allein "
                        "auf 'Helm und Brille tragen' baut, verstößt gegen das STOP-Prinzip.\n\n"
                        "Typische Gefährdungen in Werkhallen sind nach DGUV Information 211-039 "
                        "elf Gruppen, darunter mechanische Gefährdungen (Quetschen, Stoßen, "
                        "Schneiden), elektrische Gefährdungen, Gefahrstoffe, biologische Belastung, "
                        "Brand- und Explosionsgefahr, thermische Belastung, Lärm und Vibration, "
                        "Strahlung, physische Belastung (Lastenhandhabung), psychische Belastung "
                        "und Arbeitsumgebung (Klima, Beleuchtung, Stolperstellen).\n\n"
                        "In einer typischen Mittelstandshalle sind die Top-Risiken erfahrungsgemäß "
                        "Stolper-, Rutsch- und Sturzunfälle (rund ein Drittel aller meldepflichtigen "
                        "Arbeitsunfälle), gefolgt von Lastenhandhabung (Bandscheibe), Heißarbeiten "
                        "(Funkenflug, UV-Strahlung beim Schweißen) und Lärm an Pressen oder "
                        "spanabhebenden Maschinen.\n\n"
                        "## Was musst du tun\n\n"
                        "1. Lies die Gefährdungsbeurteilung für deinen Arbeitsplatz — sie hängt "
                        "in der Halle oder liegt bei der Schichtleitung aus\n"
                        "2. Befolge die festgelegten Schutzmaßnahmen vollständig, nicht selektiv\n"
                        "3. Melde neue Gefährdungen, die in der Beurteilung noch nicht stehen "
                        "(neue Maschine, neuer Gefahrstoff, veränderter Ablauf)\n"
                        "4. Bringe Vorschläge zur Verbesserung ein — § 17 ArbSchG gibt dir "
                        "ausdrücklich das Vorschlagsrecht\n"
                        "5. Wirke bei der Wirksamkeitsprüfung mit, wenn du dazu eingeladen wirst "
                        "(Begehung mit Sifa, Audit)\n\n"
                        "## Praxisbeispiel\n\n"
                        "Ein Kunststoffverarbeiter erweitert seine Halle um eine neue Spritzguss-"
                        "Maschine. Die Geschäftsführung übersieht zunächst, dass das STOP-Prinzip "
                        "eine neue Gefährdungsbeurteilung verlangt, und kauft erstmal Gehörschutz "
                        "für alle Beschäftigten — die billige Lösung. Die Sifa interveniert: laut "
                        "Schritt drei und vier muss zuerst geprüft werden, ob die Lärmquelle "
                        "selbst reduzierbar ist (T-Stufe), bevor PSA (P-Stufe) zum Tragen kommt. "
                        "Eine Schallschutzkabine kostet einmalig 18.000 Euro, halbiert den "
                        "Lärmpegel und erspart 40 Beschäftigten dauerhaft den Gehörschutz. Das "
                        "Ergebnis wird dokumentiert, die Beurteilung mit Datum unterschrieben, "
                        "die Wirksamkeit ein halbes Jahr später per Messung bestätigt.\n\n"
                        "## Quelle\n\n"
                        "Inhalte gestützt auf ArbSchG §§ 5-6 (Stand 2025), "
                        "BetrSichV § 3 (Stand 2023), "
                        "BAuA-Leitfaden *Gefährdungsbeurteilung im Betrieb* und "
                        "DGUV Information 211-039 *Gefährdungsbeurteilung — 7-Schritte-Methode* "
                        "(Ausgabe 2017)."
                    ),
                ),
                ModulDef(
                    titel="Notfallorganisation",
                    inhalt_md=(
                        "## Worum geht's?\n\n"
                        "Wenn an einer Pressmaschine ein Finger eingeklemmt wird, sind die ersten "
                        "fünf Minuten entscheidend. Niemand hat dann Zeit, eine Telefonliste zu "
                        "suchen oder zu überlegen, wo der Verbandkasten hängt. Die Notfallorganisation "
                        "regelt im Voraus, wer was tut, wer wen ruft und wie der Arbeitsunfall "
                        "danach dokumentiert und gemeldet wird. Du lernst die Pflicht-Einrichtungen "
                        "und den richtigen Ablauf nach einem Unfall.\n\n"
                        "## Rechtsgrundlage\n\n"
                        "- **§ 10 ArbSchG** — Erste Hilfe und sonstige Maßnahmen bei Notfällen\n"
                        "- **§ 24 DGUV Vorschrift 1** — Ersthelfer-Quote und Erste-Hilfe-Material\n"
                        "- **§ 26 DGUV Vorschrift 1** — Pflichtmeldung von Arbeitsunfällen mit "
                        "mehr als drei Tagen Arbeitsunfähigkeit\n"
                        "- **§ 193 SGB VII** — Anzeigepflicht des Unfalls bei der "
                        "Berufsgenossenschaft\n"
                        "- **ASR A4.3** — Erste-Hilfe-Räume, Mittel und Einrichtungen\n\n"
                        "## Was musst du wissen\n\n"
                        "Jeder Betrieb muss eine Notfallorganisation vorhalten, die mindestens "
                        "vier Elemente umfasst:\n\n"
                        "- ausgebildete **Ersthelfer:innen** in ausreichender Zahl\n"
                        "- erreichbares Erste-Hilfe-Material (Verbandkasten DIN 13157 oder 13169)\n"
                        "- Aushang mit Notruf, Ersthelfern und Verbandbuch\n"
                        "- gegebenenfalls einen Erste-Hilfe-Raum (ab 1.000 Beschäftigten oder bei "
                        "besonderer Gefährdung)\n\n"
                        "Die Quote der Ersthelfer ist nach § 24 DGUV Vorschrift 1 geregelt:\n\n"
                        "| Betriebsart | Mindest-Ersthelfer-Quote |\n"
                        "|---|---|\n"
                        "| Verwaltungs- und Handelsbetriebe | 5 % der Beschäftigten |\n"
                        "| Sonstige Betriebe (Industrie) | 10 % der Beschäftigten |\n"
                        "| Kleinbetriebe (2-20 MA) | mindestens eine Person |\n\n"
                        "Die Ausbildung dauert neun Unterrichtseinheiten, die Auffrischung alle "
                        "zwei Jahre ist Pflicht. Bezahlt wird sie vom Arbeitgeber, durchgeführt "
                        "von durch die DGUV ermächtigten Stellen (DRK, ASB, Johanniter, Malteser).\n\n"
                        "Bei einem Arbeitsunfall gilt der Notruf **112** (Feuerwehr/Rettungsdienst) "
                        "und das Schema fünf W (Wo, Was, Wie viele, Welche Verletzungen, Warten "
                        "auf Rückfragen). Wichtig: nie selbst auflegen, der Disponent beendet das "
                        "Gespräch.\n\n"
                        "Jeder Bagatell-Unfall (zum Beispiel ein Schnitt am Finger, der mit einem "
                        "Pflaster versorgt wird) muss in das **Verbandbuch** eingetragen werden. "
                        "Pflichtangaben sind Name, Datum, Uhrzeit, Ort, Hergang und Art der "
                        "Versorgung. Aufbewahrungsdauer: fünf Jahre. Grund: stellt sich später "
                        "eine Wunde als ernsthaft heraus oder kommt es zu einer Berufskrankheit, "
                        "ist das Verbandbuch der Versicherungs-Nachweis gegenüber der "
                        "Berufsgenossenschaft.\n\n"
                        "Bei Arbeitsunfähigkeit von mehr als drei Tagen ist der Unfall innerhalb "
                        "von drei Tagen über die zuständige **Berufsgenossenschaft** anzuzeigen "
                        "(§ 193 SGB VII). Tödliche oder Massenunfälle sind sofort zu melden.\n\n"
                        "## Was musst du tun\n\n"
                        "1. Kenne den Standort der nächsten Verbandkästen und der Notruftafel\n"
                        "2. Kenne die Namen der Ersthelfer:innen deiner Schicht — sie hängen am "
                        "Aushang oder stehen am Spind\n"
                        "3. Bei einem Unfall: Unfallstelle sichern (Maschine ausschalten, "
                        "Absperrung), Notruf 112 nach Schema 5 W, Erste Hilfe durch Ersthelfer, "
                        "Schichtleitung informieren\n"
                        "4. Trage jeden Bagatell-Unfall sofort ins Verbandbuch ein\n"
                        "5. Mache keine eigenen Aussagen zum Unfallhergang an Externe (Versicherung, "
                        "Presse) — das übernimmt die Geschäftsführung\n\n"
                        "## Praxisbeispiel\n\n"
                        "In einer Automotive-Zulieferer-Halle stürzt ein Lagermitarbeiter beim "
                        "Auspacken einer Palette aus knapp zwei Metern Höhe von einer Ameise. Ein "
                        "Kollege ist ausgebildeter Ersthelfer und reagiert nach Schema: er "
                        "schickt einen zweiten Kollegen zum Notruf-Anruf 112, sichert die "
                        "Halsregion des Verletzten mit Decke und stabilen Tüchern, spricht ihn "
                        "bewusst an und hält ihn warm. Parallel wird die Schichtleitung "
                        "informiert, die den Eingangsbereich freihält und die Sifa benachrichtigt. "
                        "Im Verbandbuch wird der Vorfall eingetragen, am nächsten Tag stellt die "
                        "Personalabteilung die Unfallanzeige bei der BG Holz und Metall, die Sifa "
                        "untersucht den Hergang, die Gefährdungsbeurteilung wird ergänzt um eine "
                        "Anseilpflicht bei Arbeiten von der Ameise aus.\n\n"
                        "## Quelle\n\n"
                        "Inhalte gestützt auf ArbSchG § 10 (Stand 2025), "
                        "DGUV Vorschrift 1 §§ 24-26 (Stand 2023), "
                        "ASR A4.3 *Erste-Hilfe-Räume, Mittel und Einrichtungen* (Ausgabe 2022) "
                        "und SGB VII § 193."
                    ),
                ),
            ),
            fragen=(
                FrageDef(
                    text="Wie oft muss eine Pflichtunterweisung nach § 12 ArbSchG mindestens stattfinden?",
                    erklaerung="§ 12 ArbSchG schreibt eine Unterweisung bei Einstellung, "
                    "Tätigkeitswechsel und mindestens einmal jährlich vor.",
                    optionen=_opts(
                        ("Alle drei Jahre", False),
                        ("Mindestens einmal jährlich (§ 12 ArbSchG)", True),
                        ("Nur bei Einstellung", False),
                        ("Nur, wenn ein Unfall passiert ist", False),
                    ),
                ),
                FrageDef(
                    text="Wer trägt nach § 3 ArbSchG die rechtliche Hauptverantwortung für den Arbeitsschutz im Betrieb?",
                    erklaerung="§ 3 ArbSchG benennt eindeutig den Arbeitgeber. Auch wenn er "
                    "Aufgaben überträgt, bleibt die strafrechtliche Verantwortung bei ihm.",
                    optionen=_opts(
                        ("Die Sicherheitsbeauftragten", False),
                        ("Die Fachkraft für Arbeitssicherheit", False),
                        ("Der Arbeitgeber (§ 3 ArbSchG)", True),
                        ("Die Berufsgenossenschaft", False),
                    ),
                ),
                FrageDef(
                    text="Ab wie vielen Beschäftigten muss ein Betrieb Sicherheitsbeauftragte bestellen?",
                    erklaerung="§ 22 SGB VII verlangt Sicherheitsbeauftragte ab regelmäßig mehr "
                    "als 20 Beschäftigten — also ab 21.",
                    optionen=_opts(
                        ("Ab 5 Beschäftigten", False),
                        ("Ab 10 Beschäftigten", False),
                        ("Ab 21 Beschäftigten (§ 22 SGB VII)", True),
                        ("Ab 50 Beschäftigten", False),
                    ),
                ),
                FrageDef(
                    text="Wofür steht die Abkürzung Sifa?",
                    erklaerung="Sifa ist die Kurzform für Fachkraft für Arbeitssicherheit nach "
                    "Arbeitssicherheitsgesetz (ASiG). Sie berät den Arbeitgeber.",
                    optionen=_opts(
                        ("Sicherheitsfachausschuss", False),
                        ("Sicherheits-Inspektor der Berufsgenossenschaft", False),
                        ("Fachkraft für Arbeitssicherheit", True),
                        ("Sicherheitsbeauftragter im Aufsichtsrat", False),
                    ),
                ),
                FrageDef(
                    text="Wofür steht das STOP-Prinzip bei der Auswahl von Schutzmaßnahmen?",
                    erklaerung="Substitution, Technisch, Organisatorisch, Personenbezogen — in "
                    "dieser Reihenfolge. PSA ist die letzte und schwächste Stufe.",
                    optionen=_opts(
                        ("Sicherheit-Tempo-Ordnung-Pausen", False),
                        ("Substitution-Technisch-Organisatorisch-Personenbezogen (PSA)", True),
                        ("Stop-Tempo-Ordnung-Prüfung", False),
                        ("Standard-Tätigkeit-Ordnung-Person", False),
                    ),
                ),
                FrageDef(
                    text="Wie viele Schritte umfasst die Gefährdungsbeurteilung nach der BAuA-/DGUV-Methode?",
                    erklaerung="DGUV Information 211-039 beschreibt die Gefährdungsbeurteilung "
                    "als 7-Schritte-Methode, von der Tätigkeitserfassung bis zur Fortschreibung.",
                    optionen=_opts(
                        ("3 Schritte", False),
                        ("5 Schritte", False),
                        ("7 Schritte (DGUV Information 211-039)", True),
                        ("10 Schritte", False),
                    ),
                ),
                FrageDef(
                    text="Welche Ersthelfer-Quote schreibt § 24 DGUV Vorschrift 1 für Industriebetriebe vor?",
                    erklaerung="In sonstigen Betrieben (Industrie) sind 10 % der Beschäftigten als "
                    "Ersthelfer auszubilden. In Verwaltung/Handel reichen 5 %.",
                    optionen=_opts(
                        ("2 %", False),
                        ("5 % wie in Verwaltungsbetrieben", False),
                        ("10 % der Beschäftigten", True),
                        ("25 %", False),
                    ),
                ),
                FrageDef(
                    text="Du siehst, dass die Schutzhaube an der Tafelschere defekt ist. Was tust du nach § 16 ArbSchG?",
                    erklaerung="§ 16 ArbSchG verpflichtet jede:n Beschäftigte:n, festgestellte "
                    "Gefahren unverzüglich an die Führungskraft oder den SiBe zu melden.",
                    optionen=_opts(
                        ("Vorsichtig weiterarbeiten und am Schichtende Bescheid sagen", False),
                        ("Maschine außer Betrieb nehmen und sofort der Schichtleitung oder dem SiBe melden", True),
                        ("Selbst reparieren, wenn man Werkzeug zur Hand hat", False),
                        ("Den Defekt fotografieren und beim nächsten Audit ansprechen", False),
                    ),
                ),
                FrageDef(
                    text="Dein Vorgesetzter weist dich an, eine Tätigkeit auszuführen, die akut lebensgefährlich ist. Welches Recht hast du?",
                    erklaerung="§ 17 ArbSchG erlaubt dir bei unmittelbarer erheblicher Gefahr, "
                    "die Arbeit niederzulegen, ohne dass dir daraus Nachteile entstehen.",
                    optionen=_opts(
                        ("Du musst die Anweisung trotzdem befolgen", False),
                        ("Du darfst die Arbeit nach § 17 ArbSchG niederlegen, ohne Nachteile befürchten zu müssen", True),
                        ("Du musst die Berufsgenossenschaft anrufen, bevor du etwas tust", False),
                        ("Du musst die Arbeit ausführen und nachträglich Beschwerde einlegen", False),
                    ),
                ),
                FrageDef(
                    text="In welcher Reihenfolge wird ein Notruf nach Schema 5 W abgesetzt?",
                    erklaerung="Wo, Was, Wie viele Verletzte, Welche Verletzungen, Warten auf "
                    "Rückfragen. Nie selbst auflegen — der Disponent beendet das Gespräch.",
                    optionen=_opts(
                        ("Wer-Wann-Warum-Wo-Wie", False),
                        ("Wo-Was-Wie viele-Welche Verletzungen-Warten auf Rückfragen", True),
                        ("Warum-Wo-Was-Wer-Wann", False),
                        ("Wer-Wo-Was-Warum-Welche Hilfe", False),
                    ),
                ),
                FrageDef(
                    text="Du verletzt dich beim Auspacken am Cuttermesser leicht am Finger und versorgst die Wunde mit einem Pflaster. Was tust du danach?",
                    erklaerung="Auch Bagatell-Verletzungen sind nach DGUV Vorschrift 1 ins "
                    "Verbandbuch einzutragen — als Versicherungs-Nachweis für die BG.",
                    optionen=_opts(
                        ("Nichts, ist nur ein Pflaster", False),
                        ("Eintrag ins Verbandbuch — auch bei Bagatell-Verletzungen Pflicht", True),
                        ("Sofort die Berufsgenossenschaft anrufen", False),
                        ("Foto auf dem Schwarzen Brett aushängen, damit andere aufpassen", False),
                    ),
                ),
                FrageDef(
                    text="Bei welcher Arbeitsunfähigkeit muss der Unfall der Berufsgenossenschaft gemeldet werden?",
                    erklaerung="§ 193 SGB VII fordert die Unfallanzeige bei mehr als drei Tagen "
                    "Arbeitsunfähigkeit. Tödliche Unfälle sind sofort zu melden.",
                    optionen=_opts(
                        ("Erst ab einer Woche Arbeitsunfähigkeit", False),
                        ("Bei mehr als drei Tagen Arbeitsunfähigkeit (§ 193 SGB VII)", True),
                        ("Nur bei tödlichen Unfällen", False),
                        ("Nur, wenn die Sifa es ausdrücklich verlangt", False),
                    ),
                ),
                FrageDef(
                    text="Welche Maßnahme entspricht dem STOP-Prinzip in der RICHTIGEN Reihenfolge?",
                    erklaerung="Erst die Lärmquelle reduzieren (T = Technisch), dann Gehörschutz "
                    "(P = Personenbezogen). PSA ist nie der erste Schritt.",
                    optionen=_opts(
                        ("Sofort Gehörschutz an alle ausgeben — fertig", False),
                        ("Erst Schallschutzkabine prüfen (T), dann ggf. Gehörschutz (P)", True),
                        ("Schichtdienst kürzen und Pause verlängern als Erstes", False),
                        ("Beschäftigte mit empfindlichem Gehör versetzen", False),
                    ),
                ),
                FrageDef(
                    text="Was ist der häufigste Unfalltyp in deutschen Werkhallen?",
                    erklaerung="Stolper-, Rutsch- und Sturzunfälle (SRS) machen rund ein Drittel "
                    "aller meldepflichtigen Arbeitsunfälle aus — vor Lastenhandhabung und Maschine.",
                    optionen=_opts(
                        ("Verbrennungen beim Schweißen", False),
                        ("Stolper-, Rutsch- und Sturzunfälle (SRS)", True),
                        ("Vergiftungen durch Gefahrstoffe", False),
                        ("Hochspannungs-Unfälle", False),
                    ),
                ),
                FrageDef(
                    text="Ein Kollege keilt einen Notausgang offen, weil 'frische Luft besser tut'. Wie bewertest du das?",
                    erklaerung="Notausgänge offen zu halten hebt den Brandabschnitt auf — eine "
                    "Ordnungswidrigkeit. Sofort melden und schließen ist die Pflicht aus § 16 ArbSchG.",
                    optionen=_opts(
                        ("Akzeptabel, wenn nur kurz", False),
                        ("Ordnungswidrigkeit — sofort schließen und an Führungskraft/SiBe melden", True),
                        ("Erlaubt, solange Sicht zum Ausgang besteht", False),
                        ("Akzeptabel im Sommer wegen Hitze", False),
                    ),
                ),
                FrageDef(
                    text="Welche Aufgabe hat ein:e Sicherheitsbeauftragte:r (SiBe) NICHT?",
                    erklaerung="SiBe sind ehrenamtliche Kollegen ohne Weisungsrecht. Sie beraten "
                    "und melden Mängel, dürfen aber keine Anweisungen erteilen.",
                    optionen=_opts(
                        ("Sie melden Mängel und Beinaheunfälle", False),
                        ("Sie sind Ansprechpartner für Kollegen", False),
                        ("Sie erteilen Beschäftigten arbeitsrechtliche Weisungen", True),
                        ("Sie unterstützen die Sifa bei Begehungen", False),
                    ),
                ),
                FrageDef(
                    text="Wo findest du die Gefährdungsbeurteilung deines Arbeitsplatzes?",
                    erklaerung="Die Gefährdungsbeurteilung ist nach § 6 ArbSchG zu dokumentieren "
                    "und muss am Arbeitsplatz oder bei der Schichtleitung zugänglich sein.",
                    optionen=_opts(
                        ("Nur bei der Geschäftsführung, nicht für Beschäftigte einsehbar", False),
                        ("Im Aushang an der Halle, bei der Schichtleitung oder im internen Portal", True),
                        ("Nur online bei der Berufsgenossenschaft", False),
                        ("Nur in Schulungsunterlagen, nicht im Original", False),
                    ),
                ),
                FrageDef(
                    text="Du hebst regelmäßig 20-kg-Werkstücke. Welche Maßnahme entspricht dem STOP-Prinzip am besten?",
                    erklaerung="Hebezeuge sind eine T-Maßnahme und schalten die Gefährdung an der "
                    "Quelle aus. Rückenschule (P-Stufe) wäre nur die letzte Option.",
                    optionen=_opts(
                        ("Rückenstützgurt für jeden Beschäftigten", False),
                        ("Hebezeug oder Vakuum-Heber zur Verfügung stellen (T-Stufe)", True),
                        ("Rückenschule als Pflicht-Training", False),
                        ("Beschäftigte zur Vorsicht ermahnen", False),
                    ),
                ),
                FrageDef(
                    text="Eine Kollegin schneidet sich beim Heißarbeiten an einer scharfen Blechkante. Was sind die ersten drei Schritte?",
                    erklaerung="Unfallstelle sichern (Maschine aus), Notruf 112 bzw. Ersthelfer "
                    "rufen, Erste Hilfe leisten. Schichtleitung wird parallel informiert.",
                    optionen=_opts(
                        ("Werkstück erstmal fertigstellen, dann melden", False),
                        ("Unfallstelle sichern, Ersthelfer/Notruf, Erste Hilfe leisten", True),
                        ("Erst Fotos für die Versicherung machen", False),
                        ("Selbst Auto holen und sie zum Arzt fahren", False),
                    ),
                ),
                FrageDef(
                    text="Welche Aussage zur Persönlichen Schutzausrüstung (PSA) ist FALSCH?",
                    erklaerung="PSA ist die letzte Stufe des STOP-Prinzips, nicht die erste. Erst "
                    "müssen Substitution, Technik und Organisation geprüft werden.",
                    optionen=_opts(
                        ("PSA muss vom Arbeitgeber gestellt werden", False),
                        ("PSA ist die erste und wichtigste Schutzmaßnahme — vor allen anderen", True),
                        ("Beschäftigte sind nach § 15 ArbSchG zur Nutzung verpflichtet", False),
                        ("PSA ersetzt keine technischen Schutzmaßnahmen", False),
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
                    "## Worum geht's?\n\n"
                    "Falsches Löschmittel macht Brände schlimmer. Wasser auf Frittierfett "
                    "erzeugt eine meterhohe Stichflamme, Wasser auf brennende Magnesium-Späne "
                    "löst eine Knallgas-Explosion aus. Du lernst, welcher Brand mit welchem "
                    "Löscher zu löschen ist und warum die Klassen-Kennung auf jedem "
                    "Feuerlöscher lebenswichtig ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **DIN EN 2** — Einteilung der Brandklassen A bis F\n"
                    "- **DIN EN 3** — Tragbare Feuerlöscher: Bauart, Kennzeichnung\n"
                    "- **ASR A2.2** — Pflicht zur Ausstattung von Arbeitsstätten mit Feuerlöschern\n"
                    "- **§ 10 ArbSchG** — Arbeitgeber muss Beschäftigte vor Brandgefahren schützen\n\n"
                    "## Was musst du wissen\n\n"
                    "Es gibt fünf Brandklassen, die sich nach dem brennenden Stoff richten. "
                    "Jede Klasse hat geeignete und ungeeignete Löschmittel:\n\n"
                    "| Klasse | Brennstoff | Beispiele | Geeignet | Ungeeignet |\n"
                    "|---|---|---|---|---|\n"
                    "| A | Feste glutbildende Stoffe | Holz, Papier, Textil, Kunststoff | Wasser, Schaum, ABC-Pulver | — |\n"
                    "| B | Flüssigkeiten | Benzin, Diesel, Lacke, Lösemittel | Schaum, CO₂, ABC-Pulver | Wasser |\n"
                    "| C | Gase | Propan, Erdgas, Acetylen | ABC-Pulver, BC-Pulver | Wasser, Schaum |\n"
                    "| D | Metalle | Magnesium, Aluminium-Späne, Lithium | D-Pulver, trockener Sand | Wasser, Schaum, CO₂ |\n"
                    "| F | Speisefette/-öle | Frittierfett, Pflanzenöl | Klasse-F-Löscher, Branddecke | Wasser |\n\n"
                    "Im Industriebetrieb sind die Löscher nach Risiko-Bereich verteilt: "
                    "ABC-Pulver oder Schaum in Büro und Lager, Schaum plus CO₂ in der "
                    "Werkstatt, zusätzlich D-Pulver im CNC-Bereich mit Späne-Sammler, "
                    "CO₂ am Server-Schrank und Klasse-F-Löscher in der Kantine.\n\n"
                    "Wichtige Eigenschaften der Löschmittel:\n\n"
                    "- **CO₂** löscht rückstandsfrei und ist gut für Elektronik, birgt aber "
                    "Erstickungsgefahr in kleinen Räumen und Erfrierungsrisiko an der Düse\n"
                    "- **ABC-Pulver** ist universell einsetzbar, hinterlässt jedoch "
                    "Korrosionsschäden an Elektronik\n"
                    "- **D-Pulver** ist ein Spezialprodukt für Metallbrände und darf "
                    "niemals durch ABC-Pulver ersetzt werden\n\n"
                    "## Was musst du tun\n\n"
                    "Die Bedienung folgt für alle Löschertypen einem festen Schema:\n\n"
                    "1. Sicherung ziehen (Splint oder Plombe)\n"
                    "2. Schlauch greifen, auf den Brand richten\n"
                    "3. Auslöseventil drücken\n"
                    "4. Stoßweise löschen, nicht in einem Zug entleeren\n"
                    "5. Mit dem Wind im Rücken arbeiten, Glut und Wurzeln löschen, nicht nur die Flammen\n"
                    "6. Nach dem Löschen die Brandstelle beobachten, Wiederentzündung ist möglich\n\n"
                    "Bei mehreren Löschern gleichzeitig einsetzen, nicht nacheinander.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Metallverarbeitung gerät die Späne-Sammelwanne an einer "
                    "CNC-Fräse in Brand, weil Magnesium-Späne durch Funkenflug entzündet "
                    "werden. Ein Kollege greift reflexartig zum Wasserlöscher an der Säule. "
                    "Der Wasserstrahl löst eine Knallgas-Reaktion aus, eine kleine Verpuffung "
                    "schleudert brennende Späne meterweit. Richtig wäre der **D-Pulver-Löscher** "
                    "gewesen, der in dieser Halle in zwei Metern Entfernung hängt und in der "
                    "Gefährdungsbeurteilung genau für dieses Szenario vorgesehen ist.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DIN EN 2:2005 *Brandklassen*, "
                    "DGUV Information 205-001 *Arbeitssicherheit durch vorbeugenden Brandschutz* "
                    "und ASR A2.2 *Maßnahmen gegen Brände* (Ausgabe 2022)."
                ),
            ),
            ModulDef(
                titel="Verhalten im Brandfall",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Zimmerbrand erreicht nach zwei bis drei Minuten den Flashover — "
                    "alle Raumgase entzünden sich gleichzeitig, der Raum wird zur Brennkammer. "
                    "Wer in den ersten 60 Sekunden richtig reagiert, rettet meistens alle. "
                    "Du lernst die richtige Reihenfolge und warum 95 Prozent der Brandtoten "
                    "an Rauch sterben, nicht an Verbrennungen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 ArbSchG** — Erste Hilfe und sonstige Maßnahmen bei Notfällen\n"
                    "- **§ 22 DGUV Vorschrift 1** — Pflicht zu Räumungs- und Brandschutzübungen\n"
                    "- **ASR A2.2** — Maßnahmen gegen Brände, Verhalten im Brandfall\n\n"
                    "## Was musst du wissen\n\n"
                    "Die richtige Reihenfolge folgt dem Merksatz **RAMS**:\n\n"
                    "1. **R**uhe bewahren\n"
                    "2. **A**larm auslösen und Notruf 112\n"
                    "3. **M**enschen retten\n"
                    "4. **S**chließen und gegebenenfalls löschen\n\n"
                    "Panik ist der häufigste Tötungsfaktor: falsche Richtung, Aufzug benutzt, "
                    "Türen aufgerissen. Tief atmen, einschätzen wo es brennt, wo Rauch ist, "
                    "wo der Fluchtweg ist und wer in der Nähe ist.\n\n"
                    "**Rauchgas** ist die eigentliche Gefahr. Brandrauch enthält Kohlenmonoxid, "
                    "Cyanwasserstoff, Salzsäure und Phosgen. Drei bis fünf Atemzüge können "
                    "tödlich sein. In Augenhöhe ist die Konzentration meist schon letal, am "
                    "Boden bleibt eine 20 bis 30 Zentimeter dünne Schicht frischer Luft. "
                    "Deshalb gilt im Rauch: kriechen oder tief gebückt gehen.\n\n"
                    "**Türen** sind Brandschutzbarrieren. Eine geschlossene Tür verzögert die "
                    "Rauchausbreitung um rund zehn Minuten und kann eine Stichflamme (Backdraft) "
                    "beim Aufreißen eines Brandraums verhindern. Vor dem Öffnen einer Tür "
                    "immer die Klinke mit dem Handrücken auf Hitze prüfen — ist sie heiß, "
                    "nicht öffnen und einen anderen Fluchtweg suchen.\n\n"
                    "**Löschversuche** sind nur sinnvoll, wenn drei Bedingungen gleichzeitig "
                    "erfüllt sind: dein Fluchtweg bleibt gesichert, es ist ein Entstehungsbrand "
                    "(Flammen klein, nicht über Tischhöhe) und du hast das richtige Löschmittel "
                    "griffbereit. Sonst gilt: raus, Tür zu, auf die Feuerwehr warten.\n\n"
                    "## Was musst du tun\n\n"
                    "Im Brandfall sofort:\n\n"
                    "1. Brandmeldetaster drücken (rote Kästen an Säulen und Wänden, Glas einschlagen)\n"
                    "2. Notruf 112 absetzen, parallel zur Brandmeldeanlage\n"
                    "3. Kollegen warnen, laut rufen und durch betroffene Hallen gehen\n"
                    "4. Türen beim Verlassen schließen\n"
                    "5. Treppe benutzen, niemals den Aufzug\n"
                    "6. Zum Sammelplatz gehen und bei der verantwortlichen Person melden\n\n"
                    "Wertgegenstände bleiben liegen: Notebook, Handy, Tasche sind ersetzbar. "
                    "Wer zurückgeht, gefährdet sich und die Helfer. In ein evakuiertes "
                    "Gebäude darf nur die Feuerwehr zurück.\n\n"
                    "In stark verrauchten Bereichen Atem anhalten, ein Tuch vor Mund und "
                    "Nase, zügig auf maximal 30 Meter durchqueren. Wenn der Weg blockiert "
                    "ist, in einen Raum mit Fenster gehen, Tür schließen, den Türspalt mit "
                    "nasser Kleidung abdichten und am Fenster bemerkbar machen.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Lackiererei rüstet ein Kollege nachmittags Verdünner ein, als "
                    "ein Funke aus einem unsachgemäß abgestellten Schleifgerät einen "
                    "Schwelbrand am Boden auslöst. Er reagiert ruhig: drückt den Brandmelder "
                    "an der Säule, ruft per Funk die Schichtleitung, warnt die zwei Kollegen "
                    "in der Spritzkabine, schließt die Lacktür beim Hinausgehen und sammelt "
                    "alle am vereinbarten Treffpunkt vor Tor 2. Die Feuerwehr findet den "
                    "Brand auf zwei Quadratmeter begrenzt vor — die geschlossene Brandschutztür "
                    "hat die Sauerstoffzufuhr genug gedrosselt, um den Flashover zu verhindern.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Information 205-001 *Arbeitssicherheit durch "
                    "vorbeugenden Brandschutz* und ASR A2.2 *Maßnahmen gegen Brände* "
                    "(Ausgabe 2022). Verhaltensregeln nach den Empfehlungen der "
                    "vfdb (Vereinigung zur Förderung des Deutschen Brandschutzes)."
                ),
            ),
            ModulDef(
                titel="Flucht- und Rettungswege",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Fluchtweg ist der Weg, auf dem du im Notfall ins Freie kommst. "
                    "Ein blockierter oder schlecht gekennzeichneter Fluchtweg kann den "
                    "Unterschied zwischen Evakuierung in zwei Minuten und Toten ausmachen. "
                    "Du lernst, welche Anforderungen Fluchtwege erfüllen müssen, was darauf "
                    "nichts zu suchen hat und was am Sammelplatz passiert.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 4 ArbStättV** — Arbeitsstätten müssen sichere Fluchtwege haben\n"
                    "- **ASR A2.3** — Fluchtwege und Notausgänge: Maße, Kennzeichnung, Beleuchtung\n"
                    "- **§ 16 ArbSchG** — Beschäftigte sind verpflichtet, Gefahren zu melden\n"
                    "- **§ 22 DGUV Vorschrift 1** — Jährliche Räumungsübung\n\n"
                    "## Was musst du wissen\n\n"
                    "Jeder Arbeitsplatz muss mindestens einen Fluchtweg ins Freie haben. "
                    "In normalen Büros darf dieser bis zu 35 Meter lang sein, in Bereichen "
                    "erhöhter Brandgefahr nur 25 Meter. Bei mehr als rund zehn Personen "
                    "oder in größeren Räumen sind zwei voneinander unabhängige Fluchtwege "
                    "Pflicht.\n\n"
                    "Bauliche Anforderungen nach ASR A2.3:\n\n"
                    "| Element | Anforderung |\n"
                    "|---|---|\n"
                    "| Mindestbreite | 1,00 m bis 20 Personen, +0,60 m je weitere 100 |\n"
                    "| Türen | öffnen in Fluchtrichtung, Panik-Schloss ohne Schlüssel |\n"
                    "| Treppenhaus | eigener Brandabschnitt mit T30- oder T90-Türen |\n"
                    "| Kennzeichnung | grünes Rettungszeichen nach DIN EN ISO 7010 |\n"
                    "| Sicherheitsbeleuchtung | mindestens 60 Minuten Notstrom |\n\n"
                    "Brandschutztüren dürfen niemals offen gekeilt werden. Das ist eine "
                    "**Ordnungswidrigkeit** mit Bußgeld bis 50.000 Euro und kann im "
                    "Brandfall Menschenleben kosten, weil eine offene Brandschutztür den "
                    "ganzen Brandabschnitt zunichte macht.\n\n"
                    "Pro Etage sind mindestens fünf Prozent der Beschäftigten als "
                    "**Brandschutzhelfer** ausgebildet (ASR A2.2). Sie kennen die Löscher- "
                    "und Melderpositionen, können Entstehungsbrände bekämpfen und führen "
                    "die Evakuierung ihres Bereichs. Die Schulung dauert mindestens zwei "
                    "Stunden inklusive praktischer Löschübung, Auffrischung alle drei bis "
                    "fünf Jahre.\n\n"
                    "## Was musst du tun\n\n"
                    "Auf Fluchtwegen darf nichts stehen, auch nicht kurzfristig:\n\n"
                    "- Keine Paletten, Kartons, Materialwagen\n"
                    "- Keine Mülltonnen, Stühle, Putzeimer\n"
                    "- Keine abgestellten Stapler oder Hubwagen\n"
                    "- Keine gekeilten Brandschutztüren\n\n"
                    "Wenn du ein Hindernis siehst, räume es weg oder melde es sofort der "
                    "Schichtleitung. Das ist keine Petze, sondern deine gesetzliche Pflicht "
                    "nach § 16 ArbSchG.\n\n"
                    "Bei einem Alarm, auch bei einer Übung:\n\n"
                    "1. Arbeit sofort einstellen, Maschine wenn schnell möglich abschalten\n"
                    "2. Sachen liegen lassen, keine Tasche und kein Notebook\n"
                    "3. Ruhig und zügig zum nächsten Fluchtweg\n"
                    "4. Türen schließen beim Verlassen\n"
                    "5. Zum Sammelplatz gehen, nicht zum Auto\n"
                    "6. Bei der verantwortlichen Person am Sammelplatz melden\n\n"
                    "Das Gebäude betritt niemand wieder, bis die Feuerwehr freigibt — "
                    "auch nicht, um schnell das Handy zu holen.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem Zulieferbetrieb hat sich über Wochen eingebürgert, dass leere "
                    "Paletten vor der Brandschutztür zwischen Lager und Halle zwischen"
                    "gelagert werden — angeblich nur bis zur nächsten Spedition. Bei der "
                    "jährlichen Räumungsübung dauert die Evakuierung der Lagerschicht acht "
                    "Minuten statt der geplanten drei, weil die Stapler über die Paletten "
                    "manövrieren müssen. Die Geschäftsführung zieht Konsequenzen: alle "
                    "Fluchtwege werden mit Bodenmarkierung versehen, das unbefugte Abstellen "
                    "wird arbeitsvertraglich abmahnbar gemacht. Bei der nächsten Übung "
                    "dauert die Evakuierung zwei Minuten zehn Sekunden.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf ArbStättV (Stand 2022), "
                    "ASR A2.3 *Fluchtwege und Notausgänge* (Ausgabe 2022) und "
                    "DGUV Information 205-023 *Brandschutzhelfer*."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Brandklasse beschreibt brennende Metalle wie Magnesium oder Aluminium-Späne?",
                erklaerung="Brandklasse D umfasst Metallbrände. Diese erfordern Spezial-Löschmittel "
                "(D-Pulver oder trockener Sand) — Wasser ist hier lebensgefährlich.",
                optionen=_opts(
                    ("Klasse A (feste glutbildende Stoffe)", False),
                    ("Klasse B (Flüssigkeiten)", False),
                    ("Klasse D (Metalle)", True),
                    ("Klasse F (Speisefette)", False),
                ),
            ),
            FrageDef(
                text="Welches Löschmittel ist auf einem Fettbrand (Klasse F) lebensgefährlich?",
                erklaerung="Wasser verdampft auf 100 °C explosionsartig und schleudert brennendes "
                "Fett meterhoch. Richtig sind Klasse-F-Löscher oder eine dichte Branddecke.",
                optionen=_opts(
                    ("Wasser", True),
                    ("Klasse-F-Löscher", False),
                    ("Branddecke", False),
                    ("CO₂", False),
                ),
            ),
            FrageDef(
                text="Warum ist CO₂ als Löschmittel besonders gut für Server-Räume geeignet?",
                erklaerung="CO₂ verdrängt Sauerstoff und verdampft rückstandslos. Pulver-Löscher "
                "würden Elektronik durch Korrosion zerstören.",
                optionen=_opts(
                    ("Es löscht rückstandsfrei und beschädigt keine Elektronik", True),
                    ("Es ist besonders kalt und kühlt schneller als andere Löschmittel", False),
                    ("Es ist geräuschlos im Einsatz", False),
                    ("Es ist ungiftig und kann unbedenklich eingeatmet werden", False),
                ),
            ),
            FrageDef(
                text="Wo wird ein D-Pulver-Löscher in einer Maschinenbau-Halle typischerweise platziert?",
                erklaerung="D-Pulver ist ein Spezial-Löschmittel für Metallbrände und gehört in "
                "die Nähe von Späne-Sammlern an Magnesium- oder Aluminium-verarbeitenden Maschinen.",
                optionen=_opts(
                    ("In jedem Büro", False),
                    ("In Bereichen mit Magnesium- oder Aluminium-Spänen, z.B. an CNC-Fräsen", True),
                    ("In der Kantine", False),
                    ("Ausschließlich im Server-Raum", False),
                ),
            ),
            FrageDef(
                text="Was passiert, wenn man Wasser auf brennendes Magnesium gibt?",
                erklaerung="Wasser reagiert mit dem brennenden Metall unter Bildung von Wasserstoff "
                "(Knallgas) — eine Explosion ist die Folge.",
                optionen=_opts(
                    ("Der Brand wird effektiv gelöscht", False),
                    ("Es bildet sich Knallgas, eine Explosion droht", True),
                    ("Der Brand erlischt langsam von außen nach innen", False),
                    ("Es entsteht giftiger Rauch ohne weitere Folgen", False),
                ),
            ),
            FrageDef(
                text="Wie löscht man mit einem Pulverlöscher technisch richtig?",
                erklaerung="Stoßweise löschen (nicht in einem Zug entleeren) und mit dem Wind "
                "im Rücken, sonst löscht man sich selbst ein.",
                optionen=_opts(
                    ("In einem Zug entleeren, damit nichts übrig bleibt", False),
                    ("Stoßweise und mit dem Wind im Rücken", True),
                    ("Von oben senkrecht auf die Flammenspitzen", False),
                    ("Mit langsamer kreisender Bewegung von außen nach innen", False),
                ),
            ),
            FrageDef(
                text="Wo sollte ABC-Pulver nach Möglichkeit NICHT eingesetzt werden?",
                erklaerung="Pulver kriecht in jede Ritze und korrodiert Elektronik. Für Server-Räume "
                "ist CO₂ die richtige Wahl.",
                optionen=_opts(
                    ("In der Werkhalle", False),
                    ("Am Server-Schrank wegen Korrosionsschäden an Elektronik", True),
                    ("Im Lager", False),
                    ("Im Freien bei Windstille", False),
                ),
            ),
            FrageDef(
                text="Wofür steht das Akronym RAMS im Brandfall?",
                erklaerung="RAMS gibt die Handlungs-Reihenfolge vor: erst Ruhe, dann Alarm, dann "
                "Menschen retten, dann Schließen und ggf. Löschen.",
                optionen=_opts(
                    ("Rufen-Atmen-Melden-Sichern", False),
                    ("Ruhe-Alarm-Menschen retten-Schließen", True),
                    ("Rauch-Alarm-Maske-Sicherheit", False),
                    ("Retten-Aufzug-Melden-Sammeln", False),
                ),
            ),
            FrageDef(
                text="Woran sterben rund 95 Prozent aller Brandopfer?",
                erklaerung="Rauchgas (CO, Cyanwasserstoff, Phosgen) wirkt schon nach wenigen "
                "Atemzügen tödlich, schneller als die Flammen selbst.",
                optionen=_opts(
                    ("An den Verbrennungen durch die Flammen", False),
                    ("An Rauchgasvergiftung (Kohlenmonoxid und Cyanwasserstoff)", True),
                    ("An Stromschlag durch beschädigte Leitungen", False),
                    ("An Trümmer-Verletzungen durch einstürzende Decken", False),
                ),
            ),
            FrageDef(
                text="Du musst durch einen stark verrauchten Flur. Wie verhältst du dich?",
                erklaerung="Am Boden, in den unteren 20-30 cm, bleibt eine Schicht frischerer Luft. "
                "In Augenhöhe ist die Rauchkonzentration oft schon tödlich.",
                optionen=_opts(
                    ("Atem anhalten und aufrecht rennen", False),
                    ("Tief gebückt oder kriechend bewegen, am Boden ist die Luft besser", True),
                    ("Mund mit Tuch zuhalten und langsam aufrecht gehen", False),
                    ("Augen schließen und sich an der Wand entlang tasten", False),
                ),
            ),
            FrageDef(
                text="Warum darf im Brandfall niemals der Aufzug benutzt werden?",
                erklaerung="Der Aufzugsschacht wirkt wie ein Kamin und zieht Rauch hoch. Bei "
                "Stromausfall bleibt der Aufzug zwischen den Etagen stecken.",
                optionen=_opts(
                    ("Weil er zu langsam ist", False),
                    ("Weil er ausfallen kann und der Schacht wie ein Kamin wirkt", True),
                    ("Weil er die Stromversorgung der Sprinkler blockiert", False),
                    ("Weil das in der Hausordnung verboten ist", False),
                ),
            ),
            FrageDef(
                text="Du stehst vor einer geschlossenen Tür, hinter der du Feuer vermutest. Was tust du?",
                erklaerung="Hinter einer geschlossenen Tür kann sich ein sauerstoffarmer Schwelbrand "
                "halten. Beim Aufreißen schlägt eine Stichflamme (Backdraft) heraus.",
                optionen=_opts(
                    ("Sofort öffnen und mit Löscher angreifen", False),
                    ("Klinke mit Handrücken auf Hitze prüfen, bei Wärme nicht öffnen", True),
                    ("Mehrfach klopfen und horchen, dann öffnen", False),
                    ("Tür einen Spalt öffnen, um zu schauen", False),
                ),
            ),
            FrageDef(
                text="Wann darfst du als Mitarbeiter:in einen Brand selbst löschen?",
                erklaerung="Drei Bedingungen müssen alle gleichzeitig erfüllt sein. Sonst gilt: "
                "raus, Tür zu, Feuerwehr abwarten.",
                optionen=_opts(
                    ("Immer, sobald du einen Löscher griffbereit hast", False),
                    ("Nur wenn Fluchtweg gesichert, Entstehungsbrand und richtiges Löschmittel vorhanden ist", True),
                    ("Nur als ausgebildeter Brandschutzhelfer", False),
                    ("Nur wenn die Feuerwehr nicht erreichbar ist", False),
                ),
            ),
            FrageDef(
                text="Warum sollte man im Brandfall Türen beim Verlassen des Raumes schließen?",
                erklaerung="Eine geschlossene Tür reduziert Sauerstoffzufuhr und Rauchausbreitung. "
                "Sie kann Leben retten — die der Kollegen hinter der Tür.",
                optionen=_opts(
                    ("Damit niemand reingeht und etwas gestohlen wird", False),
                    ("Eine geschlossene Tür verzögert die Rauchausbreitung um rund 10 Minuten", True),
                    ("Damit der Lärm der Sirenen draußen bleibt", False),
                    ("Weil das in der Brandschutzordnung als Pflicht steht", False),
                ),
            ),
            FrageDef(
                text="Welche maximale Fluchtweg-Länge gilt nach ASR A2.3 in normalen Büros?",
                erklaerung="Die Vorgabe ist 35 m. In Bereichen erhöhter Brandgefahr sind es 25 m, "
                "in größeren Räumen mit guter Übersicht kann sie länger sein.",
                optionen=_opts(
                    ("15 m", False),
                    ("25 m", False),
                    ("35 m", True),
                    ("50 m", False),
                ),
            ),
            FrageDef(
                text="Wie sind Fluchtwege gekennzeichnet?",
                erklaerung="DIN EN ISO 7010 normiert das Rettungszeichen: weißes Männchen läuft "
                "durch eine Tür, weißer Pfeil auf grünem Grund.",
                optionen=_opts(
                    ("Rote Pfeile auf weißem Grund", False),
                    ("Grünes Rettungszeichen mit Männchen und Pfeil nach DIN EN ISO 7010", True),
                    ("Blaue Schilder mit weißer Schrift", False),
                    ("Gelbe Punktmarkierung am Boden", False),
                ),
            ),
            FrageDef(
                text="Was sind die rechtlichen Folgen, wenn jemand eine Brandschutztür offen keilt?",
                erklaerung="Eine offene Brandschutztür hebt den ganzen Brandabschnitt auf. "
                "Bußgeld bis 50.000 €, im Schadensfall ist persönliche Haftung möglich.",
                optionen=_opts(
                    ("Keine, das ist eine gängige Praxis", False),
                    ("Ordnungswidrigkeit mit Bußgeld bis 50.000 € und Aufhebung des Brandschutz-Konzepts", True),
                    ("Nur in öffentlichen Gebäuden verboten", False),
                    ("Erlaubt, solange Material durchgetragen wird", False),
                ),
            ),
            FrageDef(
                text="Du siehst eine abgestellte Palette mitten auf dem Fluchtweg. Was ist deine Pflicht?",
                erklaerung="§ 16 ArbSchG verpflichtet jede:n Beschäftigte:n, Gefahren unverzüglich "
                "zu melden — oder selbst zu beseitigen, wenn das ohne Gefährdung möglich ist.",
                optionen=_opts(
                    ("Vorbeigehen, ist nicht dein Bereich", False),
                    ("Wegräumen wenn möglich oder sofort an die Schichtleitung melden (§ 16 ArbSchG)", True),
                    ("Nur melden, wenn die Palette groß ist", False),
                    ("Fotografieren und am nächsten Tag im Teammeeting ansprechen", False),
                ),
            ),
            FrageDef(
                text="Wofür ist der Sammelplatz nach einer Evakuierung da?",
                erklaerung="Am Sammelplatz wird per Anwesenheitsliste geprüft, wer fehlt. Diese "
                "Information bekommt die Feuerwehr, damit gezielt gesucht werden kann.",
                optionen=_opts(
                    ("Pflicht-Raucherpause während der Evakuierung", False),
                    ("Damit Verantwortliche prüfen können, wer noch im Gebäude vermisst wird", True),
                    ("Wartebereich für Angehörige der Mitarbeitenden", False),
                    ("Treffpunkt für die Feuerwehr zum Abladen der Schläuche", False),
                ),
            ),
            FrageDef(
                text="Welcher Anteil der Beschäftigten muss pro Brandabschnitt als Brandschutzhelfer ausgebildet sein?",
                erklaerung="ASR A2.2 fordert mindestens 5 % — bei besonderen Risiken auch mehr. "
                "Brandschutzhelfer sind die Erstmaßnahme vor dem Eintreffen der Feuerwehr.",
                optionen=_opts(
                    ("Nur die Geschäftsführung", False),
                    ("Mindestens 5 % der Beschäftigten pro Brandabschnitt (ASR A2.2)", True),
                    ("Nur das eigene Sicherheitspersonal", False),
                    ("Nur freiwillige Feuerwehrleute aus der Belegschaft", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #5
    KursDef(
        titel="Erste Hilfe — Auffrischung",
        beschreibung="Auffrischung nach DGUV Vorschrift 1 § 26. "
        "Notruf, Bewusstlosigkeit, Wiederbelebung, Wundversorgung.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Notruf-Schema 5 W",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Wenn in der Werkhalle jemand schwer verletzt zusammenbricht — "
                    "eingequetscht zwischen Werkstück und Spannvorrichtung, abgestürzt "
                    "von der Leiter, Stromschlag am Schaltschrank — entscheidet die "
                    "erste Minute. In dieser Minute musst du den Rettungsdienst "
                    "alarmieren, ohne wichtige Informationen zu vergessen. Das "
                    "Notruf-Schema **5 W** ist die Gedankenstütze, mit der du auch "
                    "unter Adrenalin alle relevanten Angaben in der richtigen "
                    "Reihenfolge an die Leitstelle gibst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 ArbSchG** — Arbeitgeber muss Erste Hilfe und Notfallmaßnahmen organisieren\n"
                    "- **§ 24 DGUV Vorschrift 1** — Erste-Hilfe-Material, Meldeeinrichtungen, Rettungstransport\n"
                    "- **§ 25 DGUV Vorschrift 1** — Aushänge zur Ersten Hilfe gut sichtbar anbringen\n"
                    "- **§ 323c StGB** — Unterlassene Hilfeleistung ist Straftat\n\n"
                    "## Was musst du wissen\n\n"
                    "Der Notruf in Deutschland und in der ganzen EU lautet **112** "
                    "(Feuerwehr und Rettungsdienst). Die Nummer ist kostenlos, "
                    "ohne Vorwahl und auch aus dem Festnetz, vom Werktelefon und "
                    "vom Handy ohne SIM-Karte erreichbar.\n\n"
                    "Das 5-W-Schema gibt dir die Struktur für das Telefonat:\n\n"
                    "| Frage | Was du sagst |\n"
                    "|---|---|\n"
                    "| Wo ist es passiert? | Adresse, Halle, Stockwerk, Tor — möglichst genau |\n"
                    "| Was ist passiert? | Art des Notfalls in einem kurzen Satz |\n"
                    "| Wie viele Verletzte? | Zahl der betroffenen Personen |\n"
                    "| Welche Verletzungen? | Sichtbare Schäden, Bewusstsein, Atmung |\n"
                    "| Warten auf Rückfragen | Niemals zuerst auflegen |\n\n"
                    "Die Leitstelle lässt dich nicht auflegen, sondern fragt nach. "
                    "Sie kann über ihr System parallel zum Gespräch bereits das "
                    "nächstgelegene Rettungsmittel auslösen. Auflegen verlierst du "
                    "die Verbindung — und damit auch Hinweise zur weiteren Erstversorgung, "
                    "die der Disponent dir am Telefon geben kann (Rea-Anleitung, "
                    "Blutstillung, stabile Seitenlage).\n\n"
                    "Eine besondere Rolle in jedem Betrieb spielt der **Ersthelfer** "
                    "oder die **Ersthelferin**. Nach DGUV Vorschrift 1 § 26 Abs. 2 "
                    "muss der Arbeitgeber je nach Betriebsart mindestens 5 Prozent "
                    "(Verwaltungs- und Handelsbetriebe) bzw. 10 Prozent (sonstige "
                    "Betriebe, also auch produzierendes Gewerbe) der anwesenden "
                    "Beschäftigten als Ersthelfer ausbilden lassen. Die Auffrischung "
                    "ist alle zwei Jahre Pflicht — wer die Frist überschreitet, "
                    "verliert den Status und muss die volle Grundausbildung von "
                    "neun Unterrichtseinheiten erneut absolvieren.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du Zeuge oder Zeugin eines Notfalls wirst:\n\n"
                    "1. Ruhig bleiben und Unfallstelle absichern (Maschine ausschalten, Stromzufuhr unterbrechen)\n"
                    "2. Verletzten ansprechen, auf Atmung und Bewusstsein prüfen\n"
                    "3. Notruf 112 absetzen oder durch Kollegin absetzen lassen\n"
                    "4. Beim Telefonat ruhig und langsam sprechen, die 5 W beantworten\n"
                    "5. Bei der Verletzten bleiben, betreuen und gegebenenfalls Erste Hilfe leisten\n"
                    "6. Den Rettungsdienst am Tor einweisen, damit er keine Zeit verliert\n\n"
                    "Den Notruf darfst du nicht der ausgebildeten Ersthelferin "
                    "überlassen, wenn diese mit der Versorgung beschäftigt ist. "
                    "Jede anwesende Person ist zur Hilfeleistung verpflichtet — wer "
                    "wegsieht, macht sich nach § 323c StGB strafbar (Geldstrafe oder "
                    "Freiheitsstrafe bis zu einem Jahr).\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Schichtleiter findet in einer Metallverarbeitungs-Halle einen "
                    "Kollegen bewusstlos am Boden, neben einer offenen "
                    "Schweiß-Stromquelle. Er greift sofort den Hauptschalter an der "
                    "Wand und legt die Anlage spannungsfrei, *bevor* er sich dem "
                    "Verletzten nähert — sonst wäre er selbst gefährdet. Dann "
                    "drückt er die Halle-interne Notruf-Taste, die parallel die "
                    "Werkschutz-Zentrale und die 112 erreicht. Im Gespräch sagt er "
                    "knapp: *Halle 3, Tor B, Hannoversche Straße 14, ein Mann ca. "
                    "40 Jahre, bewusstlos nach Stromunfall, atmet flach, keine "
                    "sichtbaren Blutungen*. Die Leitstelle leitet ihn während des "
                    "Wartens zur stabilen Seitenlage an. Der Rettungsdienst ist in "
                    "sechs Minuten am Tor — der Werkschutz hat es offen gehalten "
                    "und führt das Team direkt zur Halle.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Vorschrift 1 *Grundsätze der "
                    "Prävention* §§ 24-26 (Stand 2023), DGUV Information 204-022 "
                    "*Erste Hilfe im Betrieb* und DGUV Information 204-006 "
                    "*Anleitung zur Ersten Hilfe* (Stand Januar 2023)."
                ),
            ),
            ModulDef(
                titel="Bewusstlosigkeit & Wiederbelebung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Herz-Kreislauf-Stillstand führt nach drei bis fünf Minuten "
                    "ohne Sauerstoff zu irreversiblen Hirnschäden. Wer in dieser "
                    "Zeit mit Herzdruckmassage beginnt, verdoppelt bis verdreifacht "
                    "die Überlebenschance. In einer typischen Werkhalle dauert es "
                    "trotz Notruf oft acht bis zwölf Minuten, bis der Rettungsdienst "
                    "an der Person ist. Diese Minuten musst du als Laienhelfer "
                    "überbrücken. Du lernst, wie du Bewusstlosigkeit erkennst, "
                    "die stabile Seitenlage anwendest und die Wiederbelebung nach "
                    "den GRC-Leitlinien 2025 durchführst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 24 DGUV Vorschrift 1** — Erste-Hilfe-Material und Rettungstransport\n"
                    "- **§ 26 DGUV Vorschrift 1** — Ersthelfer-Quote und Fortbildung\n"
                    "- **GRC-Leitlinien 2025** — Aktuelle Reanimations-Empfehlungen des German Resuscitation Council\n"
                    "- **§ 323c StGB** — Hilfeleistungspflicht für jedermann\n\n"
                    "## Was musst du wissen\n\n"
                    "Bewusstlosigkeit erkennst du in drei Sekunden: ansprechen, "
                    "leicht rütteln, keine Reaktion. Dann prüfst du in maximal "
                    "zehn Sekunden die Atmung — Kopf vorsichtig überstrecken, Kinn "
                    "anheben, sehen ob sich der Brustkorb hebt, hören und fühlen "
                    "ob Atem aus Mund oder Nase kommt. Schnappatmung ist *keine* "
                    "normale Atmung, sondern ein typisches Zeichen für "
                    "Herzstillstand.\n\n"
                    "Atmet die Person normal, kommt die **stabile Seitenlage**: "
                    "sie hält die Atemwege frei und verhindert Ersticken an "
                    "Erbrochenem. Atmet sie nicht normal, beginnt sofort die "
                    "**Herz-Lungen-Wiederbelebung (HLW)**.\n\n"
                    "Die HLW-Parameter nach GRC 2025:\n\n"
                    "| Parameter | Wert |\n"
                    "|---|---|\n"
                    "| Verhältnis Druck zu Beatmung | 30:2 |\n"
                    "| Drucktiefe Erwachsener | 5 bis 6 cm |\n"
                    "| Frequenz | 100 bis 120 pro Minute |\n"
                    "| Druckpunkt | Mitte des Brustkorbs, unteres Drittel des Brustbeins |\n"
                    "| Entlastung | Brustkorb vollständig zurückfedern lassen |\n\n"
                    "Wenn du dir die Beatmung nicht zutraust (Ekel, "
                    "Infektions-Sorge), ist reine Herzdruckmassage ohne Beatmung "
                    "ausdrücklich besser als nichts. Sauerstoff ist im Blut noch "
                    "für mehrere Minuten vorhanden — das Drücken hält den "
                    "Kreislauf in Gang.\n\n"
                    "Ein **AED** (Automatisierter Externer Defibrillator) ist in "
                    "vielen Betrieben verfügbar (grünes Schild mit weißem Herz "
                    "und Blitz). Er führt dich per Sprachanweisung durch den "
                    "Einsatz: Elektroden aufkleben, Person freimachen, "
                    "Rhythmus-Analyse abwarten, ggf. Schock-Knopf drücken. Bis "
                    "der AED angeschlossen ist, weiter drücken — die HLW wird "
                    "nur für die Analyse-Sekunden unterbrochen.\n\n"
                    "## Was musst du tun\n\n"
                    "Bei Bewusstlosigkeit mit normaler Atmung — stabile Seitenlage:\n\n"
                    "1. Naher Arm im rechten Winkel nach oben legen\n"
                    "2. Fernen Arm über die Brust legen, Hand an die nahe Wange\n"
                    "3. Fernes Bein anwinkeln und am Knie zu dir ziehen, Person dreht auf die Seite\n"
                    "4. Kopf nach hinten neigen, Mund leicht öffnen, Atmung weiter prüfen\n"
                    "5. Beim Verletzten bleiben, alle Minute Atmung kontrollieren\n\n"
                    "Bei fehlender oder anormaler Atmung — Wiederbelebung:\n\n"
                    "1. Notruf 112 und AED holen lassen (zweite Person)\n"
                    "2. Person auf festen Untergrund, Oberkörper freimachen\n"
                    "3. Handballen Mitte Brustkorb, andere Hand darüber, Arme gestreckt\n"
                    "4. 30 Mal drücken (5-6 cm tief, 100-120/min), dann 2 Mal beatmen\n"
                    "5. AED anschließen sobald da, Sprachanweisungen folgen\n"
                    "6. Weiter im 30:2-Rhythmus bis Rettungsdienst übernimmt\n\n"
                    "Alle zwei Minuten Helferwechsel, weil Druckqualität sonst "
                    "schnell nachlässt. Pausen so kurz wie möglich halten — jede "
                    "Sekunde Pause kostet Druck im Kreislauf.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Kunststoff-Spritzguss-Fertigung sackt eine Maschinen"
                    "führerin an ihrer Anlage zusammen. Eine Kollegin sieht es, "
                    "ruft laut nach Hilfe und alarmiert die Schichtleitung über "
                    "Funk. Der ausgebildete Ersthelfer aus dem Bereich Logistik "
                    "kommt nach 40 Sekunden, prüft Bewusstsein und Atmung — "
                    "Schnappatmung, kein Bewusstsein. Er beginnt sofort mit der "
                    "Herzdruckmassage, eine zweite Kollegin holt den AED, der "
                    "ausgeschildert im Pausenraum hängt. Der AED gibt nach "
                    "Anschluss einen Schock ab, danach geht die HLW weiter. Als "
                    "der Rettungsdienst nach neun Minuten eintrifft, hat die "
                    "Frau wieder einen tastbaren Puls. Ohne die frühe HLW und "
                    "den AED wäre sie nicht zu retten gewesen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf die GRC-Leitlinien 2025 "
                    "(*Reanimationsleitlinien des German Resuscitation Council*), "
                    "DGUV Information 204-007 *Handbuch zur Ersten Hilfe* "
                    "und DGUV Information 204-022 *Erste Hilfe im Betrieb*."
                ),
            ),
            ModulDef(
                titel="Wunden, Verbrennungen, Schock",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Die häufigsten Notfälle in der Industrie sind keine "
                    "Herzstillstände, sondern Quetschungen, Schnittverletzungen "
                    "an Blechkanten, Verbrennungen beim Schweißen oder Löten, "
                    "Verätzungen beim Umfüllen von Chemikalien und Stürze von "
                    "Leitern oder Bühnen. Du lernst, wie du Wunden versorgst, "
                    "starke Blutungen stoppst, Verbrennungen richtig behandelst "
                    "und einen Schock erkennst, bevor er lebensbedrohlich wird.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 24 DGUV Vorschrift 1** — Erste-Hilfe-Material muss bereitgehalten werden\n"
                    "- **ASR A4.3** — Erste-Hilfe-Räume, -Mittel und -Einrichtungen\n"
                    "- **DIN 13157** — Inhalt Verbandkasten Typ C (kleine Betriebe)\n"
                    "- **DIN 13169** — Inhalt Verbandkasten Typ E (größere Betriebe)\n\n"
                    "## Was musst du wissen\n\n"
                    "Der **Verbandkasten** muss laut ASR A4.3 in jedem Betrieb gut "
                    "sichtbar gekennzeichnet und schnell erreichbar sein. Standard "
                    "in Industriebetrieben ist Typ E (DIN 13169) — er reicht für "
                    "bis zu 50 Beschäftigte je Verbandkasten. Das Vorhandensein "
                    "wird durch ein weißes Kreuz auf grünem Grund (DIN EN ISO 7010 "
                    "E003) markiert. Nach jedem Einsatz wird aufgefüllt — fehlende "
                    "Inhalte sind eine Ordnungswidrigkeit.\n\n"
                    "Bei **Wunden** gilt die Reihenfolge: nicht berühren, nicht "
                    "auswaschen (Ausnahme: Verätzung), nicht desinfizieren mit "
                    "Spiritus oder ähnlichem. Steriles Wundkissen aus dem "
                    "Verbandkasten auflegen, mit Mullbinde fixieren, fertig. Bei "
                    "**starker Blutung** zusätzlich Druckverband: zweites Wundkissen "
                    "fest auf die Wunde, Mullbinde stramm umwickeln, bei "
                    "Durchblutung ein drittes Polster nachlegen — nicht den "
                    "alten Verband entfernen.\n\n"
                    "**Verbrennungen** werden nach drei Graden eingeteilt:\n\n"
                    "| Grad | Erscheinung | Behandlung |\n"
                    "|---|---|---|\n"
                    "| I | Rötung, Schmerz (wie Sonnenbrand) | 10-20 min mit handwarmem Wasser kühlen |\n"
                    "| II | Blasenbildung | nur kurz kühlen, steril abdecken, nicht öffnen |\n"
                    "| III | Weiße oder verkohlte Haut, oft schmerzlos | nicht kühlen, steril abdecken, Notruf |\n\n"
                    "Wichtig: bei Verbrennungen über Handgröße oder im Gesicht/"
                    "Genital immer Rettungsdienst rufen. Lange Kühlung mit kaltem "
                    "Wasser ist gefährlich (Unterkühlung) — nur kurz und nur mit "
                    "handwarmem Wasser.\n\n"
                    "Bei **Verätzungen** (z.B. Säure-Spritzer beim Beizen) sofort "
                    "mit viel Wasser spülen, mindestens 10 Minuten, betroffene "
                    "Kleidung dabei entfernen. Augen-Verätzung: Augendusche oder "
                    "fließendes Wasser, immer von der Nase nach außen spülen, "
                    "damit das Ätzmittel nicht ins andere Auge läuft.\n\n"
                    "Ein **Schock** entsteht durch großen Blutverlust, starke "
                    "Schmerzen oder schwere Verbrennungen. Zeichen: blasse, "
                    "kalt-feuchte Haut, schneller flacher Puls, Frieren trotz "
                    "Wärme, Unruhe, später Bewusstseinstrübung. Unbehandelt "
                    "ist Schock lebensbedrohlich.\n\n"
                    "## Was musst du tun\n\n"
                    "Bei jeder Verletzung in fester Reihenfolge:\n\n"
                    "1. Eigenschutz prüfen — Maschine aus, Stromzufuhr trennen, scharfe Teile entfernen\n"
                    "2. Notruf 112 absetzen, falls die Verletzung dies erfordert\n"
                    "3. Wunde mit sterilem Material aus dem Verbandkasten abdecken\n"
                    "4. Betroffenen hinsetzen oder hinlegen, beruhigend ansprechen\n"
                    "5. Auf Schock-Zeichen achten und Schocklage vorbereiten\n\n"
                    "Schocklage: flach hinlegen, Beine ca. 30 cm hoch lagern "
                    "(Stuhl, Werkstoffrolle, Jacke unter die Füße). *Nicht* bei "
                    "Verdacht auf Wirbelsäulenverletzung, Atemnot, Herzbeschwerden "
                    "oder Kopfverletzung — dann flach lagern. Person zudecken, "
                    "möglichst nicht alleine lassen, regelmäßig ansprechen.\n\n"
                    "Niemals einer bewusstlosen oder schockierten Person etwas zu "
                    "trinken geben — Erstickungsgefahr und Komplikationen bei "
                    "späteren OP.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Beim Schleifen einer Stahlplatte rutscht einem Auszubildenden "
                    "die Flex an einer Blechkante ab — tiefer Schnitt am Unterarm, "
                    "spritzende Blutung. Der Meister handelt nach Schema: Flex aus, "
                    "Auszubildender hinsetzen, eigene OP-Handschuhe aus dem "
                    "Verbandkasten, zwei Wundkissen druckverbandartig fest auf "
                    "die Wunde gewickelt mit Mullbinde. Notruf 112 über das "
                    "Werktelefon — *Halle 5, Werkstraße 3, junger Mann, 17 Jahre, "
                    "tiefer Schnitt Unterarm mit starker Blutung, ansprechbar*. "
                    "Beim Warten fängt der Auszubildende an zu zittern und wird "
                    "blass — der Meister legt die Beine hoch, deckt ihn mit der "
                    "Werkstattjacke zu, spricht ihn immer wieder an. Der "
                    "Rettungsdienst kommt nach acht Minuten, der Druckverband "
                    "hat gehalten. Das Krankenhaus konfirmiert später: ohne "
                    "den schnellen Druckverband hätte die Sehnen-Verletzung "
                    "deutlich mehr Blut gekostet.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Information 204-022 *Erste Hilfe im "
                    "Betrieb*, DGUV Information 204-006 *Anleitung zur Ersten "
                    "Hilfe* (Ausgabe Januar 2023), DIN 13157/13169 *Verbandkasten* "
                    "und ASR A4.3 *Erste-Hilfe-Räume, -Mittel und "
                    "-Einrichtungen*."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Nummer ist in ganz Deutschland und EU-weit der Notruf für Rettungsdienst und Feuerwehr?",
                erklaerung="Die 112 ist EU-weit einheitlich, kostenlos und auch ohne SIM-Karte erreichbar. "
                "Die 110 ist die Polizei und nicht primär für medizinische Notfälle.",
                optionen=_opts(
                    ("110", False),
                    ("112", True),
                    ("115", False),
                    ("116 117", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet das letzte W im Notruf-Schema '5 W'?",
                erklaerung="Die Leitstelle hat in der Regel Rückfragen und kann während des Gesprächs "
                "Anweisungen geben. Nie zuerst auflegen.",
                optionen=_opts(
                    ("Wer ruft an", False),
                    ("Welcher Arzt soll kommen", False),
                    ("Warten auf Rückfragen, niemals zuerst auflegen", True),
                    ("Wann passierte es", False),
                ),
            ),
            FrageDef(
                text="In welcher Reihenfolge gibst du die Informationen beim Notruf an?",
                erklaerung="Wo, Was, Wie viele, Welche Verletzungen, Warten — in dieser Reihenfolge "
                "kann die Leitstelle parallel Rettungsmittel disponieren.",
                optionen=_opts(
                    ("Wer-Was-Warum-Wann-Wie", False),
                    ("Wo-Was-Wie viele-Welche-Warten", True),
                    ("Wann-Wo-Wer-Was-Wie", False),
                    ("Was-Wo-Wer-Wann-Warum", False),
                ),
            ),
            FrageDef(
                text="Wie hoch ist die Pflicht-Quote an Ersthelfern in einem produzierenden Betrieb (kein Verwaltungsbetrieb)?",
                erklaerung="DGUV Vorschrift 1 § 26 Abs. 2: 10 Prozent der anwesenden Versicherten in "
                "sonstigen Betrieben, 5 Prozent in Verwaltungs- und Handelsbetrieben.",
                optionen=_opts(
                    ("1 Prozent der Beschäftigten", False),
                    ("5 Prozent der Beschäftigten", False),
                    ("10 Prozent der Beschäftigten", True),
                    ("20 Prozent der Beschäftigten", False),
                ),
            ),
            FrageDef(
                text="Wie oft muss die Ersthelfer-Ausbildung aufgefrischt werden, damit der Status erhalten bleibt?",
                erklaerung="Alle 2 Jahre durch ein Erste-Hilfe-Training (9 UE). Wer die Frist "
                "überschreitet, verliert den Status und muss die gesamte Grundausbildung erneut absolvieren.",
                optionen=_opts(
                    ("Jährlich", False),
                    ("Alle 2 Jahre", True),
                    ("Alle 3 Jahre", False),
                    ("Alle 5 Jahre", False),
                ),
            ),
            FrageDef(
                text="Welche Drucktiefe gilt nach den GRC-Leitlinien 2025 bei der Herzdruckmassage am Erwachsenen?",
                erklaerung="Die aktuellen Reanimationsleitlinien des German Resuscitation Council 2025 "
                "schreiben 5 bis 6 cm bei Erwachsenen vor — tiefer riskiert Rippenbruch, weniger ist wirkungslos.",
                optionen=_opts(
                    ("1 bis 2 cm", False),
                    ("3 bis 4 cm", False),
                    ("5 bis 6 cm", True),
                    ("7 bis 8 cm", False),
                ),
            ),
            FrageDef(
                text="Welches Verhältnis von Herzdruckmassage zu Beatmung gilt nach aktuellen Leitlinien beim Erwachsenen?",
                erklaerung="Das 30:2-Schema ist GRC-Standard für Laienhelfer: 30 Mal drücken, "
                "2 Mal beatmen, dann wieder 30 Mal drücken.",
                optionen=_opts(
                    ("15:2", False),
                    ("30:2", True),
                    ("5:1", False),
                    ("50:5", False),
                ),
            ),
            FrageDef(
                text="Du findest in der Halle einen Kollegen bewusstlos neben einer offenen Schweißstromquelle. Was tust du ZUERST?",
                erklaerung="Eigenschutz hat absolute Priorität. Erst Stromzufuhr trennen, dann zur Person — "
                "sonst werden zwei Verletzte daraus.",
                optionen=_opts(
                    ("Sofort hinlaufen und mit Herzdruckmassage beginnen", False),
                    ("Hauptschalter ausschalten oder Stromzufuhr trennen, dann nähern", True),
                    ("Erst den Notruf absetzen und dann warten", False),
                    ("Den Werkstattmeister suchen und ihn entscheiden lassen", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege ist bewusstlos, atmet aber normal. Was ist die richtige Maßnahme?",
                erklaerung="Stabile Seitenlage hält die Atemwege frei und verhindert Ersticken an Erbrochenem. "
                "Herzdruckmassage wäre bei vorhandener Atmung falsch.",
                optionen=_opts(
                    ("Sofort mit Herzdruckmassage beginnen", False),
                    ("Stabile Seitenlage, Notruf 112, Atmung weiter kontrollieren", True),
                    ("Auf den Rücken legen und Wasser ins Gesicht spritzen", False),
                    ("Sitzend an die Wand lehnen und warten bis er aufwacht", False),
                ),
            ),
            FrageDef(
                text="Schnappatmung bei einer bewusstlosen Person ist ein Zeichen für was?",
                erklaerung="Schnappatmung ist kein Atmen, sondern ein Reflex bei Herzstillstand. "
                "Sie ist Indikation für sofortige Wiederbelebung.",
                optionen=_opts(
                    ("Normale Atmung im Schlaf", False),
                    ("Herzstillstand — Reanimation sofort beginnen", True),
                    ("Asthma-Anfall", False),
                    ("Schock ohne Verletzung", False),
                ),
            ),
            FrageDef(
                text="Du traust dir die Atemspende nicht zu (Ekel, Sorge um Infektion). Was ist trotzdem richtig?",
                erklaerung="Reine Herzdruckmassage ohne Beatmung ist ausdrücklich besser als gar nichts. "
                "Sauerstoff im Blut reicht für einige Minuten — entscheidend ist der Kreislauf.",
                optionen=_opts(
                    ("Gar nichts tun und nur auf den Rettungsdienst warten", False),
                    ("Nur Herzdruckmassage ohne Beatmung machen, durchgehend 100 bis 120 pro Minute", True),
                    ("Stabile Seitenlage, weil ohne Beatmung Reanimation sinnlos ist", False),
                    ("Person aufrecht hinsetzen und Wasser einflößen", False),
                ),
            ),
            FrageDef(
                text="Was ist ein AED?",
                erklaerung="Ein Automatisierter Externer Defibrillator gibt per Sprachanweisung Schock-Empfehlungen. "
                "Er erkennt schockbare Rhythmen selbst und ist von Laien sicher zu bedienen.",
                optionen=_opts(
                    ("Ein Atem-Erkennungs-Gerät zur Atemkontrolle", False),
                    ("Ein Automatisierter Externer Defibrillator zur Schockabgabe bei Herzstillstand", True),
                    ("Ein Adrenalin-Einspritz-Stift für allergische Reaktionen", False),
                    ("Ein Aushang zur Erste-Hilfe-Dokumentation", False),
                ),
            ),
            FrageDef(
                text="Wo platzierst du die Hände für die Herzdruckmassage?",
                erklaerung="Mitte des Brustkorbs, auf dem unteren Drittel des Brustbeins. Druck am Rippenbogen "
                "oder seitlich ist wirkungslos und verletzt.",
                optionen=_opts(
                    ("Linke Brustseite über dem Herz", False),
                    ("Mitte des Brustkorbs, unteres Drittel des Brustbeins", True),
                    ("Bauchmitte unterhalb des Rippenbogens", False),
                    ("Rechte Brustseite unter dem Schlüsselbein", False),
                ),
            ),
            FrageDef(
                text="Welche Frequenz hat die Herzdruckmassage nach GRC-Leitlinien?",
                erklaerung="100 bis 120 Drücke pro Minute — das entspricht etwa dem Takt von 'Stayin Alive' "
                "oder 'Atemlos durch die Nacht'.",
                optionen=_opts(
                    ("40 bis 60 pro Minute", False),
                    ("60 bis 80 pro Minute", False),
                    ("100 bis 120 pro Minute", True),
                    ("150 bis 180 pro Minute", False),
                ),
            ),
            FrageDef(
                text="Welche Norm regelt den Inhalt eines Verbandkastens Typ E für größere Betriebe?",
                erklaerung="DIN 13169 definiert den Inhalt für den großen Verbandkasten Typ E, "
                "der in Industriebetrieben üblich ist. DIN 13157 ist der kleinere Typ C.",
                optionen=_opts(
                    ("DIN 13157", False),
                    ("DIN 13169", True),
                    ("DIN EN 397", False),
                    ("DIN 12345", False),
                ),
            ),
            FrageDef(
                text="Eine Kollegin verbrennt sich beim Schweißen die Hand (Grad II, Blasenbildung). Was ist richtig?",
                erklaerung="Kurze Kühlung mit handwarmem Wasser, dann steril abdecken. Blasen NIEMALS öffnen — "
                "die intakte Blase ist der beste Wundschutz.",
                optionen=_opts(
                    ("Blasen mit sauberer Nadel öffnen, damit die Wundflüssigkeit raus kann", False),
                    ("Salbe oder Mehl auftragen, dann verbinden", False),
                    ("Kurz mit handwarmem Wasser kühlen, Blasen nicht öffnen, steril abdecken", True),
                    ("Lange mit Eiswasser kühlen, bis kein Schmerz mehr ist", False),
                ),
            ),
            FrageDef(
                text="Beim Beizen bekommt ein Mitarbeiter Säure ins Auge. Was tust du?",
                erklaerung="Sofort und lange (mindestens 10 Min) spülen, vom Naseninnenwinkel nach außen, "
                "damit das Ätzmittel nicht ins gesunde Auge läuft. Anschließend Notruf 112.",
                optionen=_opts(
                    ("Auge zukneifen und sofort zum Arzt fahren", False),
                    ("Mit viel Wasser von der Nase nach außen spülen, mindestens 10 Minuten, dann Notruf", True),
                    ("Mit Verbandsmaterial trocken abtupfen", False),
                    ("Mit Milch oder Cola spülen zur Neutralisierung", False),
                ),
            ),
            FrageDef(
                text="Welche Zeichen weisen auf einen einsetzenden Schock hin?",
                erklaerung="Blasse, kalt-feuchte Haut, schneller flacher Puls, Frieren und Unruhe sind "
                "typische Schock-Zeichen. Sofort Schocklage und Notruf, falls nicht längst erfolgt.",
                optionen=_opts(
                    ("Rote, warme Haut und langsamer Puls", False),
                    ("Blasse, kalt-feuchte Haut, schneller flacher Puls, Frieren und Unruhe", True),
                    ("Trockene Haut und geweitete Pupillen", False),
                    ("Gelbe Haut und tiefer ruhiger Atem", False),
                ),
            ),
            FrageDef(
                text="In welcher Lage versorgst du einen schockierten Patienten OHNE Verdacht auf Wirbel- oder Kopfverletzung?",
                erklaerung="Schocklage: flach hinlegen, Beine ca. 30 cm hochlagern. Das verbessert die "
                "Durchblutung von Gehirn und lebenswichtigen Organen.",
                optionen=_opts(
                    ("Sitzend an die Wand gelehnt", False),
                    ("Flach hinlegen, Beine etwa 30 cm hochlagern (Schocklage)", True),
                    ("Auf der Seite mit Knien an die Brust gezogen", False),
                    ("Bauchlage mit Kopf zur Seite", False),
                ),
            ),
            FrageDef(
                text="Was darfst du einer bewusstlosen oder schockierten Person AUF KEINEN FALL geben?",
                erklaerung="Etwas zu trinken zu geben ist gefährlich: Erstickungsgefahr durch fehlende Schluckreflexe "
                "und Komplikationen bei späteren OPs (Nüchternheits-Gebot).",
                optionen=_opts(
                    ("Eine Decke", False),
                    ("Beruhigende Worte", False),
                    ("Etwas zu trinken (Wasser, Saft, Kaffee)", True),
                    ("Eigene Jacke unter den Kopf", False),
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
                    "## Worum geht's?\n\n"
                    "Wer Kühlschmierstoff in eine ungekennzeichnete Sprühflasche umfüllt, "
                    "Reiniger neben Säurebeize ins Regal stellt oder ein Fass ohne Etikett "
                    "in die Ecke rollt, baut die häufigste Unfallursache der Metallverarbeitung "
                    "selbst auf. Die **GHS-Kennzeichnung** ist die Sprache, mit der dir jeder "
                    "Gefahrstoff sagt, was er kann, bevor er es tut. Du lernst, die neun "
                    "Piktogramme zu erkennen, das Signalwort einzuordnen und H- und P-Saetze "
                    "zu lesen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **CLP-Verordnung (EG) Nr. 1272/2008** — EU-weite Einstufung und "
                    "Kennzeichnung von Stoffen und Gemischen, in Kraft seit 2009\n"
                    "- **§ 8 GefStoffV** — Grundpflichten: Kennzeichnung am Arbeitsplatz, "
                    "auch bei Umfüllen in Standgefässe\n"
                    "- **§ 14 GefStoffV** — jährliche arbeitsplatzbezogene Unterweisung\n"
                    "- **TRGS 201** — Kennzeichnung von Abfällen und innerbetrieblichen Gebinden\n\n"
                    "## Was musst du wissen\n\n"
                    "Jeder Gefahrstoff trägt ein Etikett mit fünf Pflicht-Elementen: "
                    "Produktidentifikator, Lieferantenangabe, Gefahrenpiktogramm, "
                    "Signalwort und Gefahren- plus Sicherheitshinweise. Das **Signalwort** "
                    "ist entweder *Gefahr* (höhere Gefahrenstufe) oder *Achtung* (geringere "
                    "Stufe). Es gibt nie beides auf einem Etikett.\n\n"
                    "Die neun **GHS-Piktogramme** sind eine rotgerahmte Raute auf weissem Grund:\n\n"
                    "| Code | Symbol | Bedeutung | Typische Stoffe im Betrieb |\n"
                    "|---|---|---|---|\n"
                    "| GHS01 | Explodierende Bombe | Explosivstoff | Treibladungen, instabile Peroxide |\n"
                    "| GHS02 | Flamme | Entzündbar | Verdünner, Aceton, Benzin, Spraydosen |\n"
                    "| GHS03 | Flamme über Kreis | Brandfördernd | Wasserstoffperoxid, Nitrate |\n"
                    "| GHS04 | Gasflasche | Gas unter Druck | Acetylen, Sauerstoff, Schutzgas |\n"
                    "| GHS05 | Reagenzglas auf Hand | Ätzend / korrosiv | Säurebeize, Natronlauge, Entkalker |\n"
                    "| GHS06 | Totenkopf | Akut toxisch | Cyanide, manche Pflanzenschutzmittel |\n"
                    "| GHS07 | Ausrufezeichen | Reizend, sensibilisierend, gesundheitsschädlich | viele Reiniger, Klebstoffe |\n"
                    "| GHS08 | Person mit Stern | Chronische Gesundheitsgefahr (CMR, Aspiration) | Kühlschmierstoffe mit Borax, Schweissrauch-Bestandteile |\n"
                    "| GHS09 | Fisch und Baum | Gewässergefährdend | Lacke, Lösemittel, viele Öle |\n\n"
                    "**H-Sätze** (Hazard) beschreiben die Gefahr, **P-Sätze** (Precautionary) "
                    "die Schutzmassnahme. H225 heisst zum Beispiel 'Flüssigkeit und Dampf "
                    "leicht entzündbar', P210 'Von Hitze, heissen Oberflächen, Funken, offenen "
                    "Flammen und anderen Zündquellen fernhalten'. Die volle Liste findest du "
                    "im Anhang III der CLP-Verordnung und im Sicherheitsdatenblatt.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor jedem Einsatz eines neuen Stoffes Etikett lesen — Signalwort, "
                    "Piktogramme, mindestens die ersten H- und P-Sätze\n"
                    "2. Niemals einen Gefahrstoff in ein altes Lebensmittelgefäss umfüllen "
                    "(Wasserflasche, Brotdose) — strikt verboten nach § 8 GefStoffV\n"
                    "3. Beim Umfüllen in eine Sprühflasche oder ein Standgefäss sofort "
                    "neu kennzeichnen: Produktname, Piktogramm, Signalwort, Datum\n"
                    "4. Bei unleserlichen oder fehlenden Etiketten den Stoff nicht verwenden "
                    "und an die Schichtleitung melden\n"
                    "5. Im Zweifel zuerst das Sicherheitsdatenblatt aufrufen, dann handeln\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Schlossereihalle steht eine 1-Liter-Wasserflasche neben der "
                    "Werkbank. Ein Auszubildender trinkt daraus, weil er sie für die Trinkflasche "
                    "des Kollegen hält. In der Flasche ist konzentrierter Entkalker, den der "
                    "Kollege zum Reinigen einer Spannvorrichtung aus dem 25-Liter-Kanister "
                    "umgefüllt hatte — ohne Etikett, ohne Piktogramm. Folge: Verätzung im "
                    "Mund-Rachen-Raum, Notarzt-Einsatz, BG-Anzeige, Strafverfahren gegen "
                    "den Vorgesetzten wegen Verstoss gegen § 8 GefStoffV. Mit GHS05-Etikett "
                    "und Signalwort 'Gefahr' wäre der Griff zur Flasche unterblieben.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf CLP-Verordnung (EG) Nr. 1272/2008 Anhang V "
                    "*Gefahrenpiktogramme*, GefStoffV (Stand 2024) und "
                    "BAuA-Praxishandbuch *GHS in der EU — Einstufung und Kennzeichnung* "
                    "(Ausgabe 2023)."
                ),
            ),
            ModulDef(
                titel="Sicherheitsdatenblatt (SDB) lesen",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Das **Sicherheitsdatenblatt (SDB)** ist der vollständige Steckbrief "
                    "eines Gefahrstoffs. Wer es lesen kann, weiss in zwei Minuten, ob der "
                    "Stoff die Lunge angreift, mit was er nicht zusammen darf, welche "
                    "Handschuhe halten und wie man im Unfall reagiert. Du lernst die "
                    "16 Pflicht-Abschnitte des SDB und welche davon im Alltag wirklich "
                    "zählen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **REACH-Verordnung (EG) Nr. 1907/2006, Art. 31 und Anhang II** — "
                    "der Lieferant muss das SDB in der Amtssprache mitliefern\n"
                    "- **§ 6 GefStoffV** — Informationsermittlung und Gefährdungsbeurteilung\n"
                    "- **TRGS 555** — Betriebsanweisung und Information der Beschäftigten\n\n"
                    "## Was musst du wissen\n\n"
                    "Ein SDB hat immer **16 Abschnitte** in fester Reihenfolge. Im Werkalltag "
                    "schaust du selten ins ganze Dokument — du gehst gezielt zu dem Abschnitt, "
                    "der zu deiner Frage passt:\n\n"
                    "| Abschnitt | Inhalt | Wann du ihn brauchst |\n"
                    "|---|---|---|\n"
                    "| 1 | Bezeichnung, Lieferant, Notrufnummer | Beim Anlegen einer Akte |\n"
                    "| 2 | Mögliche Gefahren, Signalwort, H/P-Sätze | Vor jedem Erstkontakt |\n"
                    "| 4 | Erste-Hilfe-Massnahmen | Sofort nach einem Unfall |\n"
                    "| 5 | Massnahmen zur Brandbekämpfung | Welcher Löscher passt |\n"
                    "| 6 | Verhalten bei unbeabsichtigter Freisetzung | Auslaufen, Verschütten |\n"
                    "| 7 | Handhabung und Lagerung | Vor dem Einlagern ins Regal |\n"
                    "| 8 | Begrenzung und Schutzmassnahmen, PSA, AGW | Welche Handschuhe, welche Brille |\n"
                    "| 9 | Physikalische und chemische Eigenschaften | Flammpunkt, Dichte |\n"
                    "| 10 | Stabilität und Reaktivität | Was darf nicht in Kontakt kommen |\n"
                    "| 13 | Hinweise zur Entsorgung | Abfallschlüssel-Nr. AVV |\n\n"
                    "Die für dich wichtigsten Abschnitte sind **4, 6, 7 und 8**. Abschnitt 8 "
                    "enthält die **Arbeitsplatzgrenzwerte (AGW)** — die Konzentration in der "
                    "Atemluft, bei der über acht Stunden keine Gesundheitsschäden zu erwarten "
                    "sind. Wird er überschritten, brauchst du Absaugung oder Atemschutz.\n\n"
                    "**Aushangpflicht:** Nach TRGS 555 muss für jeden Gefahrstoff am "
                    "Arbeitsplatz eine **Betriebsanweisung** in verständlicher Sprache "
                    "ausgehängt sein — meist eine A4-Seite im Regal oder am Mischplatz. "
                    "Das SDB selbst muss zugänglich sein, etwa im Ordner an der "
                    "Werkstattzentrale oder über das Werks-Intranet.\n\n"
                    "Veraltete SDBs sind ein häufiger Mangel bei BG-Audits. Der Lieferant "
                    "muss eine neue Version aktiv zusenden, sobald sich Einstufung oder "
                    "Schutzmassnahmen ändern. Datum in Abschnitt 16 prüfen — älter als drei "
                    "Jahre ohne Aktualisierung ist verdächtig.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor dem ersten Einsatz eines neuen Stoffes SDB öffnen und Abschnitte "
                    "2, 4, 7 und 8 lesen\n"
                    "2. Prüfen, ob die im Betrieb vorhandene PSA (Handschuhe, Brille, "
                    "Atemschutz) mit Abschnitt 8 übereinstimmt\n"
                    "3. Die ausgehängte Betriebsanweisung an deinem Arbeitsplatz vor jeder "
                    "Schicht mit neuem Stoff einmal lesen — die Aushangsprache ist verbindlich\n"
                    "4. Bei fehlendem SDB oder fehlender Betriebsanweisung den Stoff nicht "
                    "einsetzen, sondern an die Schichtleitung oder Fachkraft für "
                    "Arbeitssicherheit melden\n"
                    "5. Im Unfall sofort Abschnitt 4 öffnen und gleichzeitig Notruf wählen\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine neue Charge Säurebeize wird in der Galvanik angeliefert. Der "
                    "Schichtführer öffnet das beiliegende SDB und sieht in Abschnitt 8, "
                    "dass der bisher verwendete Nitril-Handschuh (0,11 mm) für den neuen "
                    "Stoff nur eine Durchbruchszeit von 15 Minuten hat. Die alte Charge "
                    "vertrug Nitril 0,11 mm mit über vier Stunden. Er stoppt den Einsatz "
                    "der neuen Beize, bestellt 0,38-mm-Butyl-Handschuhe und aktualisiert "
                    "die ausgehängte Betriebsanweisung. Zwei Wochen später hätte ohne diese "
                    "Prüfung ein Mitarbeiter eine Verätzung der Unterarme erlitten — die "
                    "Durchbruchszeit war an der gewohnten Misch-Tätigkeit überschritten.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf REACH-Verordnung (EG) Nr. 1907/2006 Anhang II "
                    "*Anforderungen an Sicherheitsdatenblätter* (zuletzt geändert "
                    "Verordnung (EU) 2020/878), TRGS 555 *Betriebsanweisung und Information "
                    "der Beschäftigten* (Ausgabe 2017) und GefStoffV § 6."
                ),
            ),
            ModulDef(
                titel="Lagerung & Substitution",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Falsche Lagerung ist die zweithäufigste Unfallursache nach falscher "
                    "Handhabung. Säure neben Lauge, Brennbares neben Sauerstoff, Gasflaschen "
                    "ohne Halterung — jeder dieser Fehler ist im Audit ein Verstoss und im "
                    "Schadensfall die Voll-Haftung des Unternehmers. Du lernst die Grundregeln "
                    "der TRGS 510 und den **Substitutionsgrundsatz** nach § 6 GefStoffV: "
                    "Erst prüfen, ob du den Gefahrstoff ganz vermeiden oder durch einen "
                    "harmloseren ersetzen kannst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 6 GefStoffV** — Informationsermittlung, Substitutionsprüfung\n"
                    "- **§ 7 GefStoffV** — Grundpflichten beim Umgang, Schutzmassnahmen\n"
                    "- **§ 9 GefStoffV** — Lagerung von Gefahrstoffen\n"
                    "- **TRGS 510** — Lagerung von Gefahrstoffen in ortsbeweglichen Behältern, "
                    "definiert die Lagerklassen (LGK) und Zusammenlagerungs-Verbote\n"
                    "- **TRGS 600** — Substitution als bevorzugte Schutzmassnahme\n\n"
                    "## Was musst du wissen\n\n"
                    "Vor der Lagerung steht die **Substitutionspflicht**: Der Arbeitgeber muss "
                    "prüfen, ob ein gefährlicher Stoff durch einen weniger gefährlichen ersetzt "
                    "oder ganz weggelassen werden kann. Beispiele aus der Metallverarbeitung: "
                    "wassermischbarer Kühlschmierstoff statt minerlischem Schneidöl, "
                    "wasserbasierter Entfetter statt Trichlorethylen, mechanisches Bürsten "
                    "statt Säurebeize wo möglich. Das Ergebnis der Prüfung wird in der "
                    "**Gefährdungsbeurteilung** dokumentiert.\n\n"
                    "Bleibt der Gefahrstoff im Betrieb, gilt TRGS 510 mit den **Lagerklassen "
                    "(LGK)**. Es gibt 12 Hauptklassen mit Unterklassen, die Zuordnung steht "
                    "im Sicherheitsdatenblatt Abschnitt 7 oder lässt sich aus dem Piktogramm "
                    "ableiten:\n\n"
                    "| LGK | Stoffgruppe | Beispiele |\n"
                    "|---|---|---|\n"
                    "| 2A | Verdichtete und verflüssigte Gase | Acetylen, Argon, Sauerstoff |\n"
                    "| 3 | Entzündbare Flüssigkeiten | Verdünner, Aceton, Benzin |\n"
                    "| 4.1A | Sonst. explosionsgefährliche Stoffe | Nitrocellulose |\n"
                    "| 5.1A | Stark oxidierende Stoffe | Wasserstoffperoxid >50 % |\n"
                    "| 6.1A | Akut toxische Stoffe | wenige Spezial-Chemikalien |\n"
                    "| 8A | Ätzende Stoffe, entzündbar | Säurebeize mit Lösemittel |\n"
                    "| 8B | Ätzende Stoffe, nicht entzündbar | Natronlauge, Salzsäure verdünnt |\n"
                    "| 10 | Sonstige Flüssigkeiten | Kühlschmierstoff-Emulsion |\n"
                    "| 12 | Nicht brennbare Feststoffe | Salze, Pulver |\n\n"
                    "Wichtige Zusammenlagerungs-Verbote: **Säuren niemals mit Laugen** "
                    "(LGK 8A/B unter sich auch nur mit Auffangwannen-Trennung), **brennbare "
                    "Flüssigkeiten niemals mit oxidierenden Stoffen** (LGK 3 + LGK 5.1 = "
                    "Brand- und Explosionsgefahr), **Gasflaschen aufrecht und gegen Umfallen "
                    "gesichert** mit Ventilschutzkappe. Mengenschwellen aus TRGS 510 Anhang 3 "
                    "bestimmen, ob ein eigener **Gefahrstoffschrank** oder ein **Gefahrstoff"
                    "lager** mit Brandabschnitt nötig ist — typisch über 200 kg entzündbare "
                    "Flüssigkeit kein Lagern mehr im Arbeitsraum.\n\n"
                    "Auffangwannen sind Pflicht für alle flüssigen wassergefährdenden Stoffe "
                    "(WGK 1-3). Volumen der Wanne: mindestens 10 Prozent der gelagerten Menge, "
                    "mindestens das Volumen des grössten Einzelgebindes.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Gefahrstoffe nur im dafür ausgewiesenen Schrank oder Regal lagern, "
                    "nicht 'kurz' auf der Werkbank stehen lassen\n"
                    "2. Originalgebinde nicht öffnen und stehen lassen — nach Gebrauch sofort "
                    "verschliessen und zurück ins Lager\n"
                    "3. Säurebeize und Reiniger niemals im selben Auffangwannen-Bereich, "
                    "auch nicht 'für eine Stunde'\n"
                    "4. Gasflaschen sofort nach dem Anlieferung mit Kette oder Bügel sichern "
                    "und Ventilschutzkappe nur zum Anschliessen entfernen\n"
                    "5. Bei Auslaufen sofort mit Bindemittel (Vermiculit, Chemikalien-Bindevlies) "
                    "aufnehmen, niemals mit Wasser wegspülen — kommt ins Grundwasser und ist "
                    "eine Straftat nach § 324a StGB (Bodenverunreinigung)\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem mittelständischen Zulieferer ist die Säurebeize (Phosphorsäure-"
                    "Gemisch, LGK 8B) jahrelang im selben Stahlregal wie der Industrie-Reiniger "
                    "(Natronlauge-Lösung, LGK 8B) gelagert worden — beide tropfen gelegentlich. "
                    "Bei einer routinemässigen Begehung durch die Berufsgenossenschaft fällt "
                    "auf, dass die Auffangwannen-Trennung fehlt. Die BG verhängt einen Mängel-"
                    "bescheid mit Frist von vier Wochen. Der Betrieb investiert 1.800 Euro in "
                    "zwei getrennte Gefahrstoffschränke mit eigener Wanne pro Schrank. Drei "
                    "Monate später platzt ein 10-Liter-Kanister Phosphorsäure unbemerkt im "
                    "Nachtbetrieb. Die Säure läuft in die Wanne, die Lauge bleibt unberührt — "
                    "ohne die Trennung hätte die Reaktion Chlorgas freigesetzt, die "
                    "Nachtschicht hätte evakuiert werden müssen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf TRGS 510 *Lagerung von Gefahrstoffen in "
                    "ortsbeweglichen Behältern* (Ausgabe 2021), TRGS 600 *Substitution* "
                    "(Ausgabe 2008, fortgeschrieben 2020), GefStoffV §§ 6, 7, 9 und "
                    "DGUV Regel 113-001 *Lagerung gefährlicher Stoffe in Arbeitsräumen*."
                ),
            ),
            ModulDef(
                titel="Verhalten im Schadensfall",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein zerbrochener Säurekanister, eine Stichflamme aus dem Reinigerfass, "
                    "ein Schweisser mit Verdünner-Spritzer im Auge — wer in den ersten zwei "
                    "Minuten falsch reagiert, macht aus einem Erste-Hilfe-Fall einen "
                    "Notarzt-Einsatz oder einen Brand zur Werkstatt-Vernichtung. Du lernst "
                    "die richtige Reihenfolge bei Verätzungen, Vergiftungen, Auslaufen und "
                    "Brand sowie die Rolle der **Notdusche und Augendusche**.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 13 GefStoffV** — Massnahmen bei Betriebsstörungen, Unfällen und "
                    "Notfällen\n"
                    "- **§ 10 ArbSchG** — Erste Hilfe und Notfallmassnahmen\n"
                    "- **DGUV Vorschrift 1 § 24** — Notrufeinrichtungen, Erste-Hilfe-Mittel\n"
                    "- **TRGS 526** — Laboratorien (analog für Werkstatt-Mischplätze): "
                    "Notdusche im Umkreis von 5 m, Wassertemperatur 15-30 °C\n\n"
                    "## Was musst du wissen\n\n"
                    "Bei jedem Schadensfall mit Gefahrstoff gilt die Reihenfolge: "
                    "**Eigenschutz, Personen retten, Alarm, Eingrenzen, Aufnehmen**. "
                    "Eigenschutz heisst, dass du dich nicht in die Schadenstelle hineinziehen "
                    "lässt — eine ausgelaufene Säurelache, in die du hineintrittst, macht "
                    "aus dem Helfer das nächste Opfer.\n\n"
                    "**Verätzung der Haut:** Sofort kontaminierte Kleidung entfernen "
                    "(vorsichtig, nicht über den Kopf ziehen, eher aufschneiden) und mit "
                    "viel Wasser mindestens 15 Minuten spülen. Bei grossflächigem Kontakt "
                    "unter die Notdusche stellen — die Auslösung ist meist eine grosse "
                    "dreieckige Stange oder ein Fusspedal.\n\n"
                    "**Verätzung des Auges:** Lidspalte mit den Fingern auseinanderziehen "
                    "und mit der Augendusche oder einer Augenspülflasche von innen nach "
                    "aussen spülen, mindestens 10 Minuten. Kontaktlinsen während des Spülens "
                    "entfernen, falls möglich. Danach sofort zum Augenarzt — Säure- und "
                    "Laugenverätzungen am Auge können in Minuten zur Erblindung führen.\n\n"
                    "**Inhalation von Dämpfen:** Person sofort an die frische Luft bringen, "
                    "Notruf 112. Bei Bewusstlosigkeit stabile Seitenlage, bei Atemstillstand "
                    "Wiederbelebung. Beim Notruf den Stoffnamen und wenn möglich den "
                    "**UN-Nummer aus dem SDB Abschnitt 14** ansagen — das Gift-Notruf-Zentrum "
                    "kann darüber das Antidot bestimmen.\n\n"
                    "**Verschlucken:** Niemals Erbrechen auslösen, niemals Milch zum Verdünnen "
                    "geben (Aufnahme im Darm beschleunigen sich). Mund ausspülen, ruhig "
                    "halten, Notruf 112 und Giftnotruf des Bundeslandes anrufen.\n\n"
                    "**Auslaufen (kein Brand):** Schadensbereich grosszügig absperren, "
                    "Belüftung erhöhen wenn möglich (Tore auf, Lüfter an), mit chemiekalien-"
                    "beständigem Bindemittel (Vermiculit für Säuren/Laugen, Universal-Vlies "
                    "für Öle) aufnehmen. Das kontaminierte Bindemittel ist Sondermüll und "
                    "geht in ein gekennzeichnetes Spezial-Fass.\n\n"
                    "**Brand:** Bei brennenden Gefahrstoffen niemals Wasserlöscher auf "
                    "Lösemittel-Brand und niemals CO2 auf Metallspäne — Brandklasse-Tabelle "
                    "im Kopf haben (siehe Brandschutz-Schulung). Bei grösseren Mengen sofort "
                    "Halle räumen, Brandschutztüren schliessen, Feuerwehr 112.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Position von Notdusche, Augendusche, Erste-Hilfe-Kasten und nächstem "
                    "Brandmelder kennen — vor der ersten Schicht im Bereich abgehen\n"
                    "2. Bei Unfall mit Hautkontakt sofort 15 Minuten unter fliessendem Wasser "
                    "spülen, parallel die Schichtleitung informieren lassen\n"
                    "3. Bei Augenkontakt sofort Augendusche, mindestens 10 Minuten, "
                    "danach zwingend Augenarzt\n"
                    "4. Beim Notruf Stoffname und wenn möglich UN-Nummer angeben (SDB "
                    "Abschnitt 14), die Leitstelle leitet an das Gift-Informationszentrum weiter\n"
                    "5. Auslaufende Gefahrstoffe niemals mit Wasser wegspülen, sondern mit "
                    "Bindemittel aufnehmen und als Sondermüll entsorgen\n\n"
                    "## Praxisbeispiel\n\n"
                    "In der Werkhalle einer Federnfabrik kippt ein 25-Liter-Kanister mit "
                    "konzentrierter Säurebeize von einem nicht ausreichend gesicherten "
                    "Hubwagen. Etwa fünf Liter laufen aus, zwei Tropfen treffen den Unterarm "
                    "des Staplerfahrers durch den Ärmel. Er reagiert lehrbuchmässig: ruft "
                    "laut den Kollegen, der den Bereich absperrt und Bindemittel holt, geht "
                    "selbst zur Notdusche neben dem Mischplatz, zieht das Hemd aus und spült "
                    "den Unterarm 15 Minuten lang. Der Kollege parallel: Bindemittel auf die "
                    "Lache, Tore auf zur Belüftung, Notruf 112 mit Stoffname Phosphorsäure "
                    "und UN-Nummer aus dem ausgehängten SDB. Der Rettungsdienst übernimmt nach "
                    "fünf Minuten, die Verätzung bleibt oberflächlich, Heilungsdauer drei "
                    "Tage. Ohne Notdusche und ohne sofortiges Spülen wäre die Säure durch die "
                    "Hautschichten gewandert — Operations-Sache statt Pflaster-Sache.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf GefStoffV § 13 *Massnahmen bei Betriebsstörungen* "
                    "(Stand 2024), TRGS 526 *Laboratorien* (Anwendung sinngemäss auf "
                    "Werkstatt-Mischplätze), DGUV Information 213-850 *Sicheres Arbeiten in "
                    "Laboratorien* und Empfehlungen des Giftinformationszentrums-Nord "
                    "(GIZ-Nord, Göttingen)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wie oft muss eine Unterweisung nach § 14 GefStoffV durchgeführt werden?",
                erklaerung="§ 14 Absatz 2 GefStoffV verlangt eine arbeitsplatzbezogene "
                "Unterweisung vor Aufnahme der Tätigkeit und danach mindestens jährlich.",
                optionen=_opts(
                    ("Einmal beim Eintritt, danach nur bei Stoffwechsel", False),
                    ("Mindestens jährlich, arbeitsplatzbezogen", True),
                    ("Alle drei Jahre", False),
                    ("Nur wenn die BG eine Begehung ankündigt", False),
                ),
            ),
            FrageDef(
                text="Welches GHS-Piktogramm kennzeichnet einen ätzenden Stoff wie Natronlauge?",
                erklaerung="GHS05 zeigt zwei Reagenzgläser, aus denen Flüssigkeit auf eine "
                "Hand und ein Material tropft, das davon zerfressen wird.",
                optionen=_opts(
                    ("GHS02 (Flamme)", False),
                    ("GHS05 (Reagenzgläser auf Hand/Material)", True),
                    ("GHS07 (Ausrufezeichen)", False),
                    ("GHS09 (Fisch und Baum)", False),
                ),
            ),
            FrageDef(
                text="Welches Signalwort kennzeichnet die höhere Gefahrenstufe auf einem GHS-Etikett?",
                erklaerung="Es gibt nur zwei Signalwörter — 'Gefahr' steht für die höhere, "
                "'Achtung' für die geringere Gefahrenstufe. Beide gleichzeitig gibt es nie.",
                optionen=_opts(
                    ("Achtung", False),
                    ("Warnung", False),
                    ("Gefahr", True),
                    ("Vorsicht", False),
                ),
            ),
            FrageDef(
                text="Wofür stehen H-Sätze im Etikett bzw. Sicherheitsdatenblatt?",
                erklaerung="H-Sätze (Hazard Statements) beschreiben die Gefahr des Stoffes. "
                "P-Sätze (Precautionary Statements) hingegen beschreiben Schutzmassnahmen.",
                optionen=_opts(
                    ("Herstellerangaben zur Charge", False),
                    ("Hinweise auf die Gefahr (Hazard Statements)", True),
                    ("Höchstmenge im Lager", False),
                    ("Handelsklasse nach REACH", False),
                ),
            ),
            FrageDef(
                text="Wie viele Pflicht-Abschnitte hat ein Sicherheitsdatenblatt nach REACH?",
                erklaerung="REACH-Verordnung Anhang II schreibt 16 Abschnitte in fester "
                "Reihenfolge vor, von Bezeichnung (1) bis sonstige Angaben (16).",
                optionen=_opts(
                    ("10", False),
                    ("12", False),
                    ("16", True),
                    ("20", False),
                ),
            ),
            FrageDef(
                text="In welchem SDB-Abschnitt findest du die richtige Erste-Hilfe-Massnahme?",
                erklaerung="Abschnitt 4 trägt den Titel 'Erste-Hilfe-Massnahmen' und ist "
                "nach Aufnahmewegen (Haut, Auge, Inhalation, Verschlucken) gegliedert.",
                optionen=_opts(
                    ("Abschnitt 2", False),
                    ("Abschnitt 4", True),
                    ("Abschnitt 8", False),
                    ("Abschnitt 13", False),
                ),
            ),
            FrageDef(
                text="Was regelt die TRGS 510?",
                erklaerung="TRGS 510 regelt die Lagerung von Gefahrstoffen in ortsbeweglichen "
                "Behältern, inkl. Mengenschwellen und Zusammenlagerungs-Tabelle der Lagerklassen.",
                optionen=_opts(
                    ("Die Kennzeichnung von Abfällen", False),
                    ("Die Lagerung von Gefahrstoffen in ortsbeweglichen Behältern", True),
                    ("Die Sicherheitsdatenblatt-Pflicht", False),
                    ("Die ärztliche Vorsorge von Beschäftigten", False),
                ),
            ),
            FrageDef(
                text="Welche Reihenfolge gilt nach § 6 GefStoffV bei der Auswahl von Schutzmassnahmen?",
                erklaerung="Das **STOP-Prinzip**: Substitution (S) vor technischen Massnahmen "
                "(T) vor organisatorischen Massnahmen (O) vor persönlicher Schutzausrüstung (P). "
                "PSA ist die letzte Wahl, nicht die erste.",
                optionen=_opts(
                    ("Erst PSA, dann technische Massnahmen", False),
                    ("Substitution vor Technik vor Organisation vor PSA (STOP)", True),
                    ("Reihenfolge spielt keine Rolle, Hauptsache Schutz", False),
                    ("Erst Unterweisung, dann alles andere", False),
                ),
            ),
            FrageDef(
                text="Du findest in der Halle eine Sprühflasche mit unbekannter Flüssigkeit ohne Etikett. Was tust du?",
                erklaerung="Ohne Kennzeichnung darf der Stoff nicht verwendet werden (§ 8 GefStoffV). "
                "Er ist an die Schichtleitung zu melden, die Herkunft muss geklärt werden.",
                optionen=_opts(
                    ("Schnuppern, um den Stoff zu erkennen", False),
                    ("Wegschütten, damit niemand mehr daran kommt", False),
                    ("Nicht benutzen und an die Schichtleitung melden", True),
                    ("Für sich selbst beschriften und weiterverwenden", False),
                ),
            ),
            FrageDef(
                text="Wer hat dir Säurebeize auf den Unterarm gespritzt. Was ist die richtige Sofortmassnahme?",
                erklaerung="Sofort kontaminierte Kleidung entfernen und mindestens 15 Minuten "
                "mit viel Wasser unter der Notdusche spülen — dann erst ärztliche Versorgung.",
                optionen=_opts(
                    ("Mit trockenem Tuch abwischen, dann Salbe auftragen", False),
                    ("Kleidung entfernen, mind. 15 Min Notdusche, dann Arzt", True),
                    ("Mit Mehl bestreuen, um die Säure zu binden", False),
                    ("Mit Natronlauge neutralisieren", False),
                ),
            ),
            FrageDef(
                text="Säurebeize ist auf den Hallenboden ausgelaufen. Wie nimmst du den Stoff auf?",
                erklaerung="Chemikalien-Bindemittel wie Vermiculit oder spezielles Bindevlies "
                "aufnehmen. Wegspülen mit Wasser ist eine Straftat nach § 324a StGB.",
                optionen=_opts(
                    ("Mit dem Wasserschlauch ins Bodenablauf-Gitter spülen", False),
                    ("Mit Sägemehl aufnehmen und in den normalen Restmüll", False),
                    ("Mit Chemikalien-Bindemittel aufnehmen und als Sondermüll entsorgen", True),
                    ("Mit Pressluft in eine Ecke blasen", False),
                ),
            ),
            FrageDef(
                text="Du fülltst Verdünner aus dem 25-Liter-Kanister in eine 1-Liter-Sprühflasche. Welche Pflicht hast du?",
                erklaerung="§ 8 GefStoffV verlangt, dass jedes Standgefäss am Arbeitsplatz "
                "mit Produktname, Piktogramm und Signalwort gekennzeichnet ist — auch beim "
                "Umfüllen für eine einzige Schicht.",
                optionen=_opts(
                    ("Keine, solange du es selbst benutzt", False),
                    ("Neu kennzeichnen mit Produktname, Piktogramm und Signalwort", True),
                    ("Nur mit dem Datum der Umfüllung beschriften", False),
                    ("Den Originalkanister nebendran stellen reicht aus", False),
                ),
            ),
            FrageDef(
                text="Welche Augenspül-Dauer ist bei Säure-/Laugen-Spritzer minimal nötig?",
                erklaerung="Mindestens 10 Minuten kontinuierlich, danach zwingend Augenarzt. "
                "Säure- und Laugenverätzungen können in Minuten zur Erblindung führen.",
                optionen=_opts(
                    ("30 Sekunden", False),
                    ("2 Minuten", False),
                    ("Mindestens 10 Minuten", True),
                    ("Bis es nicht mehr brennt", False),
                ),
            ),
            FrageDef(
                text="Was darfst du auf keinen Fall im selben Auffangbereich lagern?",
                erklaerung="Säuren (LGK 8B sauer) und Laugen (LGK 8B basisch) reagieren beim "
                "Kontakt heftig, teilweise unter Freisetzung von Chlorgas. TRGS 510 verlangt "
                "räumliche oder bauliche Trennung.",
                optionen=_opts(
                    ("Zwei verschiedene Reinigungstücher", False),
                    ("Säurebeize und Natronlauge-Reiniger zusammen", True),
                    ("Zwei Liter Kühlschmierstoff in zwei Kanistern", False),
                    ("Eine Spraydose und einen Pinsel", False),
                ),
            ),
            FrageDef(
                text="Welches GHS-Piktogramm steht für chronische Gesundheitsgefahren wie CMR-Stoffe?",
                erklaerung="GHS08 (Mensch mit Stern auf der Brust) kennzeichnet Stoffe mit "
                "krebserzeugender, erbgutverändernder, reproduktionstoxischer Wirkung sowie "
                "Atemwegssensibilisierung und Aspirationsgefahr.",
                optionen=_opts(
                    ("GHS06 (Totenkopf)", False),
                    ("GHS07 (Ausrufezeichen)", False),
                    ("GHS08 (Mensch mit Stern)", True),
                    ("GHS09 (Fisch und Baum)", False),
                ),
            ),
            FrageDef(
                text="Welcher SDB-Abschnitt nennt den Arbeitsplatzgrenzwert (AGW) und die richtige PSA?",
                erklaerung="Abschnitt 8 'Begrenzung und Überwachung der Exposition / Persönliche "
                "Schutzausrüstung' enthält AGW-Werte, empfohlene Handschuh-Werkstoffe und "
                "Durchbruchszeiten, Brillen-Schutzklasse und Atemschutz-Filter.",
                optionen=_opts(
                    ("Abschnitt 3", False),
                    ("Abschnitt 8", True),
                    ("Abschnitt 11", False),
                    ("Abschnitt 15", False),
                ),
            ),
            FrageDef(
                text="Eine Kollegin trinkt versehentlich aus einer alten Wasserflasche mit Entkalker. Was tust du NICHT?",
                erklaerung="Erbrechen auslösen ist bei ätzenden Stoffen verboten — der Stoff "
                "passiert die Speiseröhre ein zweites Mal und verätzt sie zusätzlich. Mund "
                "ausspülen, Notruf 112, Giftnotruf, ruhig halten.",
                optionen=_opts(
                    ("Mund mit Wasser ausspülen lassen", False),
                    ("Notruf 112 absetzen", False),
                    ("Erbrechen auslösen", True),
                    ("Sicherheitsdatenblatt heraussuchen", False),
                ),
            ),
            FrageDef(
                text="Welcher Grundsatz steht in § 6 GefStoffV bei der Auswahl eines Gefahrstoffs an erster Stelle?",
                erklaerung="Substitution: Der Arbeitgeber muss prüfen, ob der Gefahrstoff "
                "durch einen weniger gefährlichen ersetzt oder das Verfahren ganz geändert "
                "werden kann. TRGS 600 konkretisiert das Vorgehen.",
                optionen=_opts(
                    ("Möglichst günstig einkaufen", False),
                    ("Substitutionsprüfung — gibt es einen weniger gefährlichen Ersatz?", True),
                    ("Möglichst grosse Gebinde wählen, das spart Verpackung", False),
                    ("Den Stoff bevorraten, der die meiste Schicht hält", False),
                ),
            ),
            FrageDef(
                text="Welche Information muss eine Betriebsanweisung nach TRGS 555 enthalten?",
                erklaerung="TRGS 555 verlangt mindestens: Anwendungsbereich, Gefahren für Mensch "
                "und Umwelt, Schutzmassnahmen und Verhaltensregeln, Verhalten im Gefahrfall, "
                "Erste Hilfe und sachgerechte Entsorgung — in verständlicher Sprache am Arbeitsplatz.",
                optionen=_opts(
                    ("Den Einkaufspreis des Stoffes", False),
                    ("Gefahren, Schutzmassnahmen, Verhalten im Notfall, Erste Hilfe, Entsorgung", True),
                    ("Den Lieferantennamen und die Bestellnummer", False),
                    ("Die Telefonnummer des Geschäftsführers", False),
                ),
            ),
            FrageDef(
                text="In der Galvanik tritt ein stechender Geruch auf, dir wird schwindelig. Was tust du?",
                erklaerung="Eigenschutz zuerst — sofort den Bereich verlassen, Kollegen warnen, "
                "Notruf 112 mit Hinweis auf möglichen Gefahrstoff-Austritt. Niemals zurück, "
                "um 'kurz nachzusehen', das ist der häufigste Fehler bei Gas-Unfällen.",
                optionen=_opts(
                    ("Tief durchatmen, um den Stoff zu identifizieren", False),
                    ("Bereich sofort verlassen, Kollegen warnen, Notruf 112", True),
                    ("Fenster schliessen, damit nichts entweicht", False),
                    ("Erst die Schichtleitung anrufen, dann entscheiden", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #7
    KursDef(
        titel="Persönliche Schutzausrüstung (PSA)",
        beschreibung="Unterweisung nach PSA-Benutzungsverordnung. Auswahl, Tragepflicht, Prüfung & Wartung, Atemschutz.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Auswahl & Tragepflicht",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "PSA ist die letzte Verteidigungslinie. Wenn technische Schutzmaßnahmen "
                    "(Einhausung, Absaugung) und organisatorische Maßnahmen (Arbeitsabläufe, "
                    "Trennung) eine Gefährdung nicht vollständig beseitigen, bleibt die "
                    "**persönliche Schutzausrüstung** als drittes und letztes Mittel — "
                    "Sicherheitsschuhe, Schutzbrille, Gehörschutz, Helm, Handschuhe, "
                    "Atemschutz. In diesem Modul lernst du, warum welche PSA wo Pflicht ist, "
                    "wer sie auswählt und bezahlt und was passiert, wenn du sie weglässt.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 3 ArbSchG** — Arbeitgeber muss Gefährdungen primär durch "
                    "technische Maßnahmen beseitigen; PSA ist nachrangig\n"
                    "- **§ 2 PSA-BV** — PSA muss passen, geeignet sein und darf keine "
                    "neue Gefahr schaffen\n"
                    "- **EU-Verordnung 2016/425** — Kategorien I, II, III und CE-Kennzeichnung "
                    "von PSA-Produkten\n"
                    "- **§ 15 ArbSchG** — Beschäftigte sind verpflichtet, bereitgestellte "
                    "PSA bestimmungsgemäß zu benutzen\n\n"
                    "## Was musst du wissen\n\n"
                    "PSA ist nach EU 2016/425 in drei Kategorien eingeteilt — je höher die "
                    "Kategorie, desto strenger die Anforderungen an Herstellung und Prüfung:\n\n"
                    "| Kategorie | Risiko | Beispiele |\n"
                    "|---|---|---|\n"
                    "| I | geringfügig (rückholbar) | einfache Gartenhandschuhe, leichte Sonnenbrille |\n"
                    "| II | mittel | Schutzbrille EN 166, Industriehelm, einfache Sicherheitsschuhe |\n"
                    "| III | dauerhafte Schäden oder Tod | Atemschutz, Auffanggurt, Chemikalienschutz, Lärmschutz |\n\n"
                    "Kategorie-III-PSA löst zwei zusätzliche Pflichten aus: jährliche "
                    "Sachkunde-Prüfung und obligatorische praktische Trageübung in der "
                    "Unterweisung (nicht nur Theorie).\n\n"
                    "In der typischen Industriewerkstatt sind diese PSA-Pakete üblich:\n\n"
                    "- **Sicherheitsschuhe S3** — Stahlkappe, durchtrittsichere Sohle, "
                    "öl- und kraftstoffbeständig; Pflicht in jeder Halle mit Materialtransport\n"
                    "- **Schutzbrille EN 166** — Kennung F (mechanisch) bei Bohren und Schleifen, "
                    "Kennung 3 (Flüssigkeitsspritzer) im Galvanik-Bereich, Schweißerschutzschild "
                    "DIN EN 175 am Schweißplatz\n"
                    "- **Gehörschutz** — ab 80 dB(A) zur Verfügung stellen, ab 85 dB(A) Tragepflicht\n"
                    "- **Schutzhandschuhe** — EN 388 (mechanisch), EN 374 (Chemie), niemals "
                    "an rotierenden Maschinen (Einzugsgefahr)\n"
                    "- **Atemschutz** — beim Trocken-Schleifen, Schweißen, Lackieren\n\n"
                    "Die **Kosten für PSA trägt allein der Arbeitgeber** (§ 3 Abs. 3 ArbSchG). "
                    "Vom Lohn abziehen ist verboten — auch nicht teilweise, auch nicht bei "
                    "Verlust durch Eigenverschulden ohne vorherige schriftliche Vereinbarung. "
                    "Reinigung und Ersatz fallen ebenfalls auf den Betrieb.\n\n"
                    "## Was musst du tun\n\n"
                    "Beim Betreten eines PSA-pflichtigen Bereichs:\n\n"
                    "1. Vor dem Eintreten die am Eingang ausgehängte Piktogramm-Tafel beachten\n"
                    "2. Alle dort gezeigten PSA anlegen, bevor du die Halle betrittst\n"
                    "3. Sitz prüfen: Helm fest, Brille dicht, Schuhe geschnürt, Gehörschutz tief im Ohr\n"
                    "4. Beschädigte oder verlorene PSA sofort beim Vorgesetzten melden und ersetzen lassen\n"
                    "5. PSA niemals an Kollegen weitergeben, sie ist personenbezogen angepasst\n"
                    "6. Nach Schichtende fachgerecht reinigen und am vorgesehenen Platz lagern\n\n"
                    "Wenn du eine PSA als unpassend oder schlecht empfindest (drückt, beschlägt, "
                    "rutscht), melde das. Du hast nach § 17 ArbSchG ein **Vorschlagsrecht**, "
                    "und der Betrieb muss reagieren — schlecht sitzende PSA wird oft weggelegt, "
                    "und das ist die häufigste Ursache von Unfällen.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Schlosser in einer Metallverarbeitung zieht beim kurzen Nachsetzen "
                    "eines Werkstücks die Schutzbrille hoch — 'nur dreißig Sekunden'. Im "
                    "selben Moment bricht ein Schleifscheiben-Splitter ab und trifft ihn ins "
                    "rechte Auge. Sehkraft 30 Prozent, Frührente mit 47. Die Berufsgenossenschaft "
                    "stellt fest: Brille hatte CE und EN 166 F, war vorhanden, Unterweisung "
                    "erfolgt. Schaden trägt die BG — aber der Mann ist Invalide. Lehre: "
                    "Schutzbrille bleibt unten, *immer*, auch beim Nachsetzen. Disziplin gewinnt.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf PSA-Benutzungsverordnung §§ 2-3, "
                    "EU-Verordnung 2016/425 (PSA-Verordnung), § 3 und § 15 ArbSchG sowie "
                    "DGUV Regel 112-189/190 *Benutzung von Augen- und Atemschutz*."
                ),
            ),
            ModulDef(
                titel="Prüfung & Wartung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Eine durchgescheuerte Auffanggurt-Naht, ein Helm mit einem Haarriss, "
                    "ein Sicherheitsschuh mit abgelaufener Sohle — defekte PSA bietet das "
                    "Gefühl von Schutz, aber keinen Schutz. Damit das nicht passiert, sind "
                    "Prüfung, Wartung und Aussonderung gesetzlich geregelt. Du lernst, was "
                    "du selbst täglich prüfen musst, wann eine **Sachkundige Person** "
                    "ranmuss und wann PSA in den Müll gehört.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 2 Abs. 4 PSA-BV** — Arbeitgeber hat für Instandhaltung, Reparatur, "
                    "Ersatz und Lagerung zu sorgen\n"
                    "- **DIN EN 365** — PSA gegen Absturz ist mindestens einmal jährlich "
                    "durch eine sachkundige Person zu prüfen\n"
                    "- **DGUV Grundsatz 312-906** — Qualifikation der Sachkundigen Person "
                    "für PSA gegen Absturz\n"
                    "- **DGUV Regel 112-189** — Benutzung von Augen- und Gesichtsschutz: "
                    "Sichtprüfung vor jedem Tragen\n\n"
                    "## Was musst du wissen\n\n"
                    "Es gibt drei Prüfebenen mit unterschiedlichen Verantwortlichen:\n\n"
                    "| Ebene | Wer prüft | Wann | Was |\n"
                    "|---|---|---|---|\n"
                    "| Vor-Gebrauchs-Prüfung | du selbst | vor jedem Tragen | Sichtkontrolle, offensichtliche Schäden |\n"
                    "| Sachkundige Prüfung | ausgebildete:r Prüfer:in | jährlich (PSA Kat. III) | Detailprüfung mit Protokoll |\n"
                    "| Hersteller-Inspektion | Hersteller / autorisierte Werkstatt | nach Vorgabe (z. B. alle 5 Jahre) | Demontage, Funktionstest, Rezertifizierung |\n\n"
                    "Die **Sachkundige Person** ist nach DGUV Grundsatz 312-906 geschult, "
                    "kennt die Herstellervorgaben und führt ein Prüfbuch. Ohne dokumentierte "
                    "Prüfung verliert die Versicherung im Unfallfall den Regress — und der "
                    "Arbeitgeber haftet persönlich.\n\n"
                    "Aussonderungs-Kriterien gelten kategorisch:\n\n"
                    "- **Auffanggurt nach Sturz** — sofort aussondern, auch ohne sichtbare Schäden\n"
                    "- **Helm nach Schlag** — aussondern, auch wenn 'nur einmal hingefallen'\n"
                    "- **Filter-Atemschutz** — Ablaufdatum auf Filter beachten, in der Regel "
                    "6 bis 12 Monate nach Anbruch\n"
                    "- **Sicherheitsschuh-Sohle** — bei deutlichem Profilabrieb oder durchgelaufenem "
                    "Innenfutter\n"
                    "- **Schutzbrille** — bei tiefen Kratzern, die das Sichtfeld beeinträchtigen\n\n"
                    "Lagerung beeinflusst die Lebensdauer erheblich. PSA gegen Absturz, "
                    "Atemschutz und Chemikalienhandschuhe gehören in einen trockenen, "
                    "lichtgeschützten Schrank zwischen 5 und 25 Grad Celsius. Niemals im "
                    "Auto im Sommer, niemals neben Lösemitteln, niemals nass eingelagert.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jedem Tragen Sichtkontrolle in der gleichen Reihenfolge:\n\n"
                    "1. Helm: Risse im Material, Schweißband intakt, Kinnriemen funktioniert\n"
                    "2. Schutzbrille: keine Kratzer im Blickfeld, Bügel-Scharnier fest, "
                    "Seitenschutz vorhanden\n"
                    "3. Gehörschutz: Stöpsel sauber und elastisch, Bügel-Polster nicht hart\n"
                    "4. Handschuhe: keine Löcher, Nähte fest, Innenfutter trocken\n"
                    "5. Sicherheitsschuhe: Sohle griffig, Verschluss funktioniert, keine "
                    "durchgescheuerten Stellen\n"
                    "6. Auffanggurt: Bandmaterial ohne Schnitte, Schnallen funktionieren, "
                    "Etikett lesbar, Prüfsiegel aktuell\n\n"
                    "Wenn ein einziger Punkt nicht passt: PSA aussondern, sofort Ersatz "
                    "anfordern, kein 'macht heute noch'. Defekte PSA gehört in einen klar "
                    "beschrifteten Ausschuss-Behälter, nicht zurück ins Lager — sonst greift "
                    "der nächste Kollege.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem Werkzeugbau wird ein Auffanggurt aus dem Lager geholt für eine "
                    "Wartungsarbeit am Hallenkran. Der Monteur merkt beim Anlegen, dass das "
                    "Etikett mit dem Prüfdatum fehlt. Er informiert den Vorgesetzten, statt "
                    "den Gurt zu nutzen. Eine Stichprobe zeigt: der Gurt war zuletzt vor "
                    "drei Jahren geprüft worden, die Sachkundige Person hatte gewechselt und "
                    "die Prüfintervalle waren durchgerutscht. Resultat: alle 14 Auffanggurte "
                    "des Betriebs werden zur Prüfung gegeben, drei werden ausgesondert "
                    "(versteckte Materialermüdung). Kein Unfall — wegen einer Sekunde "
                    "Aufmerksamkeit beim Anlegen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf PSA-Benutzungsverordnung § 2 Abs. 4, "
                    "DIN EN 365 *PSA gegen Absturz — Allgemeine Anforderungen*, "
                    "DGUV Grundsatz 312-906 *Sachkundige Person für PSA gegen Absturz* "
                    "sowie DGUV Regel 112-189 *Benutzung von Augen- und Gesichtsschutz*."
                ),
            ),
            ModulDef(
                titel="Atemschutz im Detail",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Schweißrauch enthält Mangan, Chrom-VI und Nickel-Oxide — alles "
                    "krebserregend nach TRGS 528. Beim Trocken-Schleifen von Edelstahl "
                    "atmest du Quarz-Feinstaub ein. Beim Lackieren kommen Isocyanate dazu. "
                    "Atemschutz ist deshalb keine optionale Vorsicht, sondern Voraussetzung "
                    "für jahrzehntelanges gesundes Arbeiten. Du lernst, welcher Atemschutz "
                    "welche Gefahr abdeckt, wie lange du ihn tragen darfst und warum "
                    "Stoppelbart und Atemschutz nicht zusammen funktionieren.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **DGUV Regel 112-190** — Benutzung von Atemschutzgeräten "
                    "(Gebrauchsdauer, Eignung, Unterweisung)\n"
                    "- **DIN EN 149** — Klassifizierung filtrierender Halbmasken (FFP1-FFP3)\n"
                    "- **DIN EN 143** — Partikelfilter mit Wechselanschluss (P1-P3)\n"
                    "- **TRGS 528** — Schweißtechnische Arbeiten (krebserzeugende Stoffe)\n"
                    "- **ArbMedVV** — Arbeitsmedizinische Vorsorge G 26.1 bis G 26.3 vor "
                    "Atemschutz-Einsatz\n\n"
                    "## Was musst du wissen\n\n"
                    "Atemschutz wird nach der Art der Gefährdung gewählt. Drei Hauptklassen:\n\n"
                    "| Klasse | Wovor schützt sie | Vielfaches des Grenzwerts | Beispiel-Einsatz |\n"
                    "|---|---|---|---|\n"
                    "| FFP1 / P1 | grober Staub, ungiftig | bis 4-fach AGW | Mauern, Mehl, Holzstaub Weichholz |\n"
                    "| FFP2 / P2 | gesundheitsschädlicher Feinstaub | bis 10-fach AGW | Quarz, Metallstaub, Hartholz, Bakterien |\n"
                    "| FFP3 / P3 | giftig, krebserregend, radioaktiv | bis 30-fach AGW | Schweißrauch, Chrom-VI, Asbest, Schimmelsporen |\n\n"
                    "Filtrierende Halbmasken (FFP) sind Einwegprodukte; Vollmasken mit "
                    "Wechselfilter (P) sind langlebiger und schützen zusätzlich die Augen. "
                    "Bei Gasen statt Partikeln greifen andere Filterklassen: A (organische "
                    "Gase), B (anorganische Gase wie Chlor), E (saure Gase), K (Ammoniak), "
                    "farbcodiert braun, grau, gelb, grün.\n\n"
                    "Atemschutz **belastet den Kreislauf**. Nach DGUV Regel 112-190 ist die "
                    "Tragezeit begrenzt und an eine arbeitsmedizinische Vorsorge gekoppelt:\n\n"
                    "- **G 26.1** — leichter Atemschutz bis 3 kg, z. B. Halbmaske mit Filter\n"
                    "- **G 26.2** — mittelschwerer Atemschutz, z. B. Vollmaske oder Gebläsegerät\n"
                    "- **G 26.3** — schwerer Atemschutz, z. B. umluftunabhängige Pressluftgeräte\n\n"
                    "Eine Eignungs-Untersuchung beim Betriebsarzt ist Pflicht vor Einsatz. "
                    "Die Tragezeit wird in der Gefährdungsbeurteilung festgelegt, typisch "
                    "75 Minuten Maximum dann Pause, nie an mehr als zwei aufeinanderfolgenden "
                    "Werktagen voll ausgenutzt.\n\n"
                    "**Dichtsitz** ist die Voraussetzung für jeden Schutz. Bartwuchs zwischen "
                    "Maskenrand und Haut macht selbst die teuerste FFP3 wirkungslos — der "
                    "Luftstrom sucht sich den Weg des geringsten Widerstands und geht an der "
                    "Maske vorbei. Glattrasiert ist Pflicht im Maskenbereich.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jedem Atemschutz-Einsatz:\n\n"
                    "1. Filter-Verpackungs- und Ablaufdatum prüfen, Filter vor Erstgebrauch "
                    "datieren\n"
                    "2. Maske auf Risse, brüchige Bänder und verklebte Ventile sichten\n"
                    "3. Glattrasieren im Dichtungsbereich, Brillenträger ggf. Maskenbrille verwenden\n"
                    "4. Bänder über den Kopf legen, Nasenklemme an die Nasenform anpassen\n"
                    "5. Dichtsitz-Test: Handflächen leicht über die Filter, einatmen — die "
                    "Maske muss sich ans Gesicht saugen\n"
                    "6. Bei Schwindel, Atemnot oder Übelkeit den Bereich sofort verlassen "
                    "und Maske absetzen\n\n"
                    "Nach Gebrauch: Filter datieren mit Anbruch-Datum, Maske mit milder Seife "
                    "reinigen, lichtgeschützt und trocken lagern. Filter werden in der Regel "
                    "nach 6 Monaten ab Anbruch unbrauchbar, auch wenn sie nicht voll ausgelastet "
                    "waren.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Schlosserei schweißt ein Mitarbeiter seit 12 Jahren Edelstahl. "
                    "Vorgaben für FFP3 oder Gebläsehelm bestehen seit Jahren, der Kollege "
                    "hat den Helm aber als 'unbequem und heiß' regelmäßig weggelegt. Bei der "
                    "G-26-Vorsorge zeigt die Lungenfunktion deutliche Einschränkungen, "
                    "Krebsmarker im Blut sind erhöht. Diagnose: chronisch-obstruktive "
                    "Lungenerkrankung in fortgeschrittenem Stadium, Verdacht auf "
                    "Berufskrankheit BK 4109 (Chrom-VI). Der Mann verliert seine "
                    "Arbeitsfähigkeit. Der Betrieb investiert daraufhin in einen "
                    "Gebläsehelm mit Frischluftzufuhr für jeden Schweißplatz — Tragekomfort "
                    "und Schutz ohne Kompromiss. Lehre: günstiger Atemschutz wird "
                    "weggelegt, teurer wird getragen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Regel 112-190 *Benutzung von Atemschutzgeräten* "
                    "(Ausgabe 2021), DGUV Regel 112-189 *Benutzung von Augen- und "
                    "Gesichtsschutz*, DIN EN 149 und DIN EN 143 sowie TRGS 528 "
                    "*Schweißtechnische Arbeiten* und ArbMedVV-Grundsätze G 26.1-G 26.3."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="In welche Kategorie nach EU 2016/425 fällt ein Auffanggurt für Arbeiten in der Höhe?",
                erklaerung="Kategorie III umfasst PSA gegen tödliche oder irreversible "
                "Risiken — dazu gehört jeder Absturzschutz. Daraus folgt jährliche "
                "Sachkunde-Prüfung und obligatorische Trageübung.",
                optionen=_opts(
                    ("Kategorie I (geringfügige Gefährdung)", False),
                    ("Kategorie II (mittlere Gefährdung)", False),
                    ("Kategorie III (Lebensgefahr / irreversible Schäden)", True),
                    ("Kategorie IV (Sonderkategorie für Höhenarbeit)", False),
                ),
            ),
            FrageDef(
                text="Wer trägt nach § 3 Abs. 3 ArbSchG die Kosten für PSA?",
                erklaerung="PSA-Kosten dürfen Beschäftigten nicht aufgebürdet werden, "
                "weder direkt noch über Lohnabzug. Auch Reinigung und Ersatz gehen "
                "auf den Arbeitgeber.",
                optionen=_opts(
                    ("Beschäftigte zu 100 Prozent", False),
                    ("Arbeitgeber zu 100 Prozent", True),
                    ("Hälftig geteilt zwischen beiden", False),
                    ("Berufsgenossenschaft", False),
                ),
            ),
            FrageDef(
                text="Welche Schutzbrillen-Kennung nach EN 166 brauchst du beim Bohren und Schleifen?",
                erklaerung="EN 166 F steht für mechanische Festigkeit bei Aufprall mit "
                "45 m/s — passend für fliegende Späne. Kennung 3 wäre für Flüssigkeitsspritzer.",
                optionen=_opts(
                    ("EN 166 F (mechanische Festigkeit)", True),
                    ("EN 166 3 (Flüssigkeitsspritzer)", False),
                    ("EN 166 8 (Lichtbogen)", False),
                    ("EN 166 9 (Metallspritzer)", False),
                ),
            ),
            FrageDef(
                text="Du betrittst eine PSA-pflichtige Halle und dein Gehörschutz fehlt. Was tust du?",
                erklaerung="§ 15 ArbSchG verpflichtet zur bestimmungsgemäßen Nutzung "
                "bereitgestellter PSA. Ohne komplette PSA bleibst du draußen und holst Ersatz.",
                optionen=_opts(
                    ("Trotzdem reingehen, ist ja nur ein kurzer Weg", False),
                    ("Mit den Fingern in den Ohren durchqueren", False),
                    ("Bereich nicht betreten, Ersatz beim Vorgesetzten anfordern", True),
                    ("Mit der Hand am Ohr durchgehen, das reicht", False),
                ),
            ),
            FrageDef(
                text="Ab welchem Lärmpegel ist Gehörschutz zwingend zu tragen?",
                erklaerung="LärmVibrationsArbSchV: ab 85 dB(A) Tragepflicht. Ab 80 dB(A) "
                "muss der Arbeitgeber Gehörschutz anbieten, ist aber noch nicht Tragepflicht.",
                optionen=_opts(
                    ("Ab 65 dB(A)", False),
                    ("Ab 80 dB(A)", False),
                    ("Ab 85 dB(A)", True),
                    ("Ab 95 dB(A)", False),
                ),
            ),
            FrageDef(
                text="Welche FFP-Klasse brauchst du beim Schweißen von Edelstahl (Chrom-VI-haltiger Schweißrauch)?",
                erklaerung="Chrom-VI ist krebserzeugend nach TRGS 528. Nur FFP3 (oder "
                "Gebläsehelm) bietet Schutz bis 30-fachem AGW gegen toxische Aerosole.",
                optionen=_opts(
                    ("FFP1", False),
                    ("FFP2", False),
                    ("FFP3 oder Gebläsehelm", True),
                    ("Einfache Stoffmaske", False),
                ),
            ),
            FrageDef(
                text="Warum funktioniert eine Filtermaske bei Drei-Tage-Bart nicht zuverlässig?",
                erklaerung="Der Luftstrom nimmt den Weg des geringsten Widerstands. Schon "
                "Stoppeln zwischen Maskenrand und Haut machen den Dichtsitz wirkungslos.",
                optionen=_opts(
                    ("Der Bart hält Partikel zurück, das ist sogar besser", False),
                    ("Spielt keine Rolle, die Bänder spannen die Maske ans Gesicht", False),
                    ("Bartwuchs verhindert den Dichtsitz, Luft umgeht den Filter", True),
                    ("Der Bart färbt die Maske von innen schwarz, sie wird unbrauchbar", False),
                ),
            ),
            FrageDef(
                text="Welche arbeitsmedizinische Vorsorge ist Pflicht vor Einsatz von Vollmasken mit Filter?",
                erklaerung="G 26.2 deckt mittelschweren Atemschutz wie Vollmasken oder "
                "Gebläsegeräte ab. G 26.1 reicht für leichten Atemschutz unter 3 kg.",
                optionen=_opts(
                    ("G 26.1 (leichter Atemschutz)", False),
                    ("G 26.2 (mittelschwerer Atemschutz)", True),
                    ("G 41 (Höhenarbeit)", False),
                    ("Keine Vorsorge nötig, freiwillig", False),
                ),
            ),
            FrageDef(
                text="Wie oft muss PSA gegen Absturz nach DIN EN 365 mindestens geprüft werden?",
                erklaerung="DIN EN 365 fordert mindestens jährliche Sachkunde-Prüfung mit "
                "Protokoll. Nach Sturzbelastung sofort und unabhängig von der Frist.",
                optionen=_opts(
                    ("Alle 5 Jahre", False),
                    ("Alle 2 Jahre", False),
                    ("Mindestens einmal jährlich durch sachkundige Person", True),
                    ("Nur bei sichtbarem Verschleiß", False),
                ),
            ),
            FrageDef(
                text="Dein Helm ist gestern aus 2 m Höhe heruntergefallen, sichtbare Schäden gibt es nicht. Was tust du?",
                erklaerung="Industriehelme sind nach Schlagbelastung auszusondern, "
                "auch ohne sichtbaren Schaden. Materialschwächen entstehen unsichtbar im "
                "Polymer.",
                optionen=_opts(
                    ("Weiter benutzen, kein Riss zu sehen", False),
                    ("Aussondern und Ersatz anfordern", True),
                    ("Nur die Innenausstattung wechseln", False),
                    ("Bis zur nächsten Jahresprüfung benutzen", False),
                ),
            ),
            FrageDef(
                text="Wo gehört defekte PSA hin?",
                erklaerung="Defekte PSA muss klar gekennzeichnet aus dem Verkehr "
                "gezogen werden, sonst greift versehentlich der nächste Kollege.",
                optionen=_opts(
                    ("Zurück ins normale PSA-Lager mit Klebeband-Hinweis", False),
                    ("In den klar beschrifteten Ausschuss-Behälter", True),
                    ("In die Abfalltrennung Restmüll", False),
                    ("In den persönlichen Spind als Reserve", False),
                ),
            ),
            FrageDef(
                text="Welches Markierungs-Kürzel weisen typische Industrie-Sicherheitsschuhe für die Werkstatt aus?",
                erklaerung="S3 ist Standard in der Industrie: Stahlkappe, durchtrittsichere "
                "Sohle, antistatisch, geschlossener Fersenbereich, öl- und kraftstoffbeständige Sohle.",
                optionen=_opts(
                    ("SB (Grundausführung mit Stahlkappe)", False),
                    ("S1 (Stahlkappe, antistatisch, aber keine durchtrittsichere Sohle)", False),
                    ("S3 (Stahlkappe, durchtrittsichere Sohle, öl- und kraftstoffbeständig)", True),
                    ("O1 (ohne Stahlkappe, Berufsschuh)", False),
                ),
            ),
            FrageDef(
                text="Du sollst kurz an einer rotierenden Bohrmaschine ein Span entfernen — was ist mit deinen Handschuhen?",
                erklaerung="An rotierenden Werkzeugen sind Handschuhe verboten — die "
                "Einzugsgefahr ist tödlich, das ganze Bauteil zieht in Sekunden in die "
                "Maschine.",
                optionen=_opts(
                    ("Schnittfeste Handschuhe der Stufe 5 anziehen", False),
                    ("Dünne Stoffhandschuhe für besseren Griff", False),
                    ("Handschuhe ausziehen, Schutzbrille bleibt auf, Maschine abschalten vor dem Eingriff", True),
                    ("Egal welche Handschuhe, Hauptsache überhaupt welche", False),
                ),
            ),
            FrageDef(
                text="Wann darf ein Filter-Atemschutz nach Anbruch noch verwendet werden?",
                erklaerung="Partikelfilter sind nach Anbruch in der Regel 6 Monate "
                "verwendbar, auch wenn sie nicht voll genutzt wurden. Datum auf den "
                "Filter notieren.",
                optionen=_opts(
                    ("Bis er optisch verfärbt ist", False),
                    ("Solange er noch verschlossen verpackt ist", False),
                    ("In der Regel bis 6 Monate nach Anbruch, Datum notieren", True),
                    ("Bis das Mindesthaltbarkeitsdatum auf der Originalverpackung erreicht ist", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege bittet dich, ihm 'kurz deine Schutzbrille zu leihen'. Wie reagierst du?",
                erklaerung="PSA ist personenbezogen angepasst (Sitz, Sehstärke, Hygiene). "
                "Der Betrieb muss jedem eine eigene zur Verfügung stellen — § 2 PSA-BV.",
                optionen=_opts(
                    ("Ausleihen, wenn die nächsten Minuten kein Risiko bestehen", False),
                    ("Ablehnen, eigene PSA bleibt persönlich; Ersatz im Lager anfordern", True),
                    ("Ausleihen, aber nur gegen Pfand", False),
                    ("Ausleihen, wenn die Brille vorher kurz desinfiziert wird", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet die Kennung 'EN 388' auf einem Schutzhandschuh?",
                erklaerung="EN 388 ist die Norm für mechanische Risiken — sie zeigt mit "
                "Ziffern Abriebfestigkeit, Schnittfestigkeit, Reißfestigkeit, "
                "Stichfestigkeit (z. B. 4-5-4-3).",
                optionen=_opts(
                    ("Schutz gegen Chemikalien", False),
                    ("Schutz gegen mechanische Risiken (Abrieb, Schnitt, Reiß, Stich)", True),
                    ("Schutz gegen Hitze und Flammen", False),
                    ("Schutz gegen Mikroorganismen", False),
                ),
            ),
            FrageDef(
                text="Welches der folgenden Beispiele ist KEINE PSA der Kategorie III?",
                erklaerung="Eine einfache Sonnenbrille schützt vor geringfügigen Gefahren "
                "und gehört zu Kategorie I. Atemschutz, Auffanggurt und Chemikalienhandschuhe "
                "sind dagegen Kategorie III.",
                optionen=_opts(
                    ("Atemschutzhalbmaske FFP3", False),
                    ("Auffanggurt nach EN 361", False),
                    ("Einfache Sonnenbrille ohne Seitenschutz", True),
                    ("Chemikalienschutzhandschuhe nach EN 374", False),
                ),
            ),
            FrageDef(
                text="Warum darf PSA gegen Absturz niemals in der Sonne im PKW gelagert werden?",
                erklaerung="UV-Strahlung und Temperaturen über 60 Grad Celsius schädigen "
                "die Polyamid-Bänder. Materialermüdung bleibt unsichtbar, wird im Sturz "
                "tödlich.",
                optionen=_opts(
                    ("Wegen Diebstahlrisiko", False),
                    ("UV-Strahlung und Hitze schwächen die Polyamid-Bänder unsichtbar", True),
                    ("Wegen Geruchsentwicklung im Kofferraum", False),
                    ("Wegen vorgeschriebener Lagerung im Pkw-Werkzeugkasten", False),
                ),
            ),
            FrageDef(
                text="Du merkst nach 30 Minuten unter Atemschutz leichten Schwindel. Was ist richtig?",
                erklaerung="Atemschutz belastet den Kreislauf. Erste Schwindel-Anzeichen "
                "bedeuten: Bereich verlassen, Maske ab, Pause, ggf. Betriebsarzt. Nicht "
                "wegdrücken.",
                optionen=_opts(
                    ("Durchhalten, vergeht meist von selbst", False),
                    ("Bereich verlassen, Maske absetzen, Pause machen, ggf. melden", True),
                    ("Maske leicht abnehmen für frische Luft, weiterarbeiten", False),
                    ("Zucker essen und weiter", False),
                ),
            ),
            FrageDef(
                text="Bei welcher PSA-Kategorie ist eine praktische Trageübung in der Unterweisung verpflichtend?",
                erklaerung="§ 3 PSA-BV fordert bei PSA gegen tödliche oder irreversible "
                "Risiken (Kategorie III) eine praktische Trageübung — Theorie allein "
                "reicht nicht.",
                optionen=_opts(
                    ("Kategorie I", False),
                    ("Kategorie II", False),
                    ("Kategorie III", True),
                    ("Bei keiner Kategorie verpflichtend", False),
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
                    "## Worum geht's?\n\n"
                    "Eine CNC-Fräse ohne Lichtschranke ist kein Werkzeug, sondern eine "
                    "Amputations-Maschine. Eine Presse ohne Zweihandsteuerung kostet "
                    "Finger. Jede Maschine in deiner Halle hat aus gutem Grund "
                    "Schutzeinrichtungen — wenn du sie verstehst, kannst du sicher "
                    "arbeiten. Wenn du sie manipulierst oder umgehst, wird aus der "
                    "Maschine ein Risiko für dich und ein Strafbestand für den "
                    "Arbeitgeber.\n\n"
                    "Du lernst, welche Arten von Schutzeinrichtungen es gibt, wie sie "
                    "funktionieren und woran du erkennst, dass eine Schutzeinrichtung "
                    "defekt oder manipuliert ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 12 BetrSichV** — Unterweisung zu Gefährdungen an Arbeitsmitteln\n"
                    "- **§ 8 BetrSichV** — Grundlegende Schutzmaßnahmen an Arbeitsmitteln\n"
                    "- **Maschinenrichtlinie 2006/42/EG** — CE-Konformität von Maschinen "
                    "(ab 20.01.2027 abgelöst durch Maschinenverordnung EU 2023/1230)\n"
                    "- **DIN EN ISO 13849-1** — Sicherheitsbezogene Steuerungsteile, "
                    "Performance Level PL a bis e\n"
                    "- **DIN EN ISO 14120** — Trennende Schutzeinrichtungen\n\n"
                    "## Was musst du wissen\n\n"
                    "Schutzeinrichtungen werden in zwei Hauptgruppen geteilt: trennende "
                    "und nicht-trennende. *Trennende* halten dich räumlich vom "
                    "Gefahrenbereich fern — eine feste Verkleidung am Antriebsstrang "
                    "oder eine verriegelte Tür am Roboterzaun. *Nicht-trennende* "
                    "erkennen, dass du dich näherst, und schalten ab — Lichtschranke, "
                    "Lichtgitter, Trittmatte, Laserscanner.\n\n"
                    "Typische Beispiele aus der Industrie:\n\n"
                    "| Schutzeinrichtung | Funktion | Typischer Einsatz |\n"
                    "|---|---|---|\n"
                    "| Trennende Schutztür mit Verriegelung | Maschine stoppt, sobald die Tür geöffnet wird | CNC-Bearbeitungszentrum, Roboterzelle |\n"
                    "| Lichtschranke / Lichtgitter | Strahl unterbrochen = Stopp-Befehl | Pressen, Stanzen, Robotermontage |\n"
                    "| Zweihandsteuerung | Beide Hände am Bedienpult, beide außerhalb des Gefahrenbereichs | Exzenter- und Hydraulikpressen |\n"
                    "| Not-Halt-Taster (rot/gelb) | Stillsetzen im Notfall, Selbsthaltung bis Reset | Jede Maschine ab geringer Gefährdung |\n"
                    "| Trittmatte / Schaltleiste | Druck oder Berührung löst Stopp aus | Förderanlagen, Pressenumfeld |\n\n"
                    "Wichtig: Eine Schutzeinrichtung ist nur so gut wie ihre **Kategorie** "
                    "nach DIN EN ISO 13849. PL e (Performance Level e) bedeutet höchste "
                    "Sicherheit, PL a die geringste. Was deine Maschine braucht, steht in "
                    "der Gefährdungsbeurteilung — du musst es nicht selbst entscheiden, "
                    "aber du darfst dich darauf verlassen.\n\n"
                    "Eine **manipulierte Schutzeinrichtung** — Lichtschranke mit Klebeband "
                    "überbrückt, Türkontakt mit Magnet getäuscht, Zweihandsteuerung "
                    "mit Holzkeil festgesetzt — ist eine Ordnungswidrigkeit nach "
                    "**§ 23 ArbSchG** mit Bußgeldern bis 30.000 Euro für dich "
                    "persönlich. Kommt es zu einem Unfall, drohen zusätzlich "
                    "**fahrlässige Körperverletzung (§ 229 StGB)** oder im Todesfall "
                    "**fahrlässige Tötung (§ 222 StGB)**.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jedem Maschinenstart:\n\n"
                    "1. Prüfe, ob alle Schutzeinrichtungen vorhanden und unbeschädigt sind\n"
                    "2. Teste den Not-Halt-Taster mindestens einmal pro Schicht\n"
                    "3. Prüfe Lichtschranken durch kurzes Unterbrechen des Strahls — die Maschine muss stoppen\n"
                    "4. Melde fehlende Schilder, gebrochene Plexiglas-Scheiben oder klemmende Türen sofort\n"
                    "5. Starte nie eine Maschine, wenn eine Schutzeinrichtung deaktiviert ist\n\n"
                    "Wenn du Manipulation entdeckst — bei einem Kollegen oder von der "
                    "Schicht davor — sag es der Schichtleitung oder dem Sicherheits"
                    "beauftragten. Das ist keine Petze, sondern deine Pflicht nach "
                    "**§ 16 ArbSchG**.\n\n"
                    "## Praxisbeispiel\n\n"
                    "An einer Exzenterpresse in der Blechbearbeitung ist die Lichtschranke "
                    "wiederholt ausgelöst, weil der Bediener das Werkstück beim Einlegen "
                    "zu nah am Strahl geführt hat. Statt die Werkstück-Auflage anzupassen, "
                    "klebt er die Lichtschranke mit zwei Streifen Gewebeband ab — *'nur "
                    "für diese Serie, dann mach ichs wieder rückgängig'*. Drei Stunden "
                    "später steht ein Kollege im Gefahrenbereich, weil er einen "
                    "Werkzeugwechsel diskutieren will. Die Presse hätte ihn nicht "
                    "abgesichert. Der Sicherheitsbeauftragte entdeckt das Klebeband bei "
                    "der Rundgangskontrolle, die Presse wird sofort stillgelegt. "
                    "Disziplinar: Abmahnung für den Bediener, OWi-Verfahren gegen den "
                    "Schichtleiter, der die Manipulation geduldet hat.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BetrSichV (Stand 2024), Maschinenrichtlinie "
                    "2006/42/EG bzw. Maschinenverordnung EU 2023/1230 (gültig ab "
                    "20.01.2027) sowie DIN EN ISO 13849-1 und DIN EN ISO 14120. "
                    "Ergänzend: DGUV Information 209-007 *Sicherheit von Werkzeug"
                    "maschinen*."
                ),
            ),
            ModulDef(
                titel="Lockout-Tagout (LOTO)",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Jeder fünfte tödliche Arbeitsunfall in deutschen Betrieben "
                    "passiert nicht beim normalen Maschinenbetrieb, sondern bei "
                    "Wartung, Reinigung oder Störungsbeseitigung — also genau dann, "
                    "wenn die Schutzeinrichtungen umgangen werden müssen, um an die "
                    "Mechanik zu kommen. **Lockout-Tagout** (kurz LOTO) ist das "
                    "Verfahren, das verhindert, dass jemand die Maschine wieder "
                    "einschaltet, während du noch mit dem Kopf zwischen den Walzen "
                    "steckst.\n\n"
                    "Du lernst, was LOTO ist, wann du es anwenden musst und welche "
                    "fünf Schritte das Verfahren bei elektrischen Anlagen umfasst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 BetrSichV** — Instandhaltung, Reinigung, Störungs"
                    "beseitigung sind sicher zu organisieren\n"
                    "- **§ 12 BetrSichV** — Unterweisung der Beschäftigten\n"
                    "- **TRBS 1112** — Technische Regel für Betriebssicherheit, "
                    "Instandhaltung\n"
                    "- **§ 6 DGUV Vorschrift 3** — Arbeiten an elektrischen Anlagen "
                    "nur im spannungsfreien Zustand (5 Sicherheitsregeln)\n"
                    "- **DGUV Information 209-015** — Instandhaltung sicher und "
                    "praxisgerecht durchführen\n\n"
                    "## Was musst du wissen\n\n"
                    "LOTO heißt wörtlich *abschließen und beschildern*. Der "
                    "Gedanke: Wer an einer Maschine arbeitet, bringt sein eigenes "
                    "Schloss am Hauptschalter an und nimmt den einzigen Schlüssel "
                    "selbst mit. Niemand anderes kann die Maschine einschalten, "
                    "solange dein Schloss hängt. Ein Schild mit deinem Namen, "
                    "Datum und Grund macht die Sperre für alle nachvollziehbar.\n\n"
                    "Das Verfahren deckt nicht nur elektrische Energie ab, sondern "
                    "alle gefährlichen Energieformen einer Maschine:\n\n"
                    "- Elektrische Energie (Hauptschalter, Sicherungen)\n"
                    "- Pneumatische Energie (Druckluft-Absperrventil entlüften)\n"
                    "- Hydraulische Energie (Druck abbauen, Ventil sperren)\n"
                    "- Mechanische Restenergie (Federn entspannen, schwere Bauteile abstützen)\n"
                    "- Thermische Energie (heiße Oberflächen abkühlen lassen)\n\n"
                    "Für den elektrischen Teil gelten die **fünf Sicherheitsregeln** "
                    "nach DGUV V3 — auswendig lernen, in dieser Reihenfolge:\n\n"
                    "1. Freischalten (Hauptschalter aus, allpolige Trennung)\n"
                    "2. Gegen Wiedereinschalten sichern (LOTO-Schloss anbringen)\n"
                    "3. Spannungsfreiheit feststellen (zweipoliger Spannungsprüfer)\n"
                    "4. Erden und kurzschließen (bei Hochspannung > 1 kV Pflicht)\n"
                    "5. Benachbarte unter Spannung stehende Teile abdecken oder abschranken\n\n"
                    "Erst wenn alle fünf Schritte abgehakt sind, darf der "
                    "Hauptschalter als sicher gelten. Eine *gefühlte Sicherheit* — "
                    "*'hab ich doch ausgeschaltet'* — reicht nicht. Schon eine "
                    "vergessene zweite Einspeisung oder ein Frequenzumrichter mit "
                    "Kondensator-Restspannung kann tödlich sein.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jedem Wartungs- oder Störungseingriff:\n\n"
                    "1. Maschine über den regulären Stopp herunterfahren, nicht über den Not-Halt\n"
                    "2. Alle Energiequellen identifizieren (Stromnetz, Druckluft, Hydraulik, Federn)\n"
                    "3. Jede Energiequelle trennen und das LOTO-Schloss anbringen\n"
                    "4. Spannungsfreiheit bzw. Druckfreiheit messen — nie nur annehmen\n"
                    "5. Schild mit Name, Datum und Grund am Schloss befestigen\n"
                    "6. Erst danach den Eingriff beginnen\n\n"
                    "Nach dem Eingriff in umgekehrter Reihenfolge: Werkzeug aus der "
                    "Maschine, Personen aus dem Gefahrenbereich, alle Personen laut "
                    "warnen, Schild und Schloss entfernen, Maschine kontrolliert "
                    "wieder einschalten.\n\n"
                    "Wenn mehrere Personen gleichzeitig arbeiten, bringt **jede** "
                    "ihr eigenes Schloss an (Multi-Lock-Bügel). Erst wenn der "
                    "letzte Kollege fertig ist und sein Schloss abnimmt, ist die "
                    "Anlage frei.\n\n"
                    "## Praxisbeispiel\n\n"
                    "An einer Spritzguss-Maschine in der Kunststoffverarbeitung "
                    "verklemmt das Granulat in der Förderschnecke. Der Anlagen"
                    "führer schaltet die Maschine am Bedienpult ab und greift in "
                    "den Trichter, um die Verstopfung zu lösen. Der Schichtkollege, "
                    "der nichts davon weiß, sieht *'Maschine steht'* und drückt "
                    "den Start-Taster — die Schnecke läuft an, der Anlagenführer "
                    "verliert drei Finger. Das richtige Vorgehen wäre gewesen: "
                    "Hauptschalter aus, eigenes LOTO-Schloss anbringen, Schild mit "
                    "Namen, Druckluft entlüften, dann erst in den Trichter greifen. "
                    "Die Maschine wäre mechanisch nicht mehr anlaufbar gewesen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BetrSichV §§ 10 und 12, TRBS 1112 "
                    "*Instandhaltung*, DGUV Vorschrift 3 § 6 (5 Sicherheitsregeln) "
                    "und DGUV Information 209-015 *Instandhaltung sicher und "
                    "praxisgerecht durchführen*."
                ),
            ),
            ModulDef(
                titel="Wartung & Störungsbeseitigung sicher",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "*'Nur kurz reingreifen'* ist die häufigste letzte Aussage vor "
                    "einem schweren Maschinenunfall. Wartung und Störungs"
                    "beseitigung sind die gefährlichsten Tätigkeiten an einer "
                    "Maschine — du bist näher dran als jeder andere, hast die "
                    "Schutzeinrichtungen oft umgangen und arbeitest unter "
                    "Zeitdruck, weil die Produktion steht.\n\n"
                    "Du lernst, wie eine Störung sicher beseitigt wird, welche "
                    "Rolle der Sondererlaubnis-Schein spielt und warum es Aufgaben "
                    "gibt, die nur eine *befähigte Person* nach BetrSichV "
                    "durchführen darf.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 BetrSichV** — Instandhaltung, Reparatur, Reinigung\n"
                    "- **§ 12 BetrSichV** — Unterweisung vor Aufnahme der Tätigkeit "
                    "und mindestens jährlich\n"
                    "- **§ 14 BetrSichV** — Prüfungen durch befähigte Personen\n"
                    "- **TRBS 1112** — Instandhaltung\n"
                    "- **§ 145 OWiG** und **§ 23 ArbSchG** — Bußgeld bei vorsätzlicher "
                    "Manipulation von Schutzeinrichtungen\n"
                    "- **§§ 222, 229 StGB** — fahrlässige Tötung / Körperverletzung\n\n"
                    "## Was musst du wissen\n\n"
                    "Wartung und Störungsbeseitigung verlangen drei Dinge in dieser "
                    "Reihenfolge: **planen**, **trennen**, **dokumentieren**.\n\n"
                    "*Planen* heißt: Bevor du anfängst, weißt du, welche Energien "
                    "im Spiel sind, welches Werkzeug du brauchst und welche Person "
                    "dich absichert. Störungsbeseitigung im Alleingang bei laufendem "
                    "Nachbargerät ist tabu — du brauchst eine zweite Person in "
                    "Ruf- und Sichtweite.\n\n"
                    "*Trennen* heißt LOTO (siehe Modul 2). Alle Energiequellen aus, "
                    "alle Schlösser dran, Spannungs- bzw. Druckfreiheit nachgemessen. "
                    "Erst dann beginnt der eigentliche Eingriff.\n\n"
                    "*Dokumentieren* heißt: Eintrag ins Wartungsbuch oder Schicht"
                    "protokoll mit Datum, Befund, Maßnahme. Bei elektrischen "
                    "Arbeiten Pflicht, bei mechanischen empfohlen.\n\n"
                    "Für riskante Sondersituationen — Arbeiten an stromführenden "
                    "Teilen, Schweißen in der Nähe von brennbaren Stoffen, "
                    "Arbeiten in engen Räumen — gilt das Prinzip **Erlaubnisschein** "
                    "(Permit-to-Work). Schicht- oder Werkstattleitung prüfen die "
                    "Gefährdung, geben das Vorgehen schriftlich frei, und erst "
                    "dann darf gearbeitet werden.\n\n"
                    "Bestimmte Prüfungen darf nicht jeder durchführen. Eine "
                    "**befähigte Person nach § 2 Abs. 6 BetrSichV** hat eine "
                    "definierte Ausbildung, Berufserfahrung und Fortbildung. Die "
                    "Prüfung der elektrischen Anlage nach DGUV V3, die UVV-Prüfung "
                    "einer Hebebühne oder die wiederkehrende Prüfung einer Presse "
                    "darf nur sie machen — nicht *'der Kollege, der sich auskennt'*.\n\n"
                    "Wer **vorsätzlich** eine Schutzeinrichtung manipuliert (Licht"
                    "schranke abklebt, Türkontakt überbrückt, Zweihandsteuerung "
                    "fixiert), riskiert Bußgelder bis 30.000 Euro nach § 23 ArbSchG. "
                    "Kommt es zum Unfall, ermitteln Berufsgenossenschaft und Staats"
                    "anwaltschaft wegen fahrlässiger Körperverletzung (§ 229 StGB) "
                    "oder fahrlässiger Tötung (§ 222 StGB) — auch gegen den "
                    "Vorgesetzten, der die Manipulation geduldet hat.\n\n"
                    "## Was musst du tun\n\n"
                    "Bei jeder Störung oder Wartung:\n\n"
                    "1. Stopp über den regulären Aus-Taster, nicht über Not-Halt\n"
                    "2. Prüfe, ob du für den Eingriff qualifiziert und befugt bist — sonst hol Fachpersonal\n"
                    "3. Wende LOTO an: alle Energien trennen, eigenes Schloss, Schild mit Namen\n"
                    "4. Prüfe Spannungs- und Druckfreiheit mit Messgerät, nicht nach Gefühl\n"
                    "5. Arbeite nie allein an Energie-führenden Anlagen, sondern mit Sicherungsperson\n"
                    "6. Dokumentiere Befund und Maßnahme im Schicht- oder Wartungsbuch\n"
                    "7. Nach dem Eingriff: Werkzeug raus, Personen raus, laut warnen, Schlösser ab, Probelauf\n\n"
                    "Wenn du dir bei einem Schritt unsicher bist — **stopp**. "
                    "Lieber zwei Stunden Produktionsausfall als ein abgerissener "
                    "Finger. Das ist kein Witz, das ist die häufigste BG-Statistik.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine Hydraulikpresse in der Automotive-Zulieferung verliert "
                    "Druck — vermutlich eine undichte Leitung. Der Anlagenführer "
                    "möchte schnell schauen, schaltet die Maschine ab und greift "
                    "in den Pressraum. Was er nicht weiß: Der Hydraulikzylinder "
                    "steht noch unter Restdruck, weil das Ablassventil verklemmt "
                    "ist. Als er die Leitung löst, schießt Hydrauliköl mit "
                    "200 bar gegen seinen Arm — Hochdruck-Injektionsverletzung, "
                    "die ohne sofortige OP zum Verlust des Arms führen kann. "
                    "Richtig wäre gewesen: LOTO-Verfahren, Druck am Manometer "
                    "auf null prüfen, Ablassventil öffnen, erst dann an die "
                    "Leitung. Die BG-Auswertung führt zu einer Nachschulung des "
                    "gesamten Wartungs-Teams und einer dokumentierten "
                    "Prüfroutine vor jedem Eingriff.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf BetrSichV §§ 10, 12 und 14 (Stand 2024), "
                    "TRBS 1112 *Instandhaltung*, DGUV Information 209-015 "
                    "*Instandhaltung sicher und praxisgerecht durchführen* sowie "
                    "DGUV Vorschrift 3 § 6 (Arbeiten an elektrischen Anlagen)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche der folgenden Schutzeinrichtungen ist *nicht-trennend*?",
                erklaerung="Nicht-trennende Schutzeinrichtungen halten dich nicht räumlich "
                "fern, sondern erkennen die Annäherung und schalten ab. Eine Lichtschranke "
                "ist das klassische Beispiel.",
                optionen=_opts(
                    ("Lichtschranke", True),
                    ("Schutzzaun um eine Roboterzelle", False),
                    ("Feste Verkleidung am Antriebsstrang", False),
                    ("Verriegelte Schutztür", False),
                ),
            ),
            FrageDef(
                text="Wofür steht *PL e* in DIN EN ISO 13849?",
                erklaerung="Performance Level e (PL e) ist die höchste Sicherheitsstufe "
                "für sicherheitsbezogene Steuerungsteile. PL a ist die geringste.",
                optionen=_opts(
                    ("Prüf-Lauf nach Einzelteilen", False),
                    ("Performance Level e — höchste Sicherheitskategorie für Steuerungen", True),
                    ("Power Level e — maximaler Energieeintrag", False),
                    ("Periodic Lockout nach Industrie-4.0-Standard", False),
                ),
            ),
            FrageDef(
                text="Du findest an einer Presse die Lichtschranke mit Gewebeband abgeklebt. Was tust du?",
                erklaerung="Eine manipulierte Schutzeinrichtung ist eine Ordnungswidrigkeit "
                "nach § 23 ArbSchG und sofortiger Stillsetzungsgrund. Melden ist Pflicht "
                "nach § 16 ArbSchG, keine Petze.",
                optionen=_opts(
                    ("Ich entferne das Klebeband stillschweigend und arbeite weiter", False),
                    ("Ich lege die Maschine still und melde die Manipulation an die Schichtleitung", True),
                    ("Ich arbeite vorsichtig weiter, weil der Vorgänger es ja auch gemacht hat", False),
                    ("Ich notiere es im Schichtbuch und mache am Ende der Schicht Meldung", False),
                ),
            ),
            FrageDef(
                text="Welches Bauteil schützt typischerweise an einer Exzenterpresse vor Handverletzungen?",
                erklaerung="Die Zweihandsteuerung zwingt den Bediener, beide Hände außerhalb "
                "des Gefahrenbereichs am Bedienpult zu halten, solange die Presse den Hub "
                "ausführt.",
                optionen=_opts(
                    ("Trittmatte", False),
                    ("Zweihandsteuerung", True),
                    ("Schutzbrille", False),
                    ("Akustisches Warnsignal", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet die Abkürzung LOTO?",
                erklaerung="Lockout-Tagout beschreibt das Abschließen (Lockout) und "
                "Beschildern (Tagout) gefährlicher Energiequellen während Wartung und "
                "Störungsbeseitigung.",
                optionen=_opts(
                    ("Logbuch-Tagebuch — Dokumentation der Schicht", False),
                    ("Lockout-Tagout — Energietrennung abschließen und beschildern", True),
                    ("Lock-Out-Take-Over — Schicht-Übergabe-Protokoll", False),
                    ("Low-Output-Test-Off — Energiespar-Modus an Maschinen", False),
                ),
            ),
            FrageDef(
                text="Welches ist die *erste* der fünf Sicherheitsregeln beim Arbeiten an elektrischen Anlagen?",
                erklaerung="Die Reihenfolge ist verbindlich: 1. Freischalten, 2. Gegen Wiedereinschalten "
                "sichern, 3. Spannungsfreiheit feststellen, 4. Erden und kurzschließen, 5. Benachbarte "
                "Teile abdecken.",
                optionen=_opts(
                    ("Spannungsfreiheit feststellen", False),
                    ("Erden und kurzschließen", False),
                    ("Freischalten", True),
                    ("Gegen Wiedereinschalten sichern", False),
                ),
            ),
            FrageDef(
                text="Wann ist die Regel *Erden und kurzschließen* zwingend Pflicht?",
                erklaerung="Die Regel ist bei Hochspannung > 1 kV verbindlich, bei "
                "Niederspannung empfohlen und je nach Anlage erforderlich.",
                optionen=_opts(
                    ("Immer, bei jeder Steckdose", False),
                    ("Bei Hochspannung über 1 kV", True),
                    ("Nur bei Photovoltaik-Anlagen", False),
                    ("Nur wenn die Anlage älter als 10 Jahre ist", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine verstopfte Förderschnecke an einer Spritzguss-Maschine reinigen. Was machst du *zuerst*?",
                erklaerung="Maschine über den regulären Aus-Schalter abschalten, LOTO am "
                "Hauptschalter, Druckluft entlüften, dann erst in den Trichter greifen.",
                optionen=_opts(
                    ("Kurz mit der Hand in den Trichter greifen, der Antrieb steht ja", False),
                    ("Maschine abschalten, LOTO am Hauptschalter, Druckluft entlüften, dann arbeiten", True),
                    ("Den Schichtkollegen bitten, am Bedienpult aufzupassen", False),
                    ("Mit einem Stab vorsichtig versuchen, das Granulat zu lösen", False),
                ),
            ),
            FrageDef(
                text="Mehrere Personen arbeiten gleichzeitig an derselben Anlage. Wie wird LOTO richtig angewendet?",
                erklaerung="Jede Person bringt ihr eigenes Schloss am Multi-Lock-Bügel an. "
                "Die Anlage ist erst frei, wenn das letzte Schloss entfernt ist.",
                optionen=_opts(
                    ("Eine Person bringt ein Schloss für alle an", False),
                    ("Jede Person bringt ihr eigenes Schloss am Multi-Lock-Bügel an", True),
                    ("Nur der Werkstattleiter bringt das Schloss an", False),
                    ("Statt LOTO reicht ein Aufkleber *Achtung Wartung*", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Energieformen wird durch LOTO *nicht* zwingend abgedeckt?",
                erklaerung="LOTO deckt alle gefährlichen Energien ab: elektrisch, pneumatisch, "
                "hydraulisch, mechanisch (Federn, Schwerkraft) und thermisch. Akustische Energie "
                "ist keine LOTO-Gefährdung.",
                optionen=_opts(
                    ("Elektrische Energie", False),
                    ("Pneumatischer Druck", False),
                    ("Akustische Energie (Lärm)", True),
                    ("Mechanische Federspannung", False),
                ),
            ),
            FrageDef(
                text="Warum reicht es *nicht*, die Spannungsfreiheit nach Gefühl anzunehmen?",
                erklaerung="Zweite Einspeisungen, Frequenzumrichter mit Kondensator-Restspannung "
                "oder vergessene Notstrom-Quellen können lebensgefährliche Spannung halten. "
                "Pflicht ist Messen mit zugelassenem Spannungsprüfer.",
                optionen=_opts(
                    ("Stimmt nicht — *gefühlt aus* ist sicher genug", False),
                    ("Zweite Einspeisungen oder Kondensator-Restspannungen können unentdeckt bleiben", True),
                    ("Es geht nur darum, die Versicherung bei Schaden zu schützen", False),
                    ("Die Berufsgenossenschaft schreibt einfach Messen vor, technisch unnötig", False),
                ),
            ),
            FrageDef(
                text="Bei welchem Arbeitsschritt benötigst du typischerweise einen schriftlichen *Erlaubnisschein* (Permit-to-Work)?",
                erklaerung="Sondergefährdungen wie Schweißen mit Heißarbeiten in der Nähe "
                "brennbarer Stoffe, Arbeiten unter Spannung oder in engen Räumen erfordern "
                "schriftliche Freigabe nach TRBS 1112.",
                optionen=_opts(
                    ("Werkzeugwechsel an einer CNC-Fräse im Normalbetrieb", False),
                    ("Schweißen in der Nähe einer Lackieranlage", True),
                    ("Büro-Computer einrichten", False),
                    ("Werkstücke an einer Stanze zuführen", False),
                ),
            ),
            FrageDef(
                text="Wer darf die wiederkehrende Prüfung einer Hydraulikpresse nach BetrSichV durchführen?",
                erklaerung="Nur eine *befähigte Person* nach § 2 Abs. 6 BetrSichV mit "
                "definierter Ausbildung, Berufserfahrung und Fortbildung darf solche "
                "Prüfungen durchführen.",
                optionen=_opts(
                    ("Jeder Mitarbeiter, der sich gut auskennt", False),
                    ("Eine befähigte Person nach § 2 Abs. 6 BetrSichV", True),
                    ("Der jüngste Auszubildende, weil er fitter ist", False),
                    ("Der Geschäftsführer persönlich", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine Störung an einer laufenden Anlage beheben — eine Sicherungsperson ist nicht da. Wie verhältst du dich?",
                erklaerung="Arbeiten an Energie-führenden Maschinen ohne zweite Person in "
                "Ruf- und Sichtweite sind tabu. Stopp, Schichtleitung holen, dann erst "
                "arbeiten.",
                optionen=_opts(
                    ("Schnell allein erledigen, damit die Produktion weiterläuft", False),
                    ("Stopp — Schichtleitung holen und auf eine Sicherungsperson warten", True),
                    ("Eine Nachricht im Schichtbuch hinterlassen, dann anfangen", False),
                    ("Per Funk Bescheid sagen, dann mit der Arbeit beginnen", False),
                ),
            ),
            FrageDef(
                text="Welche Strafnorm kann gegen *dich persönlich* greifen, wenn du eine Schutzeinrichtung manipulierst und dadurch jemand stirbt?",
                erklaerung="§ 222 StGB (fahrlässige Tötung) kann gegen den Manipulator und "
                "gegen Vorgesetzte greifen, die die Manipulation geduldet haben — Freiheits"
                "strafe bis zu fünf Jahren.",
                optionen=_opts(
                    ("Keine — nur der Arbeitgeber haftet", False),
                    ("§ 222 StGB — fahrlässige Tötung", True),
                    ("§ 263 StGB — Betrug", False),
                    ("§ 142 StGB — unerlaubtes Entfernen vom Unfallort", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zum Not-Halt-Taster (rot/gelb) stimmt?",
                erklaerung="Der Not-Halt ist *nur für Notfälle* — er soll im Normalbetrieb "
                "und auch zur regulären Wartungs-Abschaltung nicht verwendet werden, um "
                "Verschleiß und unklare Reset-Situationen zu vermeiden.",
                optionen=_opts(
                    ("Der Not-Halt ist der normale Aus-Schalter für Wartung", False),
                    ("Der Not-Halt ist nur für echte Notfälle, nicht für reguläres Abschalten", True),
                    ("Der Not-Halt darf nur vom Schichtleiter ausgelöst werden", False),
                    ("Der Not-Halt schaltet nur die Beleuchtung der Maschine ab", False),
                ),
            ),
            FrageDef(
                text="Wann ist eine Unterweisung nach § 12 BetrSichV mindestens fällig?",
                erklaerung="§ 12 BetrSichV verlangt eine Unterweisung vor Aufnahme der "
                "Tätigkeit und danach mindestens einmal jährlich, dokumentiert mit "
                "Datum und Inhalt.",
                optionen=_opts(
                    ("Einmalig bei Einstellung — danach reicht das", False),
                    ("Vor Aufnahme der Tätigkeit und danach mindestens jährlich", True),
                    ("Nur nach einem Unfall", False),
                    ("Alle fünf Jahre", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege sagt dir: *Lass das LOTO-Gedöns, ich pass am Schalter auf.* Was tust du?",
                erklaerung="Persönliche Aufsicht ersetzt LOTO nicht. Schon ein Telefonat, "
                "Toilettengang oder Schichtwechsel lässt die Aufsicht entfallen — LOTO ist "
                "Pflicht nach TRBS 1112.",
                optionen=_opts(
                    ("Klar, mit Aufpasser ist es genauso sicher", False),
                    ("Ich bestehe auf LOTO — persönliche Aufsicht ersetzt keine technische Sicherung", True),
                    ("Ich nehme an, weil er ja erfahren ist", False),
                    ("Ich frage die Schichtleitung, ob heute eine Ausnahme erlaubt ist", False),
                ),
            ),
            FrageDef(
                text="Ab welchem Datum ist die neue Maschinenverordnung (EU) 2023/1230 verbindlich anzuwenden?",
                erklaerung="Die Maschinenverordnung (EU) 2023/1230 löst ab 20.01.2027 die "
                "Maschinenrichtlinie 2006/42/EG ab. Bis dahin gilt die Richtlinie weiter.",
                optionen=_opts(
                    ("Bereits seit 2024", False),
                    ("Ab 20.01.2027", True),
                    ("Ab 2030", False),
                    ("Erst nach Ratifizierung durch Deutschland im Bundestag", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Aussagen über Schutzeinrichtungen ist *falsch*?",
                erklaerung="Schutzeinrichtungen müssen *jederzeit* wirksam sein — auch im "
                "Probelauf oder beim Einrichten. Reduzierte Geschwindigkeit oder Sonder"
                "betriebsarten sind nur mit zusätzlichen Schutzmaßnahmen zulässig.",
                optionen=_opts(
                    ("Eine Lichtschranke darf nur zur Wartung mit LOTO deaktiviert werden", False),
                    ("Im Probelauf darf die Schutztür kurz offen bleiben, wenn man aufpasst", True),
                    ("Eine Schutzeinrichtung muss bei Defekt zur Stillsetzung der Maschine führen", False),
                    ("Manipulation einer Schutzeinrichtung ist eine Ordnungswidrigkeit", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #9
    KursDef(
        titel="Lärm und Vibration am Arbeitsplatz",
        beschreibung="Unterweisung nach LärmVibrationsArbSchV. Auslösewerte, Gehörschutz-Praxis.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Auslösewerte und Pflichten",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "In einer typischen Werkhalle liegen Pressen bei 95 bis 105 dB(A), "
                    "Schleifmaschinen bei 90 dB(A), Druckluft-Werkzeuge auch mal jenseits "
                    "der 100 dB(A). Tatsächlich beginnt irreversible Innenohrschädigung "
                    "schon ab 80 dB(A) bei Dauerexposition. Lärmschwerhörigkeit ist die "
                    "häufigste anerkannte Berufskrankheit (BK 2301) in Deutschland und "
                    "kommt schleichend: erst gehen die hohen Frequenzen verloren, dann "
                    "das Sprachverstehen im Stimmengewirr. Haarzellen im Innenohr "
                    "regenerieren nicht.\n\n"
                    "Analog gilt das für Vibrationen: wer jahrelang mit Druckluftschrauber "
                    "oder Bohrhammer arbeitet, riskiert die *Weißfingerkrankheit* "
                    "(Vibrations-Vasospasmus) mit Nervenschäden und Verlust der "
                    "Feinmotorik.\n\n"
                    "Du lernst die Zahlen, ab denen der Arbeitgeber handeln muss — und "
                    "warum die 'das hört man ja nicht so'-Selbsttäuschung ein teurer "
                    "Irrtum ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **LärmVibrationsArbSchV** — Verordnung zum Schutz vor Gefährdungen durch Lärm und Vibrationen\n"
                    "- **§ 6 LärmVibrationsArbSchV** — Auslösewerte für Lärm (80 / 85 dB(A))\n"
                    "- **§ 7 LärmVibrationsArbSchV** — Maßnahmen gegen Lärm, Kennzeichnung Lärmbereich\n"
                    "- **§ 8 LärmVibrationsArbSchV** — Gehörschutz: Bereitstellung und Tragepflicht\n"
                    "- **§ 9 LärmVibrationsArbSchV** — Auslöse- und Expositionsgrenzwerte für Vibrationen\n"
                    "- **TRLV Lärm / TRLV Vibrationen** — Technische Regeln, konkretisieren die Verordnung\n\n"
                    "## Was musst du wissen\n\n"
                    "Es gibt zwei rechtlich harte Schwellen für Lärm — den *unteren* und "
                    "den *oberen* **Auslösewert**. Beide werden als Tages-Lärm"
                    "expositionspegel auf eine 8-Stunden-Schicht hochgerechnet "
                    "(L_EX,8h). Wichtig: der dämmende Effekt eines Gehörschutzes "
                    "zählt bei dieser Bewertung *nicht* mit — es ist immer der Pegel, "
                    "der ohne Schutz aufs Ohr trifft.\n\n"
                    "| Schwelle | Tages-Pegel L_EX,8h | Spitze L_pC,peak | Pflicht des Arbeitgebers |\n"
                    "|---|---|---|---|\n"
                    "| Unterer Auslösewert | 80 dB(A) | 135 dB(C) | Gehörschutz zur Verfügung stellen, Unterweisung, Vorsorge anbieten |\n"
                    "| Oberer Auslösewert | 85 dB(A) | 137 dB(C) | Lärmbereich kennzeichnen, Gehörschutz tragen Pflicht, Vorsorge Pflicht, Lärmminderungsprogramm |\n"
                    "| Maximaler Expositionswert am Ohr | 85 dB(A) unter Gehörschutz | 137 dB(C) | darf nie überschritten werden |\n\n"
                    "Die Faustregel für die Lautstärke-Wahrnehmung: jede Erhöhung um "
                    "10 dB(A) entspricht einer Verdopplung der gefühlten Lautstärke "
                    "und einer Verzehnfachung der Schallenergie. 95 dB(A) an der Presse "
                    "sind also energetisch das Hundertfache von 75 dB(A) im Pausenraum.\n\n"
                    "Bei Vibrationen gelten zwei Größen: **Hand-Arm-Vibration** (HAV) "
                    "bei handgeführten Werkzeugen und **Ganzkörper-Vibration** (GKV) "
                    "etwa beim Staplerfahren. Der Wert A(8) ist der über 8 Stunden "
                    "energieäquivalent gemittelte Beschleunigungswert.\n\n"
                    "| Art | Auslösewert A(8) | Expositionsgrenzwert A(8) |\n"
                    "|---|---|---|\n"
                    "| Hand-Arm-Vibration | 2,5 m/s² | 5,0 m/s² |\n"
                    "| Ganzkörper-Vibration (X, Y) | 0,5 m/s² | 1,15 m/s² |\n"
                    "| Ganzkörper-Vibration (Z) | 0,5 m/s² | 0,8 m/s² |\n\n"
                    "Wird der Auslösewert erreicht, muss der Arbeitgeber Maßnahmen "
                    "planen (vibrationsärmere Werkzeuge, Begrenzung der Expositionszeit, "
                    "Vibrationsdämpfende Handschuhe). Der Grenzwert darf nie "
                    "überschritten werden — Punkt.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Achte auf die gelb-schwarze Lärmbereich-Kennzeichnung mit dem Gehörschutz-Symbol (M003) — wer den Bereich betritt, muss Gehörschutz tragen, auch wenn er nur 'kurz was abholt'\n"
                    "2. Trage den Gehörschutz die ganze Schicht, nicht nur bei lauten Spitzen — schon zehn Minuten ohne Schutz pro Stunde halbieren den effektiven Schutzwert\n"
                    "3. Melde defekte oder zu laute Maschinen an die Schichtleitung, eine schlecht gewartete Presse ist oft 5 bis 10 dB(A) lauter als spezifiziert\n"
                    "4. Nutze das Angebot der arbeitsmedizinischen Vorsorge G 20 (Lärm) wahr — sie ist ab 85 dB(A) verpflichtend, ab 80 dB(A) anzubieten\n"
                    "5. Begrenze die Expositionszeit an stark vibrierenden Werkzeugen durch Tätigkeitswechsel, kurze Pausen entlasten Hand und Arm\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Werker in einer Schmiede arbeitet acht Stunden an der Gesenk"
                    "schmiedepresse, gemessener Pegel 98 dB(A). Er trägt Kapselgehörschutz "
                    "mit SNR 30 dB, setzt ihn aber alle 30 Minuten kurz ab — pro Stunde "
                    "rund drei Minuten ohne Schutz. Rechnerisch sollte er auf 68 dB(A) "
                    "am Ohr kommen. Tatsächlich liegt der effektive Tages-Pegel bei rund "
                    "84 dB(A) — die ungeschützten Minuten dominieren das Energie-Mittel "
                    "komplett, weil Lärm logarithmisch wirkt. Nach drei Jahren zeigt sein "
                    "Audiogramm die typische C5-Senke bei 4 kHz. Korrekturmaßnahme: "
                    "Gehörschutz konsequent auflassen, Verständigung über Funk oder im "
                    "Pausenraum.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf LärmVibrationsArbSchV §§ 6, 7, 8, 9 "
                    "(Stand 2017, mit Änderungen 2023), TRLV Lärm Teil 1-3 "
                    "(GMBl 2017), TRLV Vibrationen (GMBl 2015) und "
                    "DGUV Information 209-023 *Lärm beim Arbeiten an Maschinen*."
                ),
            ),
            ModulDef(
                titel="Gehörschutz in der Praxis",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Gehörschutz wirkt nur, wenn er passt, richtig sitzt und konsequent "
                    "getragen wird. Der häufigste Fehler in der Praxis ist nicht 'gar "
                    "kein Schutz', sondern 'falscher oder schlecht eingesetzter Schutz'. "
                    "Stöpsel zu locker im Gehörgang, Kapsel über Brillenbügel, die Hälfte "
                    "der Schicht zum Telefonieren rausgenommen — und plötzlich entspricht "
                    "der reale Schutz nur einem Bruchteil dessen, was auf der Verpackung "
                    "steht.\n\n"
                    "Du lernst, welche Schutztypen es gibt, wie man Stöpsel korrekt "
                    "einsetzt und warum Hand-Arm-Vibration ein eigenes Praxisthema ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 8 LärmVibrationsArbSchV** — Bereitstellung und Verwendung von Gehörschutz\n"
                    "- **PSA-Benutzungsverordnung** — Anforderungen an Persönliche Schutzausrüstung\n"
                    "- **DGUV Regel 112-194** — Benutzung von Gehörschützern\n"
                    "- **DGUV Information 209-023** — Lärm beim Arbeiten an Maschinen\n\n"
                    "## Was musst du wissen\n\n"
                    "Es gibt drei gängige Grundtypen Gehörschutz im Industrieumfeld. "
                    "Jeder hat seine Stärken und Schwächen:\n\n"
                    "| Typ | Dämmung SNR | Stärke | Schwäche |\n"
                    "|---|---|---|---|\n"
                    "| Einweg-Stöpsel (Schaumstoff) | 30-37 dB | hohe Dämmung, billig, gut bei Brille | Einsetz-Technik kritisch, Hygiene bei Wiederverwendung |\n"
                    "| Kapselgehörschutz | 25-35 dB | schnell aufgesetzt, leicht prüfbar | warm bei Hitze, problematisch mit Brille oder Helm-Anschluss |\n"
                    "| Maßangefertigter Otoplastik-Stöpsel | 15-30 dB | komfortabel über die ganze Schicht | teuer, regelmäßige Funktionsprüfung nötig |\n\n"
                    "Die **SNR-Zahl** (Single Number Rating) auf der Verpackung ist ein "
                    "Laborwert. In der Praxis erreicht man typischerweise nur 50 bis "
                    "70 Prozent davon — die TRLV Lärm rechnet deshalb mit einem "
                    "Praxisabschlag von 4 bis 9 dB je nach Schutztyp. Die Auswahl "
                    "richtet sich nach dem Pegel: bei 95 dB(A) reicht meist ein Stöpsel "
                    "der Klasse M, bei 100 dB(A) oder mehr braucht es Klasse H oder eine "
                    "Doppelausrüstung (Stöpsel plus Kapsel).\n\n"
                    "**Überdämmung** ist auch ein Problem: wenn die Restpegel unter "
                    "70 dB(A) am Ohr liegen, hört man Maschinenfehler, Warnsignale und "
                    "Kollegen nicht mehr. Das ist gefährlich. Im Idealfall liegt der "
                    "Restpegel zwischen 70 und 80 dB(A) am Ohr.\n\n"
                    "Bei **Hand-Arm-Vibration** gibt es keinen 'Schutz' im engeren Sinn, "
                    "der wie Gehörschutz dämpft. Vibrationsschutz-Handschuhe nach "
                    "DIN EN ISO 10819 helfen begrenzt im Frequenzbereich oberhalb 200 Hz, "
                    "darunter sind sie weitgehend wirkungslos. Die wichtigsten Maß"
                    "nahmen sind technische und organisatorische: vibrationsärmere "
                    "Werkzeuge, gewartete Werkzeuge (stumpfe Bohrer und unwuchtige "
                    "Schleifscheiben treiben die Vibration enorm), Tätigkeitswechsel, "
                    "Expositionszeit-Begrenzung. Konkret: ein moderner Druckluftschrauber "
                    "mit Anti-Vibrations-Griff erreicht etwa 3 m/s², ein älteres Modell "
                    "kann bei 8 m/s² liegen — bei vier Stunden Einsatz pro Schicht ist "
                    "das schon der Grenzwert.\n\n"
                    "## Was musst du tun\n\n"
                    "Schaumstoff-Stöpsel richtig einsetzen — die 'Roll-Pull-Hold'-Technik:\n\n"
                    "1. Stöpsel zwischen Daumen und Zeigefinger zu einer dünnen Rolle drücken (nicht knicken)\n"
                    "2. Mit der freien Hand das Ohr nach hinten oben ziehen, dadurch öffnet sich der Gehörgang\n"
                    "3. Den gerollten Stöpsel zügig tief in den Gehörgang schieben\n"
                    "4. Mindestens 30 Sekunden mit dem Finger leicht festhalten, bis sich der Schaum ausdehnt\n"
                    "5. Sitz prüfen: bei korrektem Sitz dämpft sich die eigene Stimme deutlich, der Raum klingt 'gedeckelt'\n\n"
                    "Kapsel-Gehörschutz korrekt nutzen:\n\n"
                    "- Haare und Brillenbügel unter der Dichtung entfernen oder mit Spezial-Brillenbügeln arbeiten\n"
                    "- Bügel nicht aufbiegen, dadurch sinkt der Anpressdruck und die Dämmung\n"
                    "- Dichtkissen sauber halten und jährlich tauschen, Hartwerden senkt den Schutzwert\n\n"
                    "Tragedisziplin:\n\n"
                    "- Im Lärmbereich nie abnehmen, auch nicht 'nur kurz'\n"
                    "- Bei sehr langen Schichten zwischendurch im Pausenraum die Ohren erholen lassen, nicht im Lärm\n"
                    "- Defekten Gehörschutz sofort tauschen, deformierte Stöpsel oder rissige Dichtungen sind wirkungslos\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Auszubildender in einer Schreinerei trägt am ersten Tag Schaum"
                    "stoff-Stöpsel mit SNR 35 dB, steckt sie aber nur halb in den "
                    "Gehörgang. An der Kantenfräse (98 dB(A)) klingt für ihn die Welt "
                    "etwas gedämpft — der reale Schutz liegt bei vielleicht 10 dB statt "
                    "35. Am Ohr kommen 88 dB(A) an, deutlich über dem Grenzwert. Der "
                    "Vorarbeiter zeigt ihm in der Pause die Roll-Pull-Hold-Technik und "
                    "kontrolliert Sitz und Tiefe. Ergebnis: deutlich wahrnehmbare "
                    "zusätzliche Dämpfung der eigenen Stimme, realer Schutz jetzt rund "
                    "28 dB, Restpegel etwa 70 dB(A). Audiogramm bei der nächsten "
                    "Vorsorge unauffällig.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Regel 112-194 *Benutzung von "
                    "Gehörschützern* (Ausgabe 2020), DGUV Information 209-023 "
                    "*Lärm beim Arbeiten an Maschinen* und TRLV Lärm Teil 3 *Lärmschutz"
                    "maßnahmen* (GMBl 2017). Vibrationsschutz nach TRLV Vibrationen und "
                    "DIN EN ISO 10819:2013."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Ab welchem Tages-Lärmexpositionspegel L_EX,8h muss der Arbeitgeber Gehörschutz zur Verfügung stellen?",
                erklaerung="Der untere Auslösewert nach § 6 LärmVibrationsArbSchV liegt bei "
                "80 dB(A). Ab hier ist die Bereitstellung von Gehörschutz Pflicht.",
                optionen=_opts(
                    ("Ab 70 dB(A)", False),
                    ("Ab 80 dB(A) (unterer Auslösewert)", True),
                    ("Ab 85 dB(A)", False),
                    ("Ab 90 dB(A)", False),
                ),
            ),
            FrageDef(
                text="Ab welchem Pegel ist das Tragen von Gehörschutz Pflicht und der Bereich als Lärmbereich zu kennzeichnen?",
                erklaerung="Der obere Auslösewert nach § 6 liegt bei 85 dB(A). Hier wird aus "
                "'Angebot' eine harte Tragepflicht, und der Bereich muss gekennzeichnet werden.",
                optionen=_opts(
                    ("Ab 80 dB(A)", False),
                    ("Ab 85 dB(A) (oberer Auslösewert)", True),
                    ("Ab 90 dB(A)", False),
                    ("Ab 100 dB(A)", False),
                ),
            ),
            FrageDef(
                text="Welcher Auslösewert gilt für Hand-Arm-Vibration nach § 9 LärmVibrationsArbSchV?",
                erklaerung="Der Auslösewert A(8) liegt bei 2,5 m/s², der nicht überschreitbare "
                "Expositionsgrenzwert bei 5,0 m/s². Werte beziehen sich auf 8 h Schichtdauer.",
                optionen=_opts(
                    ("0,5 m/s²", False),
                    ("1,15 m/s²", False),
                    ("2,5 m/s²", True),
                    ("5,0 m/s²", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet eine Pegelerhöhung um 10 dB(A) für die gefühlte Lautstärke?",
                erklaerung="Pegel ist logarithmisch: +10 dB(A) entspricht subjektiv etwa der "
                "Verdopplung der Lautstärke und der Verzehnfachung der Schallenergie.",
                optionen=_opts(
                    ("Sie wird etwa doppelt so laut empfunden", True),
                    ("Sie wird um 10 Prozent lauter", False),
                    ("Sie verzehnfacht sich subjektiv", False),
                    ("Sie ändert sich kaum hörbar", False),
                ),
            ),
            FrageDef(
                text="Was ist die häufigste anerkannte Berufskrankheit in Deutschland?",
                erklaerung="Die Lärmschwerhörigkeit (BK 2301) führt seit Jahrzehnten die Statistik "
                "der anerkannten BKen an. Schäden am Innenohr sind irreversibel.",
                optionen=_opts(
                    ("Rückenleiden", False),
                    ("Lärmschwerhörigkeit (BK 2301)", True),
                    ("Asbestose", False),
                    ("Hautekzeme durch Kühlschmierstoffe", False),
                ),
            ),
            FrageDef(
                text="Welcher Expositionsgrenzwert darf am Ohr unter Gehörschutz nie überschritten werden?",
                erklaerung="§ 8 Abs. 2 LärmVibrationsArbSchV setzt 85 dB(A) als maximalen Pegel "
                "am Ohr (also mit eingerechnetem Schutz) als obere Grenze.",
                optionen=_opts(
                    ("70 dB(A) am Ohr", False),
                    ("80 dB(A) am Ohr", False),
                    ("85 dB(A) am Ohr", True),
                    ("95 dB(A) am Ohr", False),
                ),
            ),
            FrageDef(
                text="Du arbeitest die ganze Schicht an einer 95 dB(A) lauten Presse, nimmst aber alle 20 Minuten kurz den Gehörschutz ab, um mit dem Kollegen zu sprechen. Was ist das Problem?",
                erklaerung="Lärm wirkt logarithmisch. Schon wenige Minuten ohne Schutz pro Stunde "
                "können den effektiven Tages-Pegel um mehr als 10 dB nach oben verschieben.",
                optionen=_opts(
                    ("Kein Problem, kurze Pausen sind unkritisch", False),
                    ("Die ungeschützten Minuten dominieren den Tages-Pegel, der reale Schutz halbiert sich schnell", True),
                    ("Nur problematisch, wenn der Kollege auch keinen Schutz trägt", False),
                    ("Erlaubt, solange die Pause unter 2 Minuten bleibt", False),
                ),
            ),
            FrageDef(
                text="Du siehst die gelb-schwarze Lärmbereich-Kennzeichnung an einer Hallenecke, sollst dort aber nur kurz ein Teil holen. Was tust du?",
                erklaerung="Die Pflicht gilt ab Betreten des Bereichs, auch für kurze Tätigkeiten. "
                "Schon Sekunden bei 100+ dB(A) können in der Summe schädigen.",
                optionen=_opts(
                    ("Ohne Gehörschutz reingehen, sind nur 30 Sekunden", False),
                    ("Gehörschutz aufsetzen vor dem Betreten, auch für kurze Wege", True),
                    ("Schnell durchrennen und kurz die Ohren zuhalten", False),
                    ("Erst beim Kollegen nachfragen, ob es wirklich so laut ist", False),
                ),
            ),
            FrageDef(
                text="Du bekommst Schaumstoff-Stöpsel und einen Kapselgehörschutz angeboten. Welche Auswahl ist sinnvoll?",
                erklaerung="Die Auswahl richtet sich nach Pegel, Tätigkeit (Brille, Helm), Hitze "
                "und persönlichem Komfort. Wichtig ist nicht der Typ, sondern die konsequente Nutzung.",
                optionen=_opts(
                    ("Immer den teuersten nehmen", False),
                    ("Den nehmen, der zum Pegel, zur Tätigkeit und persönlich passt, weil dann konsequent getragen", True),
                    ("Beides gleichzeitig, in jeder Situation", False),
                    ("Nur Kapsel, Stöpsel sind nie hygienisch", False),
                ),
            ),
            FrageDef(
                text="Du arbeitest mehrere Stunden täglich mit einem alten Druckluftschrauber, der spürbar stark vibriert. Was ist die richtige Reaktion?",
                erklaerung="Werkzeug-Zustand ist die wichtigste technische Maßnahme bei HAV. Stumpfe "
                "oder unwuchtige Werkzeuge erhöhen die Vibration oft drastisch.",
                optionen=_opts(
                    ("Aushalten, ist Teil des Jobs", False),
                    ("Werkzeug-Zustand prüfen lassen oder Tausch fordern, gegebenenfalls Tätigkeit wechseln", True),
                    ("Doppelte Handschuhe anziehen, das gleicht alles aus", False),
                    ("Nur lockerer halten, dann vibriert es weniger", False),
                ),
            ),
            FrageDef(
                text="Wie setzt du einen Schaumstoff-Stöpsel korrekt ein?",
                erklaerung="Roll-Pull-Hold: dünn rollen, Ohr nach hinten oben ziehen (Gehörgang öffnet "
                "sich), Stöpsel tief einsetzen, mindestens 30 s halten bis Schaum sich ausdehnt.",
                optionen=_opts(
                    ("Locker in die Ohrmuschel klemmen", False),
                    ("Dünn rollen, Ohr nach hinten oben ziehen, tief einsetzen, mindestens 30 s halten", True),
                    ("Mit Speichel anfeuchten und gerade einschieben", False),
                    ("Halb in den Gehörgang stecken, der Rest stört nur", False),
                ),
            ),
            FrageDef(
                text="Wann ist eine *Überdämmung* durch Gehörschutz ein echtes Sicherheitsproblem?",
                erklaerung="Liegt der Restpegel unter ca. 70 dB(A), werden Warnsignale, Stapler-Hupen "
                "und Kollegen-Zurufe nicht mehr gehört. Ziel ist 70-80 dB(A) am Ohr.",
                optionen=_opts(
                    ("Wenn der Schutz die ganze Schicht getragen wird", False),
                    ("Wenn der Restpegel am Ohr unter 70 dB(A) sinkt und Warnsignale unhörbar werden", True),
                    ("Überdämmung ist nie ein Problem, je mehr desto besser", False),
                    ("Nur bei Kopfhörer-Modellen mit Musik", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege sagt: 'Den Lärm hier hör ich gar nicht mehr, das macht mir nichts.' Wie bewertest du diese Aussage?",
                erklaerung="Genau das ist das Warnsignal: das Gehör hat sich bereits angepasst, "
                "vermutlich liegen schon Schäden bei hohen Frequenzen vor. Lärm wirkt unabhängig vom subjektiven Empfinden.",
                optionen=_opts(
                    ("Stimmt, wer es gewohnt ist, ist immun", False),
                    ("Klassische Selbsttäuschung, oft Zeichen einer bereits bestehenden Hörschädigung", True),
                    ("Nur ein Problem, wenn er auch keine Musik mehr hört", False),
                    ("Korrekt, ältere Mitarbeiter brauchen weniger Schutz", False),
                ),
            ),
            FrageDef(
                text="Vibrationsschutz-Handschuhe nach DIN EN ISO 10819 — was leisten sie wirklich?",
                erklaerung="Sie helfen messbar nur oberhalb ca. 200 Hz. Niedrige Frequenzen (bei "
                "Bohrhammern, Stampfern) gehen ungebremst durch — hier helfen nur technische und organisatorische Maßnahmen.",
                optionen=_opts(
                    ("Sie senken jede Vibration um den Faktor 10", False),
                    ("Sie wirken begrenzt nur im hochfrequenten Bereich, ersetzen keine technische Maßnahme", True),
                    ("Sie sind vollwertiger Ersatz für vibrationsarme Werkzeuge", False),
                    ("Sie wirken nur, wenn sie zusätzlich elektrisch beheizt sind", False),
                ),
            ),
            FrageDef(
                text="Ein:e Mitarbeiter:in lehnt das Tragen des Gehörschutzes ab. Was gilt?",
                erklaerung="§ 15 ArbSchG und § 8 LärmVibrationsArbSchV machen das Tragen oberhalb "
                "85 dB(A) zur Pflicht. Verweigerung ist arbeitsrechtlich abmahnbar.",
                optionen=_opts(
                    ("Persönliche Entscheidung, akzeptieren", False),
                    ("Tragen ist gesetzliche Pflicht ab oberem Auslösewert, Verweigerung ist abmahnbar", True),
                    ("Nur Auszubildende müssen tragen", False),
                    ("Erlaubt, wenn schriftliche Verzichtserklärung vorliegt", False),
                ),
            ),
            FrageDef(
                text="Welche Wirkung haben dB-Werte unter Gehörschutz auf die rechtliche Bewertung des Auslösewerts?",
                erklaerung="§ 6 LärmVibrationsArbSchV: die dämmende Wirkung des Gehörschutzes wird "
                "beim Auslösewert ausdrücklich nicht angerechnet — bewertet wird der Pegel ohne Schutz.",
                optionen=_opts(
                    ("Der Schutz wird voll angerechnet, dadurch sinkt der bewertete Pegel", False),
                    ("Die dämmende Wirkung wird beim Auslösewert nicht berücksichtigt", True),
                    ("Schutz halbiert den bewerteten Pegel", False),
                    ("Hängt vom SNR-Wert des Schutzes ab", False),
                ),
            ),
            FrageDef(
                text="Was zeigt die typische 'C5-Senke' im Audiogramm?",
                erklaerung="Die C5-Senke (Einbruch bei 4 kHz) ist das klassische frühe Zeichen einer "
                "Lärmschwerhörigkeit, bevor Sprachverstehen messbar leidet.",
                optionen=_opts(
                    ("Eine Mittelohrentzündung", False),
                    ("Den ersten messbaren Schritt einer Lärmschwerhörigkeit bei 4 kHz", True),
                    ("Eine angeborene Hörstörung", False),
                    ("Einen Defekt des Audiometers", False),
                ),
            ),
            FrageDef(
                text="Welche arbeitsmedizinische Vorsorge gehört zum Thema Lärm?",
                erklaerung="Die Vorsorge G 20 (Lärm) ist ab 85 dB(A) Pflicht, ab 80 dB(A) als "
                "Angebotsvorsorge bereitzustellen. Sie umfasst Audiogramm und Beratung.",
                optionen=_opts(
                    ("G 25 (Fahr-, Steuer-, Überwachungstätigkeiten)", False),
                    ("G 20 (Lärm) — Pflicht ab 85 dB(A), Angebot ab 80 dB(A)", True),
                    ("G 37 (Bildschirmarbeitsplatz)", False),
                    ("G 42 (Tätigkeiten mit Infektionsgefahr)", False),
                ),
            ),
            FrageDef(
                text="In welcher Reihenfolge gilt das STOP-Prinzip bei Lärm- und Vibrations-Schutz?",
                erklaerung="STOP: Substitution > Technische Maßnahmen > Organisatorische Maßnahmen > "
                "Persönliche Schutzausrüstung. PSA ist letzte Wahl, nicht erste.",
                optionen=_opts(
                    ("Persönlicher Schutz zuerst, dann Technik", False),
                    ("Substitution, Technik, Organisation, PSA als letzte Wahl", True),
                    ("Egal, Hauptsache irgendwas wird getan", False),
                    ("Erst Pause anbieten, dann Maschine tauschen", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur Innenohrschädigung durch Lärm ist korrekt?",
                erklaerung="Haarzellen im Innenohr regenerieren beim Menschen nicht. Lärmbedingte "
                "Hörverluste sind dauerhaft, der einzige Schutz ist konsequente Prävention.",
                optionen=_opts(
                    ("Mit Vitamin-Präparaten lässt sich der Schaden rückgängig machen", False),
                    ("Schäden an den Haarzellen sind irreversibel, Hörverlust bleibt dauerhaft", True),
                    ("Junge Menschen regenerieren das Gehör innerhalb von 6 Monaten", False),
                    ("Operative Wiederherstellung ist Standard", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #10
    KursDef(
        titel="Antikorruption & Geschenke-Policy",
        beschreibung="Compliance-Schulung zu Bestechung & Vorteilsnahme nach § 299 StGB + ISO 37001. Zuwendungen erkennen, Lieferantenkontakt, Meldewege.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Was ist Korruption?",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Korruption ist nicht der Koffer voll Bargeld im Hinterzimmer. Im Mittelstand "
                    "passiert sie meistens leise: ein Lieferant lädt die Einkäuferin zur Fußball-WM "
                    "ein, ein Vertriebspartner bekommt 'Provision' ohne nachvollziehbare Leistung, "
                    "die Schichtleitung bekommt ein iPad 'als Dankeschön'. Du lernst, was Korruption "
                    "rechtlich genau ist, wer Täter sein kann und warum schon der *Anschein* der "
                    "Käuflichkeit ausreicht, um dich und das Unternehmen in ernste Schwierigkeiten "
                    "zu bringen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 299 StGB** — Bestechlichkeit und Bestechung im geschäftlichen Verkehr "
                    "(Strafrahmen: Freiheitsstrafe bis zu 3 Jahren oder Geldstrafe, in besonders "
                    "schweren Fällen nach § 300 StGB bis zu 5 Jahren)\n"
                    "- **§§ 331-335 StGB** — Vorteilsannahme und Bestechlichkeit von Amtsträgern "
                    "(relevant bei jedem Kontakt zu Behörden, TÜV, Gewerbeaufsicht, Zoll)\n"
                    "- **§ 130 OWiG** — Aufsichtspflichtverletzung: Geschäftsleitung haftet bei "
                    "fehlenden Compliance-Maßnahmen mit Bußgeld bis 10 Mio. Euro\n"
                    "- **ISO 37001:2025** — internationaler Standard für Anti-Bestechungs-"
                    "Managementsysteme, oft Lieferanten-Anforderung von Konzernkunden\n\n"
                    "## Was musst du wissen\n\n"
                    "Korruption hat im Kern immer drei Bausteine: jemand fordert oder erhält einen "
                    "**Vorteil**, gewährt im Gegenzug eine **Bevorzugung** im geschäftlichen "
                    "Verkehr, und das Ganze geschieht *zur Pflichtverletzung* gegenüber dem eigenen "
                    "Arbeitgeber oder unter Verletzung des fairen Wettbewerbs. Es spielt keine "
                    "Rolle, ob die Bevorzugung tatsächlich erfolgt — die bloße Verabredung "
                    "(Unrechtsvereinbarung) ist schon strafbar.\n\n"
                    "Die wichtigsten Tatbestände im Überblick:\n\n"
                    "| Norm | Wer ist Täter | Was ist verboten |\n"
                    "|---|---|---|\n"
                    "| § 299 Abs. 1 StGB | Angestellte/Beauftragte eines Unternehmens | Vorteil annehmen oder fordern für Bevorzugung |\n"
                    "| § 299 Abs. 2 StGB | Wer einem Angestellten Vorteil anbietet | aktive Bestechung im Geschäftsverkehr |\n"
                    "| § 331 StGB | Amtsträger (Behörde, TÜV, Prüfer) | Vorteil annehmen für Dienstausübung |\n"
                    "| § 332 StGB | Amtsträger | Vorteil für pflichtwidrige Diensthandlung |\n"
                    "| § 333/334 StGB | Wer einem Amtsträger Vorteil anbietet | Vorteilsgewährung / Bestechung |\n\n"
                    "Im Industrie-Mittelstand betrifft das praktisch alle Schnittstellen nach außen: "
                    "**Einkauf** (Lieferanten-Auswahl), **Vertrieb** (Provisionen, Rabatte), **Service** "
                    "(Wartungs- und Reparaturaufträge), **Personalabteilung** (externe Dienstleister, "
                    "Zeitarbeit), aber auch jeder Kontakt zu **Behörden** (Gewerbeaufsicht, Zoll, "
                    "TÜV-Prüferin, Umweltamt). Auslandsgeschäft erhöht das Risiko zusätzlich, "
                    "weil dort Schmiergeld-Erwartungen kulturell stellenweise normalisiert sind — "
                    "*nach deutschem Recht bleibt es trotzdem strafbar*.\n\n"
                    "Wichtig: nicht nur Geld ist ein Vorteil. Auch Sachzuwendungen (Geräte, Wein, "
                    "Tickets), persönliche Vergünstigungen (Rabatt, Job für den Sohn), Einladungen "
                    "(Restaurant, Sportevent, Reise) und sogar bezahlte Vorträge oder Beraterhonorare "
                    "ohne echte Gegenleistung können Vorteile im Sinne der Strafnormen sein.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Trenne private und geschäftliche Beziehung sauber — Geschäftspartner sind nicht deine Freunde, auch wenn du sie seit 15 Jahren kennst\n"
                    "2. Dokumentiere jeden Vorteil über dem Schwellenwert (in der Compliance-Richtlinie geregelt, typisch 35-50 Euro) im Geschenke-Register\n"
                    "3. Frage dich vor der Annahme: *Könnte das den Anschein erwecken, dass meine Entscheidung dadurch beeinflusst wird?* Wenn ja: ablehnen\n"
                    "4. Bei Behördenkontakt gilt absolute Null-Toleranz: kein Kaffee, kein Mittagessen, kein Werbegeschenk\n"
                    "5. Im Zweifel den Compliance-Officer oder die Geschäftsführung fragen, *bevor* du etwas annimmst — Beratung danach ist nutzlos\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Kunststoff-Verarbeiter in Schwaben sucht einen neuen Spritzguss-Maschinenlieferanten. "
                    "Der favorisierte Lieferant lädt den Produktionsleiter und seine Ehefrau zu einem "
                    "Wochenende auf Mallorca ein — 'Werksbesichtigung des spanischen Standorts'. Wert "
                    "der Reise rund 2.400 Euro. Der Produktionsleiter nimmt an und entscheidet zwei "
                    "Wochen später zugunsten dieses Lieferanten. Ein unterlegener Mitbewerber zeigt "
                    "an. Ergebnis: Ermittlungsverfahren wegen § 299 StGB gegen den Produktionsleiter, "
                    "Bußgeld gegen das Unternehmen nach § 30 OWiG (250.000 Euro), Schadenersatz an "
                    "den unterlegenen Lieferanten, fristlose Kündigung des Produktionsleiters. Die "
                    "tatsächliche Reise hätte nichts geändert — schon die *Annahme* der Einladung "
                    "vor der Vergabe-Entscheidung erfüllt den Tatbestand.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf § 299 StGB und §§ 331-335 StGB (Stand 2025), "
                    "ISO 37001:2025 *Anti-bribery management systems*, "
                    "Transparency Deutschland *Grundsätze für Unternehmen* (2024) sowie "
                    "BGH-Rechtsprechung zur Unrechtsvereinbarung (u.a. BGH 1 StR 416/15)."
                ),
            ),
            ModulDef(
                titel="Zuwendungen — was ist erlaubt?",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Werbe-Kugelschreiber zur Hannover-Messe ist kein Problem. Ein Weihnachtskorb "
                    "im Wert von 120 Euro vom CNC-Lieferanten an die Einkäuferin schon. Wo genau "
                    "verläuft die Linie? Du lernst die steuerlichen, strafrechtlichen und "
                    "unternehmensinternen Schwellenwerte kennen — und warum die *Wahrnehmung* eines "
                    "Vorteils oft wichtiger ist als sein Euro-Betrag.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 4 Abs. 5 Nr. 1 EStG** — steuerliche Freigrenze für Geschenke an "
                    "Geschäftspartner: seit 01.01.2024 **50 Euro** pro Person und Kalenderjahr "
                    "(vorher 35 Euro). Wird die Grenze überschritten, ist der *gesamte* Wert nicht "
                    "abzugsfähig\n"
                    "- **§ 37b EStG** — Pauschalsteuer von 30 % auf Sachzuwendungen, vom schenkenden "
                    "Unternehmen zu tragen\n"
                    "- **R 19.6 LStR** — Aufmerksamkeiten an Mitarbeitende bis 60 Euro (Geburtstag, "
                    "Hochzeit) bleiben lohnsteuerfrei\n"
                    "- **§ 299 StGB** — strafrechtlicher Maßstab: jenseits jeder Steuergrenze, es "
                    "zählt die Eignung, eine Bevorzugung herbeizuführen\n\n"
                    "## Was musst du wissen\n\n"
                    "Die 50-Euro-Grenze des Steuerrechts ist ein nützlicher Anker, aber **keine "
                    "Freigrenze für das Strafrecht**. Strafbar kann auch ein Geschenk unter 50 Euro "
                    "sein, wenn es Teil eines Musters ist (jeden Monat ein neues 'kleines' Geschenk) "
                    "oder wenn es zeitlich mit einer Vergabe-Entscheidung zusammenfällt. Umgekehrt "
                    "kann eine teure Einladung sozialadäquat sein — etwa ein Geschäftsessen im "
                    "Rahmen einer Vertragsverhandlung, das beide Seiten teilen.\n\n"
                    "Orientierungsrahmen für typische Zuwendungen:\n\n"
                    "| Zuwendung | Wert | Ohne Genehmigung | Mit Genehmigung | Verboten |\n"
                    "|---|---|---|---|---|\n"
                    "| Werbeartikel (Kuli, Block, Tasse) | bis 10 Euro | ja | — | — |\n"
                    "| Wein, Pralinen, Adventskalender | 10-50 Euro | ja, ins Register | — | — |\n"
                    "| Präsentkorb, Geschäftsessen | 50-150 Euro | nein | Vorgesetzte | — |\n"
                    "| Sport- oder Kultur-Tickets | 150-500 Euro | nein | Compliance-Officer | bei laufender Vergabe |\n"
                    "| Wochenend-Reise, Tech-Geräte | über 500 Euro | nein | nur Geschäftsführung | bei Vergabe-Nähe |\n"
                    "| Bargeld, Gutscheine, Tankkarten | jeder Betrag | — | — | immer |\n\n"
                    "Drei Faustregeln aus der Compliance-Praxis helfen:\n\n"
                    "- **Transparenz-Test:** Könntest du das Geschenk offen am Empfang zeigen und in die nächste Teamsitzung mitbringen? Wenn nein, ist es zu groß.\n"
                    "- **Zeitungs-Test:** Was würde die Lokalzeitung schreiben, wenn sie morgen Bilder davon druckt? Wenn du dich für den Artikel schämen würdest, ist es zu viel.\n"
                    "- **Rollen-Tausch-Test:** Würde es dich stören, wenn dein Konkurrent dasselbe Geschenk von demselben Lieferanten bekäme? Wenn ja, ist es zu nah an Wettbewerbsverzerrung.\n\n"
                    "**Bargeld und bargeldnahe Zuwendungen** (Tankgutscheine, Amazon-Gutscheine, "
                    "Geldkarten) sind in jeder Höhe verboten. Sie haben keinerlei sachliche "
                    "Bezugsmöglichkeit zur Werbung oder Pflege einer Geschäftsbeziehung und werden "
                    "von Staatsanwaltschaften regelmäßig als Schmiergeld gewertet.\n\n"
                    "**Geschäftsessen** sind grundsätzlich erlaubt, wenn sie verhältnismäßig sind "
                    "(Bewirtungs-Charakter, nicht Luxus-Restaurant ohne Bezug), beide Seiten anwesend "
                    "sind und der dienstliche Anlass klar ist. Faustregel: bis 100 Euro pro Person "
                    "ohne Genehmigung, darüber mit Vorgesetzten-Freigabe.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Trage jede Zuwendung über 25 Euro (Wert, Anlass, Geber) in das Geschenke-Register im Compliance-Portal ein, auch wenn du sie ablehnst\n"
                    "2. Lehne Bargeld und Gutscheine ohne Ausnahme ab, höflich und schriftlich\n"
                    "3. Hole vor der Annahme von Zuwendungen über 50 Euro die Freigabe deiner Führungskraft ein, über 150 Euro die des Compliance-Officers\n"
                    "4. Lehne Einladungen während laufender Ausschreibungen oder Vertragsverhandlungen ab, unabhängig vom Wert\n"
                    "5. Verteile angenommene Geschenke (Wein, Pralinen) im Team — das nimmt den persönlichen Charakter und macht die Annahme transparent\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine Einkäuferin in einem Automotive-Zulieferer-Betrieb bekommt vom langjährigen "
                    "Schrauben-Lieferanten zum Jahresende einen Präsentkorb mit französischem Wein "
                    "und Trüffel-Konfekt im Wert von rund 180 Euro. Der Lieferant verhandelt gerade "
                    "die nächste Rahmenvertrags-Periode. Die Einkäuferin meldet das Geschenk noch "
                    "am gleichen Tag im Geschenke-Register, der Compliance-Officer entscheidet: der "
                    "Korb wird zurückgegeben mit einem höflichen Hinweis auf die Compliance-Richtlinie. "
                    "Hintergrund: 180 Euro liegen über der internen Genehmigungsgrenze, und die "
                    "laufende Vertragsverhandlung schließt eine Annahme aus, *auch* wenn der "
                    "Wert formal unter den 'klassischen' Schmiergeld-Schwellen liegt. Der Lieferant "
                    "reagiert mit Verständnis — solche Reaktionen schärfen das Profil eines "
                    "professionellen Compliance-Programms nach außen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf § 4 Abs. 5 EStG und § 37b EStG (Stand 2025, "
                    "Anhebung der Geschenke-Freigrenze auf 50 Euro durch Wachstumschancengesetz), "
                    "Bundesministerium der Finanzen *BMF-Schreiben zu Geschenken an Geschäftsfreunde* "
                    "(2024) sowie Transparency Deutschland *Hinweise zu Zuwendungen* (2024)."
                ),
            ),
            ModulDef(
                titel="Lieferanten- und Kundenbeziehungen",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Die meisten realen Korruptionsfälle im Mittelstand entstehen nicht durch "
                    "kriminelle Energie, sondern durch jahrelang gewachsene persönliche Beziehungen "
                    "und durch Strukturen, die niemand mehr hinterfragt. Du lernst typische "
                    "Risiko-Muster — von der 'Provisions-Zahlung' ohne Vertrag bis zum Kick-back — "
                    "und welche Meldewege dir offenstehen, wenn du selbst angesprochen wirst oder "
                    "etwas Verdächtiges beobachtest.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 299 StGB** — Bestechung im geschäftlichen Verkehr (Drittvorteils-Variante: "
                    "auch Vorteile an Familie oder Vereine sind erfasst)\n"
                    "- **§ 30 OWiG** — Verbandsgeldbuße: Unternehmen haftet bis 10 Mio. Euro für "
                    "Compliance-Verstöße von Leitungspersonen\n"
                    "- **HinSchG (Hinweisgeberschutzgesetz, 2023)** — Schutz von Hinweisgebern vor "
                    "Repressalien bei Meldung von Korruptionsverdacht\n"
                    "- **§ 17 UWG** — Verrat von Geschäfts- und Betriebsgeheimnissen "
                    "(Schnittmenge mit Kick-back-Konstellationen)\n\n"
                    "## Was musst du wissen\n\n"
                    "In der Industrie wiederholen sich bestimmte Korruptions-Muster mit erstaunlicher "
                    "Regelmäßigkeit. Wer sie kennt, erkennt sie:\n\n"
                    "- **Kick-back-Provision:** Lieferant zahlt einen Anteil des Auftragsvolumens zurück an die Person, die den Auftrag vergeben hat — getarnt als Beraterhonorar, Vermittlungsprovision oder über eine Briefkasten-GmbH\n"
                    "- **Scheinrechnung für 'Beratung':** der Vertriebspartner stellt Rechnungen für Leistungen, die nie erbracht wurden, das Geld fließt in Schwarzkassen für Schmiergeld\n"
                    "- **Familien-Konstrukte:** der Lieferant beschäftigt den Sohn oder die Ehepartnerin des Einkaufsleiters als 'externe Beraterin' zu auffällig guten Konditionen\n"
                    "- **Privatauftrag über die Firma:** der Lieferant verbaut beim Mitarbeitenden zu Hause kostenlos eine Solaranlage oder Küche und rechnet die Kosten in den nächsten Industrieauftrag\n"
                    "- **Sponsoring mit Hintertüren:** das Unternehmen sponsert den Sportverein, in dem der Einkaufsleiter im Vorstand sitzt — formal sauber, faktisch ein verdeckter Vorteil\n\n"
                    "**Auslandsgeschäft** verdient besondere Aufmerksamkeit. Schmiergeld an "
                    "ausländische Amtsträger ist nach **§ 335a StGB** und nach dem **OECD-"
                    "Bestechungs-Übereinkommen** strafbar — auch wenn es im jeweiligen Land "
                    "kulturell üblich oder geduldet ist. Sogenannte *Facilitation Payments* "
                    "(Klein-Schmiergelder zur Beschleunigung von Routine-Verfahren) sind nach "
                    "deutschem Recht keine Ausnahme.\n\n"
                    "**Meldewege im Unternehmen.** Wenn du Korruption beobachtest oder selbst "
                    "angesprochen wirst, stehen dir mehrere Wege offen:\n\n"
                    "| Weg | Wann sinnvoll | Schutz |\n"
                    "|---|---|---|\n"
                    "| Direkte Führungskraft | klare Fälle, vertrauensvolles Verhältnis | Arbeitsrecht |\n"
                    "| Compliance-Officer | mittelschwere Fälle, Beratungsbedarf | Vertraulichkeit garantiert |\n"
                    "| Internes Hinweisgebersystem (HinSchG) | bei Führungskraft-Verstrickung | HinSchG-Schutz vor Kündigung |\n"
                    "| Externe Meldestelle des Bundes | wenn intern keine Reaktion erfolgt | HinSchG-Schutz, anonym möglich |\n"
                    "| Staatsanwaltschaft | bei akuter Beweisvernichtungs-Gefahr | Hinweisgeberschutz nach HinSchG |\n\n"
                    "Anonyme Meldungen sind über das interne Hinweisgebersystem möglich und werden "
                    "ernsthaft verfolgt. Repressalien gegen Hinweisgeber (Kündigung, Mobbing, "
                    "Versetzung) sind nach **§ 36 HinSchG** verboten und kehren die Beweislast um: "
                    "der Arbeitgeber muss beweisen, dass eine Maßnahme *nicht* an die Meldung "
                    "gekoppelt war.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Frage nach Verträgen und Leistungsnachweisen, bevor du Rechnungen freigibst — 'Beratung' ohne nachvollziehbares Ergebnis ist ein Warnsignal\n"
                    "2. Dokumentiere Lieferanten-Auswahl mit mindestens drei Vergleichsangeboten ab der internen Wertgrenze (typisch 5.000 oder 10.000 Euro)\n"
                    "3. Melde Interessenkonflikte (Verwandtschaft, Beteiligung am Lieferanten, Nebentätigkeit) schriftlich an deine Führungskraft, bevor du in einer Vergabe-Entscheidung mitwirkst\n"
                    "4. Bei Schmiergeld-Angeboten: höflich aber klar ablehnen, sofort dem Compliance-Officer melden, Notiz mit Datum und Wortlaut anfertigen\n"
                    "5. Bei eigener Unsicherheit über einen vergangenen Vorgang: nutze das interne Hinweisgebersystem — Selbstanzeige in frühen Stadien wird im Strafverfahren regelmäßig stark strafmildernd berücksichtigt\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem Metallverarbeitungs-Betrieb in NRW vergibt der Werkstattleiter seit "
                    "Jahren sämtliche Wartungsaufträge für die CNC-Maschinen an dieselbe Firma. "
                    "Eine neue Buchhalterin fällt auf, dass die Stundensätze rund 30 Prozent über "
                    "dem Marktdurchschnitt liegen und der Wartungs-Lieferant zufällig auch das Auto "
                    "des Werkstattleiters wartet — ohne Rechnung. Sie meldet den Verdacht über das "
                    "interne Hinweisgebersystem. Eine externe Wirtschaftsprüfer-Kanzlei prüft, "
                    "findet über zwei Jahre Schaden in Höhe von rund 140.000 Euro und eine "
                    "Kick-back-Vereinbarung. Folgen: fristlose Kündigung des Werkstattleiters, "
                    "Strafanzeige nach § 299 StGB, Schadensersatz-Klage. Die Buchhalterin wird "
                    "später als Leiterin der neuen internen Compliance-Stelle befördert — der "
                    "Hinweisgeberschutz nach HinSchG hat in der Praxis funktioniert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf § 299 und § 335a StGB (Stand 2025), § 30 OWiG, "
                    "Hinweisgeberschutzgesetz (HinSchG, in Kraft seit 02.07.2023), "
                    "OECD *Convention on Combating Bribery of Foreign Public Officials* (2021), "
                    "ISO 37001:2025 sowie Transparency Deutschland *Korruption im Mittelstand — "
                    "Praxisleitfaden* (2024)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Norm regelt Bestechlichkeit und Bestechung im geschäftlichen Verkehr?",
                erklaerung="§ 299 StGB ist die zentrale Norm für Korruption zwischen Unternehmen. "
                "§§ 331 ff. betreffen Amtsträger, § 130 OWiG die Aufsichtspflicht der Geschäftsleitung.",
                optionen=_opts(
                    ("§ 130 OWiG", False),
                    ("§ 299 StGB", True),
                    ("§ 17 UWG", False),
                    ("§ 263 StGB (Betrug)", False),
                ),
            ),
            FrageDef(
                text="Wie hoch ist die steuerliche Freigrenze für Geschenke an Geschäftspartner seit dem 01.01.2024?",
                erklaerung="Mit dem Wachstumschancengesetz wurde § 4 Abs. 5 Nr. 1 EStG zum 01.01.2024 "
                "von 35 auf 50 Euro pro Person und Jahr angehoben.",
                optionen=_opts(
                    ("35 Euro", False),
                    ("44 Euro", False),
                    ("50 Euro", True),
                    ("60 Euro", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu Bargeld als Geschenk ist richtig?",
                erklaerung="Bargeld und bargeldnahe Zuwendungen (Tankkarten, Geldkarten, Amazon-Gutscheine) "
                "haben keinen Werbe-Charakter und werden regelmäßig als Schmiergeld gewertet.",
                optionen=_opts(
                    ("Bargeld bis 50 Euro ist erlaubt, weil Steuer-Freigrenze", False),
                    ("Bargeld ist in jeder Höhe verboten, ebenso Gutscheine und Tankkarten", True),
                    ("Bargeld ist erlaubt, wenn man es ins Geschenke-Register einträgt", False),
                    ("Bargeld bis 35 Euro ist sozialadäquat", False),
                ),
            ),
            FrageDef(
                text="Welcher Standard ist die internationale Norm für Anti-Bestechungs-Managementsysteme?",
                erklaerung="ISO 37001 ist seit 2016 die anerkannte internationale Norm, im Februar 2025 "
                "wurde die überarbeitete Fassung ISO 37001:2025 veröffentlicht.",
                optionen=_opts(
                    ("ISO 9001", False),
                    ("ISO 27001", False),
                    ("ISO 37001", True),
                    ("ISO 14001", False),
                ),
            ),
            FrageDef(
                text="Welche Strafe droht bei Bestechung im geschäftlichen Verkehr nach § 299 StGB?",
                erklaerung="§ 299 StGB sieht Freiheitsstrafe bis zu drei Jahren oder Geldstrafe vor; "
                "in besonders schweren Fällen (§ 300 StGB) bis zu fünf Jahren.",
                optionen=_opts(
                    ("Bußgeld bis 5.000 Euro", False),
                    ("Freiheitsstrafe bis zu 3 Jahren oder Geldstrafe, in schweren Fällen bis 5 Jahre", True),
                    ("Verwarnung beim ersten Mal, Geldstrafe ab dem zweiten Mal", False),
                    ("Nur arbeitsrechtliche Folgen, keine Strafbarkeit", False),
                ),
            ),
            FrageDef(
                text="Welcher Tatbestand erfasst Vorteilsannahme durch Amtsträger (z.B. Gewerbeaufsicht)?",
                erklaerung="§§ 331-335 StGB regeln die Korruption im öffentlichen Bereich: § 331 "
                "Vorteilsannahme, § 332 Bestechlichkeit (mit Pflichtverletzung), § 333/334 die Geberseite.",
                optionen=_opts(
                    ("§ 299 StGB", False),
                    ("§ 331 StGB (Vorteilsannahme)", True),
                    ("§ 263 StGB (Betrug)", False),
                    ("§ 266 StGB (Untreue)", False),
                ),
            ),
            FrageDef(
                text="Welche Rolle spielt die Wahrnehmung eines Vorteils im Vergleich zu seinem Geld-Wert?",
                erklaerung="Strafbar ist schon der *Anschein* der Käuflichkeit. Ein 30-Euro-Geschenk "
                "kurz vor einer Vergabe-Entscheidung kann gefährlicher sein als ein 200-Euro-Essen ohne Vergabe-Nähe.",
                optionen=_opts(
                    ("Der Geld-Wert ist allein maßgeblich, ab 50 Euro wird es strafbar", False),
                    ("Wahrnehmung und Kontext (Zeitpunkt, Beziehung) wiegen oft schwerer als der reine Wert", True),
                    ("Wahrnehmung ist nur für das Steuerrecht relevant, nicht für das Strafrecht", False),
                    ("Strafbar ist nur, wer die Bevorzugung tatsächlich gewährt", False),
                ),
            ),
            FrageDef(
                text="Ein Lieferant lädt dich zur Fußball-WM ein (Wert über 500 Euro). Du verhandelst gerade einen Vertrag mit ihm. Wie verhältst du dich?",
                erklaerung="Wert UND zeitliche Nähe zur Vergabe-Entscheidung sind beide problematisch. "
                "Ablehnen und dem Compliance-Officer melden ist die einzig richtige Reaktion.",
                optionen=_opts(
                    ("Annehmen, weil persönliche Freundschaft seit Jahren besteht", False),
                    ("Annehmen und Kosten anteilig selbst tragen, damit ist es entwertet", False),
                    ("Höflich ablehnen, schriftlich begründen, Compliance-Officer informieren", True),
                    ("Annehmen, aber nur wenn der Vertrag erst danach unterschrieben wird", False),
                ),
            ),
            FrageDef(
                text="Der CNC-Lieferant schickt zu Weihnachten einen Präsentkorb im Wert von rund 80 Euro. Was tust du?",
                erklaerung="80 Euro liegen über der typischen internen Genehmigungs-Schwelle (50 Euro). "
                "Eintrag ins Register und Freigabe-Anfrage bei der Führungskraft sind verpflichtend.",
                optionen=_opts(
                    ("Stillschweigend annehmen, ist ja nur einmal im Jahr", False),
                    ("Ins Geschenke-Register eintragen und Freigabe der Führungskraft einholen", True),
                    ("Direkt zurückschicken ohne Meldung — schnell und unkompliziert", False),
                    ("Annehmen und unter den Kollegen verteilen, dann ist der persönliche Vorteil weg", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine Wartungsfirma beauftragen. Der Inhaber ist dein Schwager. Wie gehst du vor?",
                erklaerung="Interessenkonflikte müssen *vor* einer Vergabe-Entscheidung schriftlich "
                "offengelegt werden. Die Vergabe selbst sollte dann jemand anderes verantworten.",
                optionen=_opts(
                    ("Beauftragen, wenn die Firma gute Arbeit leistet — kein Problem", False),
                    ("Interessenkonflikt schriftlich melden, Vergabe-Entscheidung delegieren", True),
                    ("Beauftragen, aber drei Vergleichsangebote einholen — dann ist es sauber", False),
                    ("Schwager bitten, einen Strohmann-Vertrag über eine andere Firma zu schließen", False),
                ),
            ),
            FrageDef(
                text="Du beobachtest, dass die Wartungsfirma deines Werkstattleiters dessen privates Auto kostenlos wartet. Was tust du?",
                erklaerung="Das ist ein klassisches Kick-back-Muster. Hinweisgebersystem nutzen — anonym "
                "möglich, mit HinSchG-Schutz vor Repressalien.",
                optionen=_opts(
                    ("Ignorieren, ist nicht dein Bereich", False),
                    ("Werkstattleiter direkt zur Rede stellen, damit er es einstellt", False),
                    ("Über das interne Hinweisgebersystem melden (HinSchG)", True),
                    ("Bei der nächsten Kaffeepause beiläufig im Kollegenkreis erwähnen", False),
                ),
            ),
            FrageDef(
                text="Bei einem Auslandsgeschäft erwartet ein Zoll-Beamter ein 'kleines Trinkgeld', damit der Container schneller frei wird. Was ist deine Pflicht?",
                erklaerung="Sogenannte *Facilitation Payments* an ausländische Amtsträger sind nach "
                "§ 335a StGB und dem OECD-Bestechungs-Übereinkommen in Deutschland strafbar, auch "
                "wenn sie im Land kulturell üblich sind.",
                optionen=_opts(
                    ("Zahlen, weil das im Land üblicherweise erwartet wird", False),
                    ("Zahlen und im Reisekostenbericht als 'sonstige Auslage' verbuchen", False),
                    ("Ablehnen, Vorgang dokumentieren, Compliance-Officer melden", True),
                    ("Zahlen, weil unter 50 Euro die Steuer-Freigrenze gilt", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu Geschäftsessen ist richtig?",
                erklaerung="Geschäftsessen sind erlaubt, wenn sie verhältnismäßig, beidseitig "
                "besucht und mit klarem dienstlichem Anlass sind. Faustregel: bis 100 Euro pro Person, "
                "darüber Genehmigung der Führungskraft.",
                optionen=_opts(
                    ("Geschäftsessen sind generell verboten, weil immer ein Vorteil", False),
                    ("Verhältnismäßige Geschäftsessen mit dienstlichem Anlass sind erlaubt", True),
                    ("Geschäftsessen sind nur bis 35 Euro pro Person zulässig", False),
                    ("Geschäftsessen sind nur in Ausnahmefällen mit Genehmigung der Geschäftsführung erlaubt", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'Unrechtsvereinbarung' im Sinne des § 299 StGB?",
                erklaerung="Die Verabredung 'Vorteil gegen Bevorzugung' ist *schon* strafbar, "
                "unabhängig davon, ob die Bevorzugung später tatsächlich erfolgt.",
                optionen=_opts(
                    ("Die schriftliche Bestätigung einer Bestechung", False),
                    ("Die bloße Verabredung zwischen Vorteilsgeber und -nehmer, schon vor Vollzug strafbar", True),
                    ("Eine Verabredung, die mindestens zwei Mal vollzogen wurde", False),
                    ("Eine Vereinbarung mit ausländischen Geschäftspartnern", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage über Werbegeschenke (Kugelschreiber, Block, Tasse mit Logo) ist richtig?",
                erklaerung="Werbeartikel mit klarem Werbe-Charakter und geringem Wert (bis ca. 10 Euro) "
                "gelten als sozialadäquat und bedürfen keiner Genehmigung.",
                optionen=_opts(
                    ("Auch Werbekugelschreiber müssen vor Annahme genehmigt werden", False),
                    ("Werbeartikel bis ca. 10 Euro sind sozialadäquat und unbedenklich", True),
                    ("Werbeartikel sind nur erlaubt, wenn das Logo des Gebers gut sichtbar ist", False),
                    ("Werbeartikel dürfen nur auf Messen angenommen werden, nicht im Büro", False),
                ),
            ),
            FrageDef(
                text="Du erhältst eine Schmiergeld-Anfrage von einem Vertriebspartner per E-Mail. Was tust du *zuerst*?",
                erklaerung="Beweise sichern (E-Mail nicht löschen!), Vorgang mit Datum und Wortlaut "
                "notieren, sofort Compliance-Officer informieren. Eigene Antwort erst nach Absprache.",
                optionen=_opts(
                    ("E-Mail löschen und vergessen — Problem gelöst", False),
                    ("Direkt antworten und scharf ablehnen, damit der Vorgang erledigt ist", False),
                    ("E-Mail aufbewahren, Vorgang dokumentieren, Compliance-Officer informieren", True),
                    ("Den Vertriebspartner anrufen und ihn um eine schriftliche Klarstellung bitten", False),
                ),
            ),
            FrageDef(
                text="Welche Behauptung über das Hinweisgeberschutzgesetz (HinSchG) ist *falsch*?",
                erklaerung="HinSchG schützt Hinweisgeber ausdrücklich auch bei anonymer Meldung und "
                "kehrt die Beweislast um. Eine namentliche Meldung ist NICHT Voraussetzung.",
                optionen=_opts(
                    ("Anonyme Meldungen werden durch interne Hinweisgebersysteme erfasst", False),
                    ("Repressalien gegen Hinweisgeber sind verboten (§ 36 HinSchG)", False),
                    ("Hinweisgeber müssen sich namentlich zu erkennen geben, um Schutz zu erhalten", True),
                    ("Der Arbeitgeber muss beweisen, dass eine Maßnahme nicht an die Meldung gekoppelt ist", False),
                ),
            ),
            FrageDef(
                text="Was ist ein 'Kick-back'?",
                erklaerung="Kick-back ist die Rückzahlung eines Anteils des Auftragsvolumens an die "
                "vergebende Person, oft getarnt als Beraterhonorar oder über eine Briefkasten-Firma.",
                optionen=_opts(
                    ("Eine erlaubte Provision an externe Vertreter", False),
                    ("Eine Rückzahlung an die vergebende Person, getarnt als Provision oder Beraterhonorar", True),
                    ("Ein Rabatt, der dem Endkunden weitergegeben wird", False),
                    ("Eine Sondervereinbarung im internationalen Geschäft", False),
                ),
            ),
            FrageDef(
                text="Welcher Test eignet sich NICHT als Faustregel zur Bewertung einer Zuwendung?",
                erklaerung="Der 'Familien-Test' existiert nicht als Compliance-Faustregel. Etabliert sind "
                "Transparenz-Test, Zeitungs-Test (öffentlich akzeptabel?) und Rollen-Tausch-Test "
                "(Konkurrent gleicher Behandlung?).",
                optionen=_opts(
                    ("Transparenz-Test (kann ich es offen zeigen?)", False),
                    ("Zeitungs-Test (würde ich mich für den Artikel schämen?)", False),
                    ("Familien-Test (was würde meine Familie sagen?)", True),
                    ("Rollen-Tausch-Test (wäre es OK für den Konkurrenten?)", False),
                ),
            ),
            FrageDef(
                text="Welche Konsequenz droht dem *Unternehmen* (nicht der Person) bei einem nachgewiesenen Korruptionsfall?",
                erklaerung="§ 30 OWiG sieht eine Verbandsgeldbuße von bis zu 10 Mio. Euro vor, dazu "
                "kann nach § 17 OWiG der wirtschaftliche Vorteil abgeschöpft werden — Gesamthöhe oft "
                "weit darüber.",
                optionen=_opts(
                    ("Keine Folgen — nur die handelnde Person haftet persönlich", False),
                    ("Verbandsgeldbuße bis 10 Mio. Euro nach § 30 OWiG, plus Vorteilsabschöpfung", True),
                    ("Maximal 5.000 Euro Bußgeld, da Wirtschaftsstrafrecht milder als Privatrecht", False),
                    ("Nur Ausschluss von öffentlichen Vergaben, keine Geldbuße", False),
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
                    "## Worum geht's?\n\n"
                    "Der Werkhallen-Alltag im Mittelstand kennt eingeschliffene Routinen: "
                    "der 'witzige' Spitzname für den polnischen Kollegen, der Spruch in "
                    "der Frühschicht über die Berufsschülerin, die Beförderung, bei der "
                    "die schwangere Schichtführerin 'erstmal nicht in Frage kommt'. Was "
                    "viele für rauen Werkhallen-Ton halten, ist juristisch oft "
                    "**Benachteiligung** nach dem Allgemeinen Gleichbehandlungsgesetz. "
                    "Dieses Modul zeigt dir, welche acht Merkmale das Gesetz schützt und "
                    "in welchen vier Formen Diskriminierung passiert — auch wenn niemand "
                    "es 'so gemeint' hat.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- *§ 1 AGG* — acht geschützte Merkmale (Schutzbereich)\n"
                    "- *§ 3 AGG* — vier Formen der Benachteiligung\n"
                    "- *§ 7 AGG* — Benachteiligungsverbot im Beschäftigungsverhältnis\n"
                    "- *§ 12 Abs. 1 AGG* — Pflicht des Arbeitgebers zu Schutzmaßnahmen\n"
                    "- *§ 12 Abs. 2 AGG* — Pflicht zur Schulung der Beschäftigten\n\n"
                    "## Was musst du wissen\n\n"
                    "Das AGG schützt vor Benachteiligung wegen acht abschließend "
                    "aufgezählter Merkmale. Andere Eigenschaften (z. B. Haarfarbe, "
                    "Gewerkschaftszugehörigkeit, Raucher:innen-Status) fallen NICHT unter "
                    "den AGG-Schutz, können aber über andere Gesetze geschützt sein.\n\n"
                    "| Merkmal nach § 1 AGG | Werkhallen-Beispiel |\n"
                    "|---|---|\n"
                    "| Rasse oder ethnische Herkunft | Spitzname mit Migrationsbezug |\n"
                    "| Geschlecht | Frau wird bei Beförderung übergangen |\n"
                    "| Religion oder Weltanschauung | Kopftuch-Verbot ohne Sachgrund |\n"
                    "| Behinderung | Werkbank zu hoch für Rollstuhl |\n"
                    "| Alter | 58-jähriger Kollege bei Schulung 'übergangen' |\n"
                    "| Sexuelle Identität | Sprüche über 'Schwule' in der Pause |\n\n"
                    "Das AGG kennt vier **Benachteiligungsformen** nach § 3 AGG:\n\n"
                    "Eine *unmittelbare Benachteiligung* liegt vor, wenn jemand "
                    "wegen eines geschützten Merkmals direkt schlechter behandelt wird "
                    "als eine vergleichbare Person — etwa wenn eine Stellenausschreibung "
                    "lautet 'junges, dynamisches Team gesucht'.\n\n"
                    "Eine *mittelbare Benachteiligung* entsteht, wenn eine "
                    "scheinbar neutrale Regel eine geschützte Gruppe besonders trifft, "
                    "ohne sachlichen Grund. Beispiel: Der Arbeitgeber verlangt für eine "
                    "Stelle 'fließendes muttersprachliches Deutsch', obwohl der Job nur "
                    "Verständigung auf B2-Niveau erfordert — das benachteiligt mittelbar "
                    "Menschen mit Migrationsgeschichte.\n\n"
                    "Eine *Belästigung* sind unerwünschte Verhaltensweisen, die ein "
                    "von Einschüchterungen, Anfeindungen, Erniedrigungen oder "
                    "Beleidigungen geprägtes Umfeld schaffen — also auch der dauerhafte "
                    "'Scherz', das Nachäffen eines Akzents oder das Ausschließen aus dem "
                    "Pausenkreis.\n\n"
                    "*Sexuelle Belästigung* umfasst unerwünschtes sexuell bestimmtes "
                    "Verhalten: Sprüche, Blicke, Berührungen, das ungebetene Versenden "
                    "von Bildern. Ob es 'so gemeint' war, ist juristisch unerheblich — "
                    "entscheidend ist, wie es bei der betroffenen Person ankommt.\n\n"
                    "Wichtig: Auch die Anweisung an andere, zu diskriminieren, ist nach "
                    "§ 3 Abs. 5 AGG selbst eine Benachteiligung. Wer als Schichtführer "
                    "sagt 'der Neue kriegt die Drecksarbeit, der versteht eh kein "
                    "Deutsch', verstößt selbst gegen das AGG.\n\n"
                    "## Was musst du tun\n\n"
                    "Im Werkhallen-Alltag heißt das konkret:\n\n"
                    "1. Mache keine Witze über Herkunft, Geschlecht, Alter, Behinderung, "
                    "Religion oder sexuelle Identität — auch nicht 'unter Männern' oder "
                    "'als Spaß'\n"
                    "2. Greife ein, wenn du erlebst, dass Kolleg:innen schlecht behandelt "
                    "werden — schweigen normalisiert das Verhalten\n"
                    "3. Sprich Betroffene nach einem Vorfall an, frage wie es ihnen geht "
                    "und ob sie Unterstützung wollen\n"
                    "4. Melde wiederholtes Fehlverhalten an Vorgesetzte oder die "
                    "Beschwerdestelle — auch als Zeug:in\n"
                    "5. Hinterfrage Auswahl- oder Beförderungs-Entscheidungen, die ein "
                    "Muster ergeben (immer nur Männer, immer nur Deutsche)\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Metallverarbeitung läuft seit Monaten ein Spitzname für "
                    "den polnischen Kollegen Marek: 'Marek, der Klempner' — eine "
                    "Anspielung auf das Polen-Klischee. Marek lacht zunächst mit, "
                    "irgendwann nicht mehr. Bei der Beförderung zum Vorarbeiter geht er "
                    "leer aus, obwohl er der dienstälteste der drei Kandidaten ist. Die "
                    "Schichtleitung begründet: 'Du bist halt nicht so ein Anführer-Typ.' "
                    "Marek wendet sich an die Beschwerdestelle nach § 13 AGG. Die "
                    "interne Prüfung ergibt: der Spitzname ist *Belästigung* nach § 3 "
                    "Abs. 3 AGG, die Auswahl-Entscheidung erfüllt zusätzlich die "
                    "Voraussetzungen einer *unmittelbaren Benachteiligung* wegen "
                    "ethnischer Herkunft. Die Firma zahlt eine Entschädigung und richtet "
                    "ein Anti-Bias-Training für alle Schichtführer ein.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf Allgemeines Gleichbehandlungsgesetz (AGG, "
                    "Stand 2025), §§ 1, 3, 7, 12 — abrufbar unter "
                    "*gesetze-im-internet.de/agg*. Erläuterungen nach den "
                    "Themenseiten der *Antidiskriminierungsstelle des Bundes* (ADS, "
                    "antidiskriminierungsstelle.de)."
                ),
            ),
            ModulDef(
                titel="Beschwerderecht & betriebliche Beschwerdestelle",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Wer im Werkhallen-Alltag diskriminiert wird, hat zwei zentrale "
                    "Rechte aus dem AGG: das **Beschwerderecht** nach § 13 und den "
                    "**Entschädigungsanspruch** nach § 15. Beide sind an Fristen und "
                    "Verfahren gebunden, die viele Beschäftigte nicht kennen — und die "
                    "Ansprüche verfallen still, wenn man zu lange wartet. Dieses Modul "
                    "zeigt dir, wie die betriebliche Beschwerdestelle funktioniert, "
                    "welche Frist du im Auge behalten musst und wie der Arbeitgeber dich "
                    "schützt, wenn du dich beschwerst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- *§ 12 Abs. 3 AGG* — Pflicht zur Unterbindung von Verstößen\n"
                    "- *§ 13 AGG* — Beschwerderecht und betriebliche Beschwerdestelle\n"
                    "- *§ 15 Abs. 1 AGG* — Anspruch auf Schadensersatz\n"
                    "- *§ 15 Abs. 2 AGG* — Anspruch auf Entschädigung in Geld\n"
                    "- *§ 15 Abs. 4 AGG* — Zwei-Monats-Frist zur schriftlichen "
                    "Geltendmachung\n"
                    "- *§ 16 AGG* — Maßregelungsverbot\n\n"
                    "## Was musst du wissen\n\n"
                    "Jedes Unternehmen mit Beschäftigten ist nach § 13 AGG verpflichtet, "
                    "eine **Beschwerdestelle** einzurichten. Diese Stelle nimmt "
                    "Beschwerden über Benachteiligungen entgegen, prüft den Sachverhalt "
                    "und teilt dir das Ergebnis mit. In Mittelstands-Betrieben ist das "
                    "oft die Personalleitung, eine HR-Person oder ein Mitglied der "
                    "Geschäftsführung. In größeren Werken kann es ein eigenes Gremium "
                    "mit Betriebsrat-Beteiligung sein. Wer die Beschwerdestelle ist, "
                    "muss dir der Arbeitgeber aktiv bekannt machen — etwa per Aushang, "
                    "Intranet oder im Pflicht-Onboarding.\n\n"
                    "Wichtige Eigenschaften der Beschwerdestelle:\n\n"
                    "- Du darfst dich beschweren, ohne den Dienstweg über deine direkte "
                    "Führungskraft zu gehen — gerade dann, wenn die Führungskraft "
                    "selbst Teil des Problems ist\n"
                    "- Die Beschwerde kann mündlich, schriftlich oder per E-Mail "
                    "erfolgen — die Stelle muss sie aber dokumentieren\n"
                    "- Es gibt keine Mindest-'Schwere' — auch ein einzelner Spruch "
                    "kann beschwerdefähig sein\n"
                    "- Die Beschwerde muss inhaltlich geprüft werden, auch wenn du sie "
                    "später zurückziehst\n\n"
                    "Zentral ist die Frist nach § 15 Abs. 4 AGG: Wer einen "
                    "*Entschädigungs- oder Schadensersatzanspruch* gegen den "
                    "Arbeitgeber durchsetzen will, muss diesen innerhalb von **zwei "
                    "Monaten** schriftlich geltend machen. Die Frist beginnt mit dem "
                    "Zeitpunkt, in dem du Kenntnis von der Benachteiligung erlangt hast "
                    "— bei einer abgelehnten Bewerbung mit Zugang der Ablehnung. Nach "
                    "Ablauf ist der Anspruch verloren, auch wenn der Vorfall sonst "
                    "eindeutig wäre. Klage auf Entschädigung muss zusätzlich innerhalb "
                    "von drei Monaten nach schriftlicher Geltendmachung beim "
                    "Arbeitsgericht eingehen.\n\n"
                    "Die Höhe der Entschädigung setzt das Arbeitsgericht fest. "
                    "Typische Größenordnungen: ein bis drei Monatsgehälter bei "
                    "diskriminierender Stellenabsage, mehrere Monatsgehälter bei "
                    "sexueller Belästigung durch Vorgesetzte.\n\n"
                    "Das **Maßregelungsverbot** nach § 16 AGG schützt dich: Der "
                    "Arbeitgeber darf dich nicht benachteiligen, weil du dich auf das "
                    "AGG berufst oder eine Beschwerde eingereicht hast — weder durch "
                    "Abmahnung, Versetzung, Schichtnachteil noch durch Kündigung. Eine "
                    "Kündigung 'als Reaktion auf' eine AGG-Beschwerde ist regelmäßig "
                    "unwirksam.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du selbst oder als Zeug:in einen AGG-Verstoß erlebst:\n\n"
                    "1. Schreibe sofort ein Gedächtnisprotokoll — Datum, Uhrzeit, Ort, "
                    "Beteiligte, exakter Wortlaut wenn möglich, anwesende Zeug:innen\n"
                    "2. Sprich Vertraute an: Betriebsrat, "
                    "Schwerbehindertenvertretung, Vertrauensperson — sie können "
                    "begleiten und beraten\n"
                    "3. Reiche die Beschwerde bei der betrieblichen Beschwerdestelle "
                    "ein — schriftlich oder per E-Mail, damit ein Eingangsdatum "
                    "festgehalten ist\n"
                    "4. Achte auf die *zwei Monate* nach § 15 Abs. 4 AGG, wenn du "
                    "Entschädigung verlangen willst — die Frist läuft auch dann, wenn "
                    "die Beschwerdestelle noch prüft\n"
                    "5. Hole dir bei Bedarf externe Beratung bei der "
                    "*Antidiskriminierungsstelle des Bundes* (ADS) oder einer "
                    "Fachanwältin für Arbeitsrecht\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine Schichtführerin in einem Kunststoff-Verarbeiter ist in der "
                    "20. Schwangerschaftswoche. Bei der Besetzung der frei gewordenen "
                    "Stelle der Produktionsleitung wird sie übergangen, obwohl sie die "
                    "qualifizierteste Bewerberin ist. Die Begründung der "
                    "Geschäftsführung: 'Du fällst ja eh erstmal aus, wir brauchen "
                    "Kontinuität.' Sie schreibt am gleichen Abend ein Protokoll, geht "
                    "drei Tage später zur Beschwerdestelle (Personalleiterin) und macht "
                    "vier Wochen nach der Absage schriftlich einen "
                    "Entschädigungsanspruch geltend — innerhalb der Zwei-Monats-Frist "
                    "nach § 15 Abs. 4 AGG. Die Geschäftsführung erkennt die "
                    "Diskriminierung wegen *Geschlecht und Schwangerschaft* an, zahlt "
                    "drei Monatsgehälter Entschädigung und besetzt die Stelle neu mit "
                    "Vertretungsregelung. Eine Kündigung der Schichtführerin wegen "
                    "ihrer Beschwerde wäre nach § 16 AGG unzulässig gewesen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf Allgemeines Gleichbehandlungsgesetz (AGG, "
                    "Stand 2025), §§ 13, 15, 16 — abrufbar unter "
                    "*gesetze-im-internet.de/agg*. Praxis-Hinweise nach den FAQ der "
                    "*Antidiskriminierungsstelle des Bundes* (ADS) zu "
                    "Arbeitgeber-Pflichten und Beschwerderecht."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wie viele Merkmale schützt das AGG nach § 1 ausdrücklich?",
                erklaerung="§ 1 AGG zählt sechs Merkmale auf (Rasse/ethnische Herkunft, "
                "Geschlecht, Religion/Weltanschauung, Behinderung, Alter, sexuelle "
                "Identität). Andere Eigenschaften wie Haarfarbe oder Raucherstatus "
                "fallen NICHT unter den AGG-Schutz.",
                optionen=_opts(
                    ("Vier Merkmale", False),
                    ("Sechs Merkmale", True),
                    ("Acht Merkmale", False),
                    ("Beliebig viele, sobald jemand sich benachteiligt fühlt", False),
                ),
            ),
            FrageDef(
                text="Welches der folgenden Merkmale ist KEIN geschütztes Merkmal nach § 1 AGG?",
                erklaerung="Die Gewerkschaftszugehörigkeit ist über andere Gesetze "
                "geschützt (Koalitionsfreiheit Art. 9 GG), aber nicht über das AGG. "
                "Die anderen vier sind in § 1 AGG aufgezählt.",
                optionen=_opts(
                    ("Behinderung", False),
                    ("Alter", False),
                    ("Gewerkschaftszugehörigkeit", True),
                    ("Sexuelle Identität", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'mittelbare Benachteiligung' nach § 3 Abs. 2 AGG?",
                erklaerung="Eine scheinbar neutrale Regel kann eine geschützte Gruppe "
                "besonders treffen, ohne dass ein sachlicher Grund die Regel "
                "rechtfertigt — das ist mittelbare Benachteiligung. Beispiel: "
                "'muttersprachliches Deutsch' für einen Job, der das nicht braucht.",
                optionen=_opts(
                    ("Eine direkt ausgesprochene Schlechterstellung wegen Geschlecht", False),
                    ("Eine scheinbar neutrale Regel, die eine geschützte Gruppe besonders trifft", True),
                    ("Ein Streit zwischen zwei Kolleg:innen", False),
                    ("Eine Benachteiligung, die niemand bemerkt", False),
                ),
            ),
            FrageDef(
                text="Wie lange hast du nach § 15 Abs. 4 AGG Zeit, einen Entschädigungsanspruch schriftlich geltend zu machen?",
                erklaerung="Die Frist beträgt zwei Monate ab Kenntnis der "
                "Benachteiligung (bzw. bei Bewerbungen ab Zugang der Ablehnung). "
                "Nach Ablauf ist der Anspruch verloren.",
                optionen=_opts(
                    ("Zwei Wochen", False),
                    ("Zwei Monate", True),
                    ("Sechs Monate", False),
                    ("Drei Jahre wie die allgemeine Verjährungsfrist", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur betrieblichen Beschwerdestelle nach § 13 AGG ist richtig?",
                erklaerung="§ 13 AGG verpflichtet jeden Arbeitgeber, eine "
                "Beschwerdestelle einzurichten — unabhängig von der "
                "Unternehmensgröße. Die Beschwerde kann formfrei (auch mündlich) "
                "eingereicht werden.",
                optionen=_opts(
                    ("Sie ist nur in Unternehmen ab 500 Beschäftigten Pflicht", False),
                    ("Jeder Arbeitgeber muss eine einrichten — unabhängig von der Größe", True),
                    ("Beschwerden müssen ausschließlich schriftlich per Einschreiben erfolgen", False),
                    ("Sie ist nur für die Geschäftsführung zugänglich", False),
                ),
            ),
            FrageDef(
                text="Was schützt § 16 AGG (Maßregelungsverbot)?",
                erklaerung="Wer eine AGG-Beschwerde einreicht oder als Zeug:in aussagt, "
                "darf deshalb nicht benachteiligt werden — weder durch Abmahnung, "
                "Versetzung noch Kündigung. Eine Kündigung 'als Reaktion auf' eine "
                "Beschwerde ist regelmäßig unwirksam.",
                optionen=_opts(
                    ("Das Recht des Arbeitgebers, Maßregelungen auszusprechen", False),
                    ("Den Schutz vor Benachteiligung wegen Inanspruchnahme von AGG-Rechten", True),
                    ("Die Lohnfortzahlung im Krankheitsfall", False),
                    ("Das Recht auf Pausenzeiten", False),
                ),
            ),
            FrageDef(
                text="Welche Form der Diskriminierung liegt bei der Stellenausschreibung 'junges, dynamisches Team' vor?",
                erklaerung="Die Formulierung benachteiligt ältere Bewerber:innen "
                "direkt wegen des Merkmals Alter — das ist eine *unmittelbare* "
                "Benachteiligung nach § 3 Abs. 1 AGG.",
                optionen=_opts(
                    ("Mittelbare Benachteiligung", False),
                    ("Unmittelbare Benachteiligung wegen Alters", True),
                    ("Belästigung", False),
                    ("Keine Benachteiligung, weil 'jung' kein geschütztes Merkmal ist", False),
                ),
            ),
            FrageDef(
                text="In der Frühschicht macht ein Kollege regelmäßig sexistische Sprüche über die einzige Frau im Team. Sie lacht mit, fühlt sich aber unwohl. Wie ist das einzuordnen?",
                erklaerung="Auch wenn die Betroffene aus Selbstschutz mitlacht, ist es "
                "*Belästigung* nach § 3 Abs. 3 AGG: unerwünschtes Verhalten, das ein "
                "erniedrigendes Umfeld schafft. Auf die subjektive Absicht des "
                "Sprechenden kommt es nicht an.",
                optionen=_opts(
                    ("Kein AGG-Verstoß, weil sie mitlacht", False),
                    ("Belästigung nach § 3 Abs. 3 AGG, weil ein erniedrigendes Umfeld entsteht", True),
                    ("Nur ein Verstoß, wenn sie die Sprüche schriftlich rügt", False),
                    ("Nur Mobbing nach BGB, nicht AGG", False),
                ),
            ),
            FrageDef(
                text="Du bist Zeug:in eines AGG-Verstoßes gegen einen Kollegen. Wie verhältst du dich?",
                erklaerung="Sofortiges Gedächtnisprotokoll sichert Beweise, der Hinweis "
                "auf die Beschwerdestelle hilft dem Betroffenen, das Maßregelungsverbot "
                "schützt dich selbst nach § 16 AGG.",
                optionen=_opts(
                    ("Vergessen — geht dich nichts an", False),
                    ("Gedächtnisprotokoll schreiben, Betroffenen ansprechen, ggf. selbst Beschwerde einreichen", True),
                    ("Direkt in den sozialen Medien posten", False),
                    ("Erst handeln, wenn der Betroffene dich darum bittet", False),
                ),
            ),
            FrageDef(
                text="Eine schwangere Schichtführerin wird bei einer Beförderung 'wegen Ausfallzeit' übergangen. Was ist juristisch korrekt?",
                erklaerung="Schwangerschaft ist ein Aspekt des geschützten Merkmals "
                "Geschlecht. Eine Beförderungs-Entscheidung darauf zu stützen ist "
                "*unmittelbare Benachteiligung* nach § 3 Abs. 1 AGG.",
                optionen=_opts(
                    ("Zulässig, weil betriebliche Kontinuität ein sachlicher Grund ist", False),
                    ("Unmittelbare Benachteiligung wegen Geschlechts — verboten nach § 7 AGG", True),
                    ("Nur dann verboten, wenn der Mutterschutz schon begonnen hat", False),
                    ("Eine Frage des Arbeitgeber-Ermessens, AGG greift hier nicht", False),
                ),
            ),
            FrageDef(
                text="Du erlebst, dass die Werkbank deines neuen Rollstuhl-fahrenden Kollegen nicht angepasst wurde. Was ist die richtige Reaktion?",
                erklaerung="Fehlende angemessene Vorkehrungen für Menschen mit "
                "Behinderung sind eine Benachteiligung nach AGG und SGB IX. Schnelle "
                "interne Meldung bringt die Sache in die Lösung.",
                optionen=_opts(
                    ("Abwarten, ob er sich beschwert", False),
                    ("An die Schichtleitung melden — angemessene Vorkehrungen sind Arbeitgeber-Pflicht", True),
                    ("Selbst die Werkbank umbauen", False),
                    ("Den Kollegen bitten, sich einen anderen Arbeitsplatz zu suchen", False),
                ),
            ),
            FrageDef(
                text="Ab wann beginnt die Zwei-Monats-Frist nach § 15 Abs. 4 AGG bei einer abgelehnten Bewerbung?",
                erklaerung="Bei Bewerbungen beginnt die Frist mit dem Zugang der "
                "schriftlichen Ablehnung — danach hat man zwei Monate, um Ansprüche "
                "schriftlich geltend zu machen.",
                optionen=_opts(
                    ("Mit Abgabe der Bewerbung", False),
                    ("Mit Zugang der Ablehnung beim/bei der Bewerber:in", True),
                    ("Mit dem ersten Bewerbungs-Gespräch", False),
                    ("Mit dem Tag des angedachten Stellenantritts", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage über die Anweisung zur Diskriminierung ist richtig?",
                erklaerung="§ 3 Abs. 5 AGG: Die Anweisung an andere, jemanden wegen "
                "eines geschützten Merkmals zu benachteiligen, ist selbst eine "
                "Benachteiligung — auch wenn die Person, die anweist, niemanden "
                "persönlich diskriminiert.",
                optionen=_opts(
                    ("Nur die ausführende Person ist verantwortlich", False),
                    ("Wer zur Diskriminierung anweist, diskriminiert selbst (§ 3 Abs. 5 AGG)", True),
                    ("Anweisungen sind nur dann AGG-relevant, wenn sie schriftlich ergehen", False),
                    ("Der Schichtführer ist als Vorgesetzter immer frei in seinen Anweisungen", False),
                ),
            ),
            FrageDef(
                text="Bei welchem dieser Sätze handelt es sich um eine AGG-Belästigung?",
                erklaerung="Das Nachäffen eines Akzents zielt direkt auf das Merkmal "
                "ethnische Herkunft und schafft ein erniedrigendes Umfeld — § 3 Abs. 3 "
                "AGG. Die anderen Aussagen sind kritisch, aber nicht merkmalsbezogen.",
                optionen=_opts(
                    ("'Der neue Praktikant ist langsam.'", False),
                    ("'Hab' ich dir doch schon dreimal erklärt!'", False),
                    ("Nachäffen des Akzents eines Kollegen 'als Spaß'", True),
                    ("'Diese Frühschicht ist anstrengend.'", False),
                ),
            ),
            FrageDef(
                text="Welche Pflicht hat der Arbeitgeber nach § 12 Abs. 2 AGG?",
                erklaerung="§ 12 Abs. 2 AGG verpflichtet den Arbeitgeber, Beschäftigte "
                "in geeigneter Weise zur Verhinderung von Benachteiligungen zu schulen "
                "— genau das ist diese Pflichtunterweisung.",
                optionen=_opts(
                    ("Jährliche Spende an die Antidiskriminierungsstelle", False),
                    ("Schulung der Beschäftigten zur Verhinderung von Benachteiligungen", True),
                    ("Quotenpflicht von 50 % Frauen in jeder Schicht", False),
                    ("Veröffentlichung aller Beschwerden im Intranet", False),
                ),
            ),
            FrageDef(
                text="Welche Anlaufstelle ist NICHT für AGG-Beschwerden zuständig?",
                erklaerung="Das Finanzamt ist für Steuerangelegenheiten zuständig. "
                "Beschwerdestelle nach § 13 AGG, Betriebsrat und ADS sind die "
                "richtigen Adressen.",
                optionen=_opts(
                    ("Betriebliche Beschwerdestelle nach § 13 AGG", False),
                    ("Antidiskriminierungsstelle des Bundes (ADS)", False),
                    ("Das Finanzamt", True),
                    ("Betriebsrat oder Schwerbehindertenvertretung", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Reaktionen des Arbeitgebers auf eine AGG-Beschwerde ist nach § 16 AGG unzulässig?",
                erklaerung="Eine Versetzung in die schlechtere Schicht 'wegen' der "
                "Beschwerde verstößt direkt gegen das Maßregelungsverbot des § 16 "
                "AGG — auch wenn formal kein Lohnverlust entsteht.",
                optionen=_opts(
                    ("Sachliche Prüfung der Beschwerde durch die Beschwerdestelle", False),
                    ("Anhörung der beteiligten Personen", False),
                    ("Versetzung des/der Beschwerdeführer:in in die schlechtere Schicht", True),
                    ("Schulung des betroffenen Teams im Anschluss", False),
                ),
            ),
            FrageDef(
                text="Du erlebst, dass der Schichtführer einem türkischstämmigen Kollegen sagt: 'Du machst die Drecksarbeit, du verstehst eh kein Deutsch.' Welche Tatbestände sind erfüllt?",
                erklaerung="Die Aussage ist direkt diskriminierend (unmittelbare "
                "Benachteiligung wegen ethnischer Herkunft, § 3 Abs. 1) UND zugleich "
                "eine Belästigung nach § 3 Abs. 3 — und durch die Zuweisung der "
                "schlechteren Aufgaben auch eine Anweisung zur Diskriminierung.",
                optionen=_opts(
                    ("Kein AGG-Verstoß, der Schichtführer hat Weisungsbefugnis", False),
                    ("Unmittelbare Benachteiligung und Belästigung wegen ethnischer Herkunft", True),
                    ("Nur ein Verstoß gegen die Hausordnung", False),
                    ("Nur dann ein Verstoß, wenn der Kollege widerspricht", False),
                ),
            ),
            FrageDef(
                text="Wie hoch ist die Entschädigung nach § 15 Abs. 2 AGG bei einer diskriminierenden Bewerbungsabsage typischerweise?",
                erklaerung="Die Rechtsprechung orientiert sich bei diskriminierenden "
                "Bewerbungsabsagen häufig an rund einem bis drei Brutto-Monatsgehältern "
                "der ausgeschriebenen Stelle — der Betrag wird vom Arbeitsgericht "
                "festgesetzt.",
                optionen=_opts(
                    ("Pauschal 500 Euro", False),
                    ("Typischerweise rund ein bis drei Brutto-Monatsgehälter der Stelle", True),
                    ("Mindestens das Doppelte des Jahresgehalts", False),
                    ("Nur Erstattung der Bewerbungskosten", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zum Verhältnis 'Spaß' versus AGG-Verstoß ist juristisch korrekt?",
                erklaerung="Für die rechtliche Einordnung kommt es auf die Wirkung beim "
                "Betroffenen an, nicht auf die subjektive Absicht der sprechenden "
                "Person. 'War nur Spaß' ist keine Rechtfertigung.",
                optionen=_opts(
                    ("Wenn es als Spaß gemeint war, liegt nie eine Benachteiligung vor", False),
                    ("Entscheidend ist die Wirkung beim Betroffenen — 'War nur Spaß' rechtfertigt nichts", True),
                    ("Spaß ist erlaubt, solange alle im Raum lachen", False),
                    ("Nur schriftliche Äußerungen können Belästigung sein", False),
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
                        "## Worum geht's?\n\n"
                        "Du beobachtest, wie ein Einkäufer regelmäßig Geschenke von einem "
                        "Lieferanten annimmt und der parallel teurer einkauft als der Markt. "
                        "Oder dir fällt auf, dass an einer alten Presse eine "
                        "Sicherheitslichtschranke seit Monaten überbrückt ist und der "
                        "Schichtleiter das verschweigt. Solche Konstellationen — Schmiergeld, "
                        "Steuerverkürzung, vertuschte Sicherheitsmängel — kennt fast jeder "
                        "Industriebetrieb 'vom Hörensagen'. Bis 2023 hat sich kaum jemand "
                        "getraut, etwas zu sagen, weil Kündigung oder Mobbing die Regel waren. "
                        "Das **Hinweisgeberschutzgesetz** (HinSchG) hat das geändert: Wer "
                        "Missstände meldet, ist seit Juli 2023 gesetzlich geschützt.\n\n"
                        "## Rechtsgrundlage\n\n"
                        "- **HinSchG** — Gesetz für einen besseren Schutz hinweisgebender Personen, in Kraft seit 02.07.2023\n"
                        "- **EU-Whistleblower-Richtlinie 2019/1937** — europäische Grundlage, in deutsches Recht umgesetzt\n"
                        "- **§ 12 HinSchG** — Pflicht zur internen Meldestelle ab 50 Beschäftigten\n"
                        "- **§ 2 HinSchG** — sachlicher Anwendungsbereich (was gemeldet werden darf)\n\n"
                        "## Was musst du wissen\n\n"
                        "Das HinSchG schützt Personen, die im beruflichen Kontext Verstöße "
                        "melden. Geschützt ist nicht nur die Stammbelegschaft, sondern auch "
                        "Auszubildende, Praktikanten, Leiharbeiter, Bewerber und ehemalige "
                        "Beschäftigte (§ 1 HinSchG).\n\n"
                        "Der sachliche Anwendungsbereich nach § 2 HinSchG ist bewusst breit. "
                        "Meldungen können sich beziehen auf:\n\n"
                        "| Bereich | Typische Beispiele |\n"
                        "|---|---|\n"
                        "| Strafbewehrte Verstöße | Bestechung, Untreue, Betrug, Umweltstraftaten |\n"
                        "| Bußgeldbewehrte Verstöße | Verstöße gegen Arbeitsschutz, Beschäftigtenrechte |\n"
                        "| Geldwäsche | Verstöße gegen das Geldwäschegesetz (GwG) |\n"
                        "| Steuerrecht | Steuerverkürzung bei Kapital- und Personengesellschaften |\n"
                        "| Produktsicherheit | Mängel an Maschinen, CE-Verstöße, Rückrufpflichten |\n"
                        "| Datenschutz | DSGVO-Verstöße, unbefugte Datenweitergabe |\n"
                        "| Vergaberecht | Manipulation bei öffentlichen Ausschreibungen |\n"
                        "| Umwelt- und Strahlenschutz | illegale Entsorgung, Grenzwert-Überschreitungen |\n\n"
                        "Nicht geschützt sind reine Beschwerden über das Betriebsklima, "
                        "persönliche Konflikte oder private Verfehlungen ohne Bezug zum "
                        "Unternehmen. Wer wissentlich falsche Informationen meldet, verliert "
                        "den Schutz und kann selbst belangt werden (§ 38 HinSchG).\n\n"
                        "Das Gesetz gibt dir ein **Wahlrecht** zwischen interner Meldestelle "
                        "(im Unternehmen) und externer Meldestelle (bei einer Behörde). Du "
                        "darfst frei wählen — die Praxis empfiehlt, zuerst intern zu melden, "
                        "wenn du dem internen Verfahren vertraust, weil das oft schneller zu "
                        "einer Lösung führt (§ 7 Abs. 1 HinSchG).\n\n"
                        "## Was musst du tun\n\n"
                        "Bevor du eine Meldung absetzt:\n\n"
                        "1. Schreibe stichpunktartig auf, was du beobachtet hast: Wer, was, wann, wo, wie oft\n"
                        "2. Sichere greifbare Belege (E-Mails, Fotos, Notizen), aber kopiere keine fremden Zugriffsrechte\n"
                        "3. Entscheide, ob du intern (Vorgesetzten, Meldestelle) oder extern (Behörde) melden willst\n"
                        "4. Wenn du unsicher bist: das HinSchG schützt dich, sobald du *begründeten Anlass zu der Annahme* hast, dass ein Verstoß vorliegt (§ 33 Abs. 1 Nr. 2) — du musst es nicht beweisen\n\n"
                        "## Praxisbeispiel\n\n"
                        "In einem Maschinenbau-Zulieferer (180 Beschäftigte) fällt einer "
                        "Sachbearbeiterin in der Buchhaltung auf, dass für einen Lieferanten "
                        "über Monate Rechnungen mit ungewöhnlich runden Beträgen ohne klare "
                        "Leistungsbeschreibung gezahlt werden. Der zuständige Einkäufer fährt "
                        "neuerdings einen sehr teuren Privatwagen. Sie hat *begründeten Anlass "
                        "zur Annahme*, dass hier Schmiergelder im Spiel sein könnten — Bestechung "
                        "ist eine Straftat nach § 299 StGB und fällt damit klar unter § 2 HinSchG. "
                        "Sie sammelt die Auffälligkeiten in einer Notiz und nutzt das interne "
                        "Hinweisgeber-Portal des Unternehmens. Ab dem Moment der Meldung steht "
                        "sie unter dem Schutz des HinSchG — ihr darf wegen der Meldung nicht "
                        "gekündigt werden, sie darf nicht versetzt werden, und falls sie es doch "
                        "wird, greift die Beweislastumkehr aus § 36 HinSchG.\n\n"
                        "## Quelle\n\n"
                        "Inhalte gestützt auf HinSchG vom 31.05.2023 (BGBl. I Nr. 140) §§ 1-3, "
                        "7, 12, 33, 38 sowie EU-Richtlinie 2019/1937 (Whistleblower-Richtlinie). "
                        "Anwendungsbereich nach Stand 2025 (BfJ-Leitfaden zur externen Meldestelle)."
                    ),
                ),
                ModulDef(
                    titel="Meldekanal & Schutzrechte",
                    inhalt_md=(
                        "## Worum geht's?\n\n"
                        "Eine Meldung absetzen ist das eine — sich darauf verlassen können, dass "
                        "danach nichts Schlimmes passiert, ist das andere. Du lernst, welche "
                        "Meldekanäle es gibt, welche Fristen gelten, was dich vor Repressalien "
                        "schützt und warum die **Beweislastumkehr** aus § 36 HinSchG ein scharfes "
                        "Schwert ist. Den internen Meldekanal findest du unter *hinweise.app.vaeren.de*.\n\n"
                        "## Rechtsgrundlage\n\n"
                        "- **§ 7 HinSchG** — Wahlrecht zwischen interner und externer Meldestelle\n"
                        "- **§ 8 HinSchG** — Vertraulichkeitsgebot (Identität bleibt geheim)\n"
                        "- **§ 16 HinSchG** — Verfahren: Eingangsbestätigung 7 Tage, Rückmeldung 3 Monate\n"
                        "- **§ 17 HinSchG** — anonyme Meldungen *sollen* bearbeitet werden\n"
                        "- **§ 33 HinSchG** — sachlicher Schutzbereich (Repressalienverbot)\n"
                        "- **§ 36 HinSchG** — Beweislastumkehr bei Benachteiligung\n"
                        "- **§ 37 HinSchG** — Schadensersatz bei Repressalien\n"
                        "- **§ 40 HinSchG** — Bußgeld bis 50.000 € bei Behinderung oder Repressalien\n\n"
                        "## Was musst du wissen\n\n"
                        "Du hast drei Wege, eine Meldung abzusetzen:\n\n"
                        "- **Interne Meldestelle** des Arbeitgebers (z.B. das Vaeren-Portal, Compliance-Beauftragte, externe Ombudsperson)\n"
                        "- **Externe Meldestelle** des Bundes beim **Bundesamt für Justiz** (BfJ) für allgemeine Verstöße\n"
                        "- **BaFin** als externe Meldestelle für Finanz- und Wertpapierthemen, **Bundeskartellamt** für Wettbewerbsverstöße\n\n"
                        "Das HinSchG garantiert dir feste Fristen, an die sich jede Meldestelle "
                        "halten muss:\n\n"
                        "| Schritt | Frist | Quelle |\n"
                        "|---|---|---|\n"
                        "| Eingangsbestätigung an dich | spätestens 7 Tage | § 17 Abs. 1 Nr. 1 |\n"
                        "| Inhaltliche Rückmeldung (was wurde gemacht) | spätestens 3 Monate | § 17 Abs. 2 |\n"
                        "| Verlängerung in komplexen Fällen | bis 6 Monate, mit Begründung | § 17 Abs. 2 |\n\n"
                        "Die **Vertraulichkeit** deiner Identität ist gesetzlich geschützt "
                        "(§ 8 HinSchG). Nur Personen, die für die Bearbeitung zwingend "
                        "zuständig sind, dürfen wissen, wer gemeldet hat. Eine Weitergabe an "
                        "Vorgesetzte oder Kollegen ist ohne deine Einwilligung verboten und "
                        "mit Bußgeld bewehrt.\n\n"
                        "**Anonyme Meldungen** sind möglich. Die externe Meldestelle beim "
                        "Bundesamt für Justiz nimmt sie ausdrücklich entgegen. Interne "
                        "Meldestellen *müssen* keinen anonymen Kanal anbieten, *sollen* aber "
                        "anonyme Meldungen bearbeiten, sofern sie eingehen (§ 17 HinSchG). "
                        "Das Vaeren-Portal akzeptiert anonyme Meldungen — du kannst über "
                        "*hinweise.app.vaeren.de* ohne Angabe deines Namens schreiben und über "
                        "einen Zugangscode später die Rückmeldung abrufen.\n\n"
                        "Verboten sind **Repressalien** jeder Art (§ 36). Dazu gehören:\n\n"
                        "- Kündigung, Abmahnung oder Nichtverlängerung des Vertrags\n"
                        "- Versetzung, Umorganisation, Entzug von Aufgaben\n"
                        "- Mobbing, Ausgrenzung, Rufschädigung\n"
                        "- Beförderungsblockade, Gehaltskürzung, schlechte Beurteilung\n"
                        "- Disziplinarmaßnahmen, Schulungsentzug, Versagen von Empfehlungen\n\n"
                        "Die **Beweislastumkehr** ist der zentrale Schutz: Erleidet eine "
                        "hinweisgebende Person nach einer Meldung eine Benachteiligung, wird "
                        "*vermutet*, dass es eine Repressalie war. Der Arbeitgeber muss dann "
                        "beweisen, dass die Maßnahme sachlich gerechtfertigt war und nichts "
                        "mit der Meldung zu tun hatte (§ 36 Abs. 2). In der Praxis ist dieser "
                        "Beweis sehr schwer zu führen.\n\n"
                        "## Was musst du tun\n\n"
                        "Wenn du eine Meldung abgeben willst:\n\n"
                        "1. Öffne *hinweise.app.vaeren.de* (interner Kanal) oder die Website des BfJ (externer Kanal)\n"
                        "2. Entscheide, ob du mit Namen oder anonym meldest — beides ist zulässig\n"
                        "3. Beschreibe den Sachverhalt sachlich: was, wer, wann, wo, wie häufig\n"
                        "4. Sichere den Zugangscode (bei anonymer Meldung) für den späteren Rückmelde-Abruf\n"
                        "5. Erwarte innerhalb von 7 Tagen die Eingangsbestätigung\n"
                        "6. Wenn du nach der Meldung Nachteile erlebst: dokumentiere sie schriftlich und melde sie sofort der Meldestelle oder einem Anwalt — § 36 schützt dich\n\n"
                        "## Praxisbeispiel\n\n"
                        "Ein Industriemechaniker meldet anonym über das Vaeren-Portal, dass an "
                        "einer Spritzgussmaschine eine zweihändige Schutzschaltung mit einem "
                        "Magnetstreifen überbrückt ist, damit der Bediener schneller arbeiten "
                        "kann — auf Anweisung des Schichtleiters. Drei Wochen später erhält "
                        "er eine Versetzung in eine andere Halle mit deutlich schlechteren "
                        "Arbeitszeiten. Die Geschäftsführung begründet das mit *betrieblichen "
                        "Erfordernissen*. Da der Schichtleiter inzwischen erraten hat, wer der "
                        "Hinweisgeber war, und intern darüber spricht, greift die "
                        "Beweislastumkehr aus § 36 Abs. 2: Vor dem Arbeitsgericht muss nun das "
                        "Unternehmen beweisen, dass die Versetzung nichts mit der Meldung zu "
                        "tun hatte. Da der zeitliche Zusammenhang offensichtlich ist und keine "
                        "schriftliche Begründung von vor der Meldung existiert, scheitert "
                        "dieser Beweis. Der Mechaniker erhält Rückversetzung plus Schadensersatz "
                        "nach § 37 HinSchG; das Unternehmen zahlt zusätzlich ein Bußgeld nach "
                        "§ 40 HinSchG wegen Repressalie.\n\n"
                        "## Quelle\n\n"
                        "Inhalte gestützt auf HinSchG §§ 7, 8, 16, 17, 33, 36, 37, 40 "
                        "(Stand 2025) sowie Hinweise des Bundesamtes für Justiz zur externen "
                        "Meldestelle und der BaFin-Hinweisgeberstelle für Finanzthemen."
                    ),
                ),
            ),
            fragen=(
                FrageDef(
                    text="Ab welcher Beschäftigtenzahl ist ein Unternehmen verpflichtet, eine interne Meldestelle einzurichten?",
                    erklaerung="Nach § 12 HinSchG müssen Unternehmen ab 50 Beschäftigten eine interne "
                    "Meldestelle betreiben. Für Betriebe ab 250 Beschäftigten galt die Pflicht seit Juli 2023.",
                    optionen=_opts(
                        ("Ab 10 Beschäftigten", False),
                        ("Ab 50 Beschäftigten", True),
                        ("Ab 250 Beschäftigten", False),
                        ("Ab 500 Beschäftigten", False),
                    ),
                ),
                FrageDef(
                    text="Welches Recht gibt § 7 HinSchG hinweisgebenden Personen?",
                    erklaerung="§ 7 Abs. 1 HinSchG räumt ein freies Wahlrecht zwischen interner und externer "
                    "Meldestelle ein. Niemand ist verpflichtet, zuerst intern zu melden.",
                    optionen=_opts(
                        ("Pflicht, immer zuerst intern zu melden", False),
                        ("Wahlrecht zwischen interner und externer Meldestelle", True),
                        ("Pflicht, immer extern beim BfJ zu melden", False),
                        ("Recht, die Meldung erst nach Anwaltskonsultation abzugeben", False),
                    ),
                ),
                FrageDef(
                    text="Welche Frist gilt für die Eingangsbestätigung einer Meldung an die hinweisgebende Person?",
                    erklaerung="§ 17 Abs. 1 Nr. 1 HinSchG schreibt vor: spätestens 7 Tage nach Eingang muss "
                    "die Meldestelle den Eingang bestätigen.",
                    optionen=_opts(
                        ("3 Tage", False),
                        ("7 Tage", True),
                        ("14 Tage", False),
                        ("3 Monate", False),
                    ),
                ),
                FrageDef(
                    text="Innerhalb welcher Frist muss die Meldestelle inhaltlich Rückmeldung über die ergriffenen Folgemaßnahmen geben?",
                    erklaerung="§ 17 Abs. 2 HinSchG schreibt 3 Monate ab Eingangsbestätigung vor. In "
                    "komplexen Fällen mit Begründung bis zu 6 Monate.",
                    optionen=_opts(
                        ("7 Tage", False),
                        ("1 Monat", False),
                        ("3 Monate", True),
                        ("12 Monate", False),
                    ),
                ),
                FrageDef(
                    text="Welche externe Meldestelle ist beim Bund grundsätzlich zuständig?",
                    erklaerung="Die externe Meldestelle des Bundes ist beim Bundesamt für Justiz (BfJ) "
                    "eingerichtet. Für Finanzthemen ist zusätzlich die BaFin zuständig.",
                    optionen=_opts(
                        ("Die Bundesagentur für Arbeit", False),
                        ("Das Bundesamt für Justiz (BfJ)", True),
                        ("Die Staatsanwaltschaft des jeweiligen Landes", False),
                        ("Die zuständige IHK", False),
                    ),
                ),
                FrageDef(
                    text="Wie hoch kann das Bußgeld nach § 40 HinSchG bei Repressalien oder Behinderung von Meldungen werden?",
                    erklaerung="§ 40 HinSchG sieht gestaffelte Bußgelder bis zu 50.000 € vor, je nach "
                    "Schwere des Verstoßes (z.B. Repressalie, Verletzung der Vertraulichkeit, Behinderung).",
                    optionen=_opts(
                        ("Bis 5.000 €", False),
                        ("Bis 10.000 €", False),
                        ("Bis 50.000 €", True),
                        ("Bis 500.000 €", False),
                    ),
                ),
                FrageDef(
                    text="Welcher der folgenden Sachverhalte fällt klar NICHT unter den Anwendungsbereich des HinSchG?",
                    erklaerung="Persönliche Konflikte ohne Bezug zu einem rechtlichen Verstoß sind keine "
                    "HinSchG-Meldung. Strafbewehrte Taten, Geldwäsche und Arbeitsschutzverstöße sind erfasst.",
                    optionen=_opts(
                        ("Schmiergeldzahlungen an einen Einkäufer", False),
                        ("Persönlicher Konflikt mit einem Kollegen ohne Rechtsverstoß", True),
                        ("Verstoß gegen das Geldwäschegesetz", False),
                        ("Vertuschter Sicherheitsmangel an einer Maschine", False),
                    ),
                ),
                FrageDef(
                    text="Du beobachtest, wie ein Vorgesetzter eine defekte Schutzeinrichtung an einer Presse überbrücken lässt. Was tust du?",
                    erklaerung="Sicherheitsmängel an Maschinen sind ein klassischer HinSchG-Fall (Schutz "
                    "von Leben und Gesundheit, § 2 Abs. 1 Nr. 2). Direkt-Anweisung an Vorgesetzten "
                    "ignorieren wäre falsch, anonyme Meldung über das Portal ist legitim.",
                    optionen=_opts(
                        ("Schweigen, weil du dann Ärger bekommst", False),
                        ("Eine Meldung über das Vaeren-Hinweisgeber-Portal absetzen, ggf. anonym", True),
                        ("Direkt zur Boulevardpresse gehen", False),
                        ("Erst zwei Jahre warten und beobachten, bevor du etwas sagst", False),
                    ),
                ),
                FrageDef(
                    text="Nach deiner Meldung wirst du wenige Wochen später ohne klare Begründung in eine andere Schicht versetzt. Was greift jetzt?",
                    erklaerung="§ 36 Abs. 2 HinSchG kehrt die Beweislast um. Der Arbeitgeber muss beweisen, "
                    "dass die Versetzung nichts mit der Meldung zu tun hatte — nicht du, dass sie eine "
                    "Repressalie war.",
                    optionen=_opts(
                        ("Du musst beweisen, dass es eine Repressalie war", False),
                        ("Die Beweislastumkehr nach § 36 HinSchG — der Arbeitgeber muss die Rechtfertigung beweisen", True),
                        ("Nichts, weil eine Versetzung keine Repressalie ist", False),
                        ("Du verlierst den Schutz, weil drei Wochen vergangen sind", False),
                    ),
                ),
                FrageDef(
                    text="Du hast nur einen Verdacht, aber keine eindeutigen Beweise. Bist du trotzdem geschützt, wenn du meldest?",
                    erklaerung="§ 33 Abs. 1 Nr. 2 HinSchG schützt, wenn *begründeter Anlass zur Annahme* "
                    "besteht — du musst den Verstoß nicht beweisen, nur plausibel begründen können.",
                    optionen=_opts(
                        ("Nein, ohne harte Beweise verlierst du jeden Schutz", False),
                        ("Ja, ein begründeter Anlass zur Annahme reicht aus", True),
                        ("Nur wenn du eine schriftliche Vollmacht eines Anwalts hast", False),
                        ("Nur wenn die Staatsanwaltschaft den Sachverhalt bestätigt", False),
                    ),
                ),
                FrageDef(
                    text="Welche der folgenden Personen sind NICHT durch das HinSchG geschützt?",
                    erklaerung="Geschützt sind Beschäftigte aller Art, einschließlich Bewerber, Praktikanten, "
                    "Leiharbeiter und Ehemalige (§ 1 HinSchG). Anonyme Fremde ohne beruflichen Bezug sind "
                    "nicht der Adressatenkreis des HinSchG.",
                    optionen=_opts(
                        ("Auszubildende im Betrieb", False),
                        ("Bewerber im laufenden Bewerbungsverfahren", False),
                        ("Ehemalige Mitarbeiter nach Vertragsende", False),
                        ("Anonyme Privatpersonen ohne beruflichen Bezug zum Unternehmen", True),
                    ),
                ),
                FrageDef(
                    text="Sind anonyme Meldungen nach HinSchG zulässig?",
                    erklaerung="§ 17 HinSchG: anonyme Meldungen *sollen* bearbeitet werden. Das Bundesamt "
                    "für Justiz akzeptiert sie ausdrücklich, interne Meldestellen müssen keinen anonymen "
                    "Kanal pflichtweise anbieten, sollen aber eingehende anonyme Meldungen bearbeiten.",
                    optionen=_opts(
                        ("Nein, anonyme Meldungen sind verboten", False),
                        ("Ja, sie sind zulässig und sollen bearbeitet werden", True),
                        ("Nur bei der Staatsanwaltschaft, intern niemals", False),
                        ("Nur wenn der Arbeitgeber sie ausdrücklich erlaubt", False),
                    ),
                ),
                FrageDef(
                    text="Welcher Schutz folgt aus § 8 HinSchG?",
                    erklaerung="§ 8 HinSchG ist das Vertraulichkeitsgebot: Die Identität der "
                    "hinweisgebenden Person darf nur den unmittelbar mit der Bearbeitung betrauten "
                    "Personen bekannt werden.",
                    optionen=_opts(
                        ("Pflicht zur Veröffentlichung der Identität", False),
                        ("Vertraulichkeit der Identität der hinweisgebenden Person", True),
                        ("Pflicht zur Information aller Vorgesetzten", False),
                        ("Recht auf eine Belohnung in Höhe von 10 Prozent des Bußgelds", False),
                    ),
                ),
                FrageDef(
                    text="Welche Maßnahme ist KEINE verbotene Repressalie nach § 36 HinSchG?",
                    erklaerung="Eine sachlich begründete Disziplinarmaßnahme wegen unabhängig dokumentierter "
                    "Pflichtverletzung ist erlaubt. Kündigung, Versetzung und Beurteilungsverschlechterung "
                    "nach einer Meldung gelten dagegen als Repressalie.",
                    optionen=_opts(
                        ("Kündigung nach einer Meldung", False),
                        ("Versetzung ohne sachlichen Grund nach einer Meldung", False),
                        ("Verschlechterung der Jahresbeurteilung wegen der Meldung", False),
                        ("Eine vor der Meldung schriftlich begründete Abmahnung wegen Zuspätkommens", True),
                    ),
                ),
                FrageDef(
                    text="Bei welcher Meldung ist die BaFin als externe Meldestelle zuständig?",
                    erklaerung="Die BaFin ist die externe Meldestelle für Verstöße im Finanz- und "
                    "Wertpapierbereich (Geldwäsche im Bankensektor, Marktmanipulation, Insiderhandel etc.).",
                    optionen=_opts(
                        ("Verstoß gegen Arbeitsschutzvorschriften", False),
                        ("Marktmanipulation und Insiderhandel im Finanzbereich", True),
                        ("Verstoß gegen das Mindestlohngesetz", False),
                        ("Mobbing am Arbeitsplatz", False),
                    ),
                ),
                FrageDef(
                    text="Du meldest wissentlich falsche Informationen, um einem Kollegen zu schaden. Was passiert?",
                    erklaerung="§ 38 HinSchG: Wer wissentlich falsche Informationen meldet, verliert "
                    "den Schutz des HinSchG und kann selbst schadensersatzpflichtig und strafrechtlich "
                    "belangt werden (z.B. üble Nachrede, falsche Verdächtigung).",
                    optionen=_opts(
                        ("Du bist trotzdem geschützt, weil du etwas gemeldet hast", False),
                        ("Du verlierst den Schutz und kannst selbst haftbar gemacht werden", True),
                        ("Nichts, anonyme Meldungen werden nicht verfolgt", False),
                        ("Du erhältst eine reduzierte Schutzwirkung von 50 Prozent", False),
                    ),
                ),
                FrageDef(
                    text="Was ist die zentrale Funktion der Beweislastumkehr in § 36 HinSchG?",
                    erklaerung="Sie verschiebt die Beweislast vom Arbeitnehmer zum Arbeitgeber. Sonst "
                    "müssten Beschäftigte beweisen, dass eine Maßnahme als Reaktion auf die Meldung "
                    "erfolgte — das ist praktisch unmöglich, weil sie keinen Zugang zu den internen "
                    "Entscheidungsprozessen haben.",
                    optionen=_opts(
                        ("Sie verlängert die Verjährungsfrist", False),
                        ("Sie verschiebt die Beweislast vom Arbeitnehmer zum Arbeitgeber", True),
                        ("Sie erhöht das Bußgeld automatisch", False),
                        ("Sie verlangt von der Meldestelle eine zweite Stellungnahme", False),
                    ),
                ),
                FrageDef(
                    text="Ein Mitarbeitender erlebt nach einer Meldung Mobbing durch Kollegen. Greift das HinSchG?",
                    erklaerung="Mobbing gehört zu den verbotenen Repressalien nach § 36 HinSchG. Der "
                    "Arbeitgeber ist verpflichtet, Schutzmaßnahmen zu ergreifen und kann auf Schadensersatz "
                    "nach § 37 in Anspruch genommen werden.",
                    optionen=_opts(
                        ("Nein, Mobbing fällt nicht unter Repressalien", False),
                        ("Ja, Mobbing ist eine Repressalie und der Arbeitgeber muss schützen und ggf. Schadensersatz leisten", True),
                        ("Nur wenn es schriftlich nachweisbar ist", False),
                        ("Nur bei körperlichem Schaden", False),
                    ),
                ),
                FrageDef(
                    text="Welche Aussage zum Verhältnis interner und externer Meldestelle ist korrekt?",
                    erklaerung="§ 7 Abs. 1 HinSchG: freie Wahl zwischen intern und extern. Eine Pflicht zur "
                    "vorherigen internen Meldung gibt es ausdrücklich nicht — anders als ursprünglich "
                    "geplant.",
                    optionen=_opts(
                        ("Die interne Meldung ist Pflicht, bevor extern gemeldet werden darf", False),
                        ("Hinweisgebende Personen können frei zwischen intern und extern wählen", True),
                        ("Externe Meldungen sind nur bei Verstößen über 100.000 € Schaden zulässig", False),
                        ("Externe Meldungen verlieren immer den Schutz des HinSchG", False),
                    ),
                ),
                FrageDef(
                    text="Wo findest du im Unternehmen Vaeren-Umfeld den internen Hinweisgeber-Meldekanal?",
                    erklaerung="Das Vaeren-Hinweisgeber-Portal ist unter hinweise.app.vaeren.de erreichbar "
                    "und erfüllt die Anforderungen des HinSchG (Vertraulichkeit, 7-Tage-Bestätigung, "
                    "3-Monats-Rückmeldung, anonyme Meldung möglich).",
                    optionen=_opts(
                        ("Per Aushang am schwarzen Brett ohne weitere Erreichbarkeit", False),
                        ("Unter hinweise.app.vaeren.de (auch anonym nutzbar)", True),
                        ("Ausschließlich über die persönliche E-Mail des Geschäftsführers", False),
                        ("Nur telefonisch über die Zentrale", False),
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
                    "## Worum geht's?\n\n"
                    "Wer einen Gabelstapler steuert, führt ein Arbeitsmittel mit bis zu fünf "
                    "Tonnen Eigengewicht, hydraulischem Hubmast und einer Geschwindigkeit von "
                    "bis zu 16 km/h. Ohne formale Berechtigung darfst du dich nicht hinter das "
                    "Lenkrad setzen, egal wie kurz die Fahrt ist. Du lernst, welche drei "
                    "Voraussetzungen gleichzeitig erfüllt sein müssen, bevor du fahren darfst, "
                    "und welche Konsequenzen ein Verstoß für dich und den Arbeitgeber hat.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 7 DGUV Vorschrift 68** — schriftlicher Fahrauftrag nur an befähigte Personen\n"
                    "- **DGUV Grundsatz 308-001** — Qualifizierung und Beauftragung der Fahrer:innen (Stand 2022)\n"
                    "- **DGUV Information 208-031** — Ausbildung Fahrer Flurförderzeuge\n"
                    "- **§ 12 ArbSchG** — jährliche Unterweisung am Arbeitsplatz\n"
                    "- **§ 29 StVO** — Führerschein der Klasse L oder B nur bei Fahrten auf öffentlichen Wegen\n\n"
                    "## Was musst du wissen\n\n"
                    "Die Berechtigung zum Steuern eines Flurförderzeugs steht erst, wenn drei "
                    "Bausteine *gleichzeitig* vorliegen — Fachjargon: die *3-Stufen-"
                    "Voraussetzung*. Fehlt einer, ist die Fahrt rechtswidrig:\n\n"
                    "| Stufe | Inhalt | Wer? | Nachweis |\n"
                    "|---|---|---|---|\n"
                    "| 1. Befähigung | Allgemeine Stapler-Ausbildung nach DGUV G 308-001, mind. 20 Unterrichtseinheiten, Theorie + Praxis + Prüfung | Externer Ausbilder oder qualifizierter interner | Staplerschein (Fahrausweis) |\n"
                    "| 2. Beauftragung | Schriftlicher Fahrauftrag des Arbeitgebers, gerätespezifisch | Geschäftsführung oder Fachvorgesetzte | Unterschriebener Auftrag in der Personalakte |\n"
                    "| 3. Unterweisung | Jährliche betriebliche Unterweisung zu Gerät, Halle, Verkehrsregeln | Sicherheitsfachkraft oder Fahrtrainer | Anwesenheits-Liste mit Datum und Unterschrift |\n\n"
                    "Der **Staplerschein** ist keine staatliche Urkunde wie der Pkw-Führerschein, "
                    "sondern eine berufsgenossenschaftliche Bescheinigung. Er gilt unbefristet, "
                    "verlangt aber regelmäßige Fahrpraxis. Wer länger als ein Jahr nicht "
                    "gefahren ist, darf nicht ohne erneute praktische Bewertung wieder fahren "
                    "(DGUV V 68 § 7 Abs. 4).\n\n"
                    "Mindestalter ist 18 Jahre. Jugendliche ab 16 dürfen nur unter Aufsicht "
                    "und im Rahmen einer Ausbildung fahren. Voraussetzung sind außerdem "
                    "körperliche und geistige Eignung — bei Hör-, Seh- oder Reaktionsproblemen "
                    "ist eine arbeitsmedizinische Vorsorge nach G 25 *Fahr-, Steuer- und "
                    "Überwachungstätigkeiten* sinnvoll, in vielen Betrieben sogar Pflicht.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jeder Schicht prüfst du:\n\n"
                    "1. Habe ich einen gültigen Staplerschein dabei oder im Betrieb hinterlegt?\n"
                    "2. Habe ich für *genau diesen* Stapler-Typ einen schriftlichen Fahrauftrag?\n"
                    "3. Habe ich in den letzten zwölf Monaten die betriebliche Unterweisung erhalten?\n"
                    "4. Bin ich fahrtauglich — ausgeschlafen, nüchtern, ohne dämpfende Medikamente?\n"
                    "5. Sehe ich klar und höre ich Warnsignale?\n\n"
                    "Wenn auch nur ein Punkt offen ist, fährst du nicht. Du meldest dich bei "
                    "der Schichtleitung und klärst die Lücke vor Schichtbeginn.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Lagerist aus dem Versand soll am Freitag um 17 Uhr aushelfen, weil "
                    "der Stamm-Staplerfahrer krank ist. Er hat vor drei Jahren in einer "
                    "anderen Firma einen Staplerschein gemacht, aber im aktuellen Betrieb "
                    "weder Fahrauftrag noch Unterweisung. Die Schichtleitung drängt ihn 'nur "
                    "für die letzten zwei Paletten'. Er sagt nein, verweist auf § 7 DGUV V 68 "
                    "und schlägt vor, die Paletten am Montag früh fertigzumachen. Genau "
                    "richtig — wäre er gefahren und hätte einen Unfall verursacht, drohten "
                    "ihm persönlich Schmerzensgeld-Forderungen, dem Geschäftsführer ein "
                    "Bußgeld nach § 21 ArbSchG und der Berufsgenossenschaft ein Regress.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Vorschrift 68 *Flurförderzeuge* (Stand 2013), "
                    "DGUV Grundsatz 308-001 *Qualifizierung und Beauftragung der Fahrerinnen "
                    "und Fahrer von Flurförderzeugen* (Ausgabe Dezember 2022) und "
                    "DGUV Information 208-031 *Einsatz von Arbeitsbühnen an Flurförderzeugen "
                    "mit Hubmast*."
                ),
            ),
            ModulDef(
                titel="Sicherer Betrieb",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Die meisten Stapler-Unfälle passieren nicht beim Heben, sondern beim "
                    "Fahren: Quetschen von Fußgängern an Hallenecken, Anfahren von Regalstützen, "
                    "Kollisionen mit anderen Staplern an Kreuzungen. Du lernst, wie du den "
                    "Stapler vor Schichtbeginn auf Verkehrssicherheit prüfst, wie du im "
                    "innerbetrieblichen Verkehr fährst und warum Anschnallen und Geschwindigkeit "
                    "keine Komfort-Themen sind, sondern Lebensretter.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 7 BetrSichV** — Prüfung von Arbeitsmitteln vor Verwendung\n"
                    "- **§ 11 DGUV Vorschrift 68** — wiederkehrende Prüfung mind. einmal jährlich (UVV-Prüfung)\n"
                    "- **DGUV Information 208-004** — *Gabelstapler* (Sicherer Betrieb, Kap. 6)\n"
                    "- **ASR A1.8** — Verkehrswege in Arbeitsstätten\n"
                    "- **§ 25 DGUV V 68** — Personenbeförderung grundsätzlich verboten\n\n"
                    "## Was musst du wissen\n\n"
                    "Bevor du losfährst, ist eine **Abfahrtkontrolle** Pflicht. Sie dauert "
                    "nicht länger als drei Minuten, deckt aber 80 Prozent der häufigen Mängel "
                    "ab:\n\n"
                    "- Reifen: Profil, Luftdruck, sichtbare Schäden\n"
                    "- Bremse, Lenkung, Hupe, Blinker, Rundumleuchte\n"
                    "- Hubmast, Hubgerüst, Hydraulik-Schläuche auf Leckage\n"
                    "- Gabelzinken auf Risse, Verbiegung, gleichmäßige Höhe\n"
                    "- Fahrerschutzdach und Lastschutzgitter unbeschädigt\n"
                    "- Sitz und **Rückhaltesystem** (Beckengurt oder Bügeltür) funktionsfähig\n\n"
                    "Mängel werden in das **Schichtbuch** (Mängelbuch) eingetragen und der "
                    "Schichtleitung gemeldet. Sicherheitsrelevante Mängel — defekte Bremse, "
                    "Hydraulik-Leck, rissige Gabel — bedeuten *sofortige Stilllegung*. Erst "
                    "nach Reparatur und Freigabe darf der Stapler wieder fahren.\n\n"
                    "Beim Fahren gelten strenge Regeln:\n\n"
                    "| Situation | Regel |\n"
                    "|---|---|\n"
                    "| Geschwindigkeit Halle | maximal 6 km/h (Schritttempo) im Personenbereich |\n"
                    "| Bauartbedingte Höchstgeschwindigkeit | meist 16 km/h, nie überschreiten |\n"
                    "| Last vor Sicht | rückwärts fahren oder Einweiser nutzen |\n"
                    "| Steigung mit Last | Last bergauf — Last zeigt nach oben |\n"
                    "| Kurven | nur mit gesenkter Last und reduziertem Tempo |\n"
                    "| Fußgänger | Vorrang, Hupen vor unübersichtlichen Ecken |\n\n"
                    "**Anschnallen** ist Pflicht, sobald der Stapler einen Beckengurt hat. "
                    "Bei einem Kipper schlägt der Fahrer ungesichert sonst zur Seite und wird "
                    "vom Fahrerschutzdach erschlagen — ein bekannter Unfallmechanismus mit "
                    "regelmäßig tödlichem Ausgang. Bügeltüren erfüllen denselben Zweck.\n\n"
                    "**Personenbeförderung** ist verboten. Niemand fährt auf der Gabel, auf "
                    "dem Trittbrett oder neben dem Fahrer mit. Einzige Ausnahme: ein "
                    "zugelassener Arbeitskorb nach DGUV Information 208-031, formschlüssig "
                    "angeschlagen, mit Geländer 1,10 m und Fußleiste. Auch dann darf der "
                    "Stapler bei besetztem Korb nicht verfahren werden — nur Feinpositionierung "
                    "bei bodenfrei angehobenem Korb mit max. 16 km/h Bauart-Geschwindigkeit.\n\n"
                    "## Was musst du tun\n\n"
                    "Bei jeder Schicht:\n\n"
                    "1. Abfahrtkontrolle nach Checkliste durchführen und in das Schichtbuch eintragen\n"
                    "2. Beckengurt anlegen oder Bügeltüren schließen, bevor du startest\n"
                    "3. Im Personenbereich Schritttempo (max. 6 km/h) und vor jeder Kreuzung hupen\n"
                    "4. Last immer abgesenkt transportieren, Gabel nur zum Aufnehmen/Absetzen heben\n"
                    "5. Niemals Personen befördern — Ausnahme nur mit zugelassenem Arbeitskorb\n"
                    "6. Beim Verlassen Gabel absenken, Feststellbremse anziehen, Schlüssel abziehen\n\n"
                    "Die jährliche **UVV-Prüfung** nach § 11 DGUV V 68 wird durch eine "
                    "befähigte Person (Sachkundige:r) durchgeführt und mit einer grünen "
                    "Prüfplakette am Stapler dokumentiert. Fehlt die Plakette oder ist sie "
                    "abgelaufen, darfst du das Gerät nicht in Betrieb nehmen.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Metallverarbeitung biegt ein Frontstapler-Fahrer mit Schritttempo "
                    "um eine Hallenecke. An der Ecke kreuzt ein Kollege aus dem Lagerbüro "
                    "ahnungslos den Weg. Weil der Fahrer vor der Ecke gehupt und Tempo "
                    "rausgenommen hat, kann er stehenbleiben, bevor er den Kollegen trifft — "
                    "Bremsweg 1,2 m bei 6 km/h, Last gesenkt, Beckengurt angelegt. Nach dem "
                    "Vorfall werden an allen Hallenecken Konvexspiegel und Bodenmarkierungen "
                    "*Stapler-Verkehr* angebracht und die Wege für Fußgänger durch gelbe "
                    "Bodenstreifen abgegrenzt — Standard nach ASR A1.8.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Vorschrift 68 *Flurförderzeuge* (Stand 2013), "
                    "DGUV Information 208-004 *Gabelstapler* (Ausgabe September 2012) und "
                    "ASR A1.8 *Verkehrswege* (Ausgabe 2018)."
                ),
            ),
            ModulDef(
                titel="Standsicherheit & Lastdiagramm",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Gabelstapler kippt nicht zufällig. Er kippt nach physikalischen "
                    "Gesetzen, sobald das Kippmoment der Last das Standmoment des Geräts "
                    "übersteigt. Der Hersteller dokumentiert die sichere Grenze im "
                    "*Lastdiagramm* (Traglastdiagramm). Du lernst, das Diagramm zu lesen, "
                    "warum Lastschwerpunkt und Hubhöhe die Tragfähigkeit massiv beeinflussen "
                    "und warum 'nur mal kurz' das häufigste letzte Wort vor einem "
                    "Kippunfall ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 BetrSichV** — Arbeitgeber stellt sicher, dass Tragfähigkeit nicht überschritten wird\n"
                    "- **DGUV Vorschrift 68 § 12** — Last muss sicher aufgenommen und transportiert sein\n"
                    "- **DGUV Information 208-004** Kap. 6.4 — Standsicherheit und Lastdiagramm\n"
                    "- **DIN EN ISO 3691-1** — Sicherheit von Flurförderzeugen mit Fahrersitz\n\n"
                    "## Was musst du wissen\n\n"
                    "Jeder Stapler hat ein **Lastdiagramm** am Fahrerschutzdach oder am "
                    "Armaturenbrett. Es zeigt die maximale Tragfähigkeit (kg) in Abhängigkeit "
                    "von zwei Variablen: dem **Lastschwerpunkt** (Abstand des Last-Schwerpunkts "
                    "vom Gabelrücken, in mm) und der **Hubhöhe** (in mm).\n\n"
                    "Der Standard-Lastschwerpunkt in Europa ist:\n\n"
                    "| Stapler-Klasse | Lastschwerpunkt | Typische Nenntragfähigkeit |\n"
                    "|---|---|---|\n"
                    "| Bis 1 t Nutzlast | 400 mm | Kleinstapler im Großhandel |\n"
                    "| 1 bis 5 t | 500 mm | Standard-Frontstapler im Mittelstand |\n"
                    "| Über 5 t | 600 mm | Schwerlast-Stapler in Schwer­industrie |\n\n"
                    "Verschiebt sich der Schwerpunkt der Last weiter nach vorn, sinkt die "
                    "Tragfähigkeit drastisch. Eine Palette mit 1.500 kg und 500 mm "
                    "Lastschwerpunkt kann ein Stapler mit 2.000 kg Nenntragfähigkeit problemlos "
                    "heben. Verteilst du dieselbe Last auf eine Sonderpalette mit 800 mm "
                    "Schwerpunkt-Abstand, reicht die Tragfähigkeit oft nicht mehr — der Stapler "
                    "*kippt vornüber*, weil das Kippmoment Last × Hebelarm das Standmoment "
                    "Eigengewicht × Radstand übersteigt.\n\n"
                    "Auch die **Hubhöhe** reduziert die Tragfähigkeit. Beim Anheben verschiebt "
                    "sich der Gesamtschwerpunkt nach oben, der Stapler wird kopflastiger und "
                    "kippanfälliger. Typische Reduktion bei Standard-Triplex-Mast: über vier "
                    "Meter Hubhöhe bis zu 30 Prozent weniger erlaubte Last.\n\n"
                    "Der zweite Kipp-Mechanismus ist **seitliches Kippen**. Es droht beim "
                    "Kurvenfahren mit gehobener Last, bei einseitiger Belastung der Gabel und "
                    "auf abschüssigem Gelände. Faustregel: Last immer mittig, beide Gabelzinken "
                    "auf gleicher Höhe, Kurven nur mit abgesenkter Last und unter 5 km/h.\n\n"
                    "Anbaugeräte (Klemmen, Verlängerungen, Schaufeln) verändern Eigengewicht "
                    "und Lastschwerpunkt. Für jedes Anbaugerät braucht der Stapler ein "
                    "*eigenes* Lastdiagramm. Ohne dieses Diagramm ist der Betrieb verboten — "
                    "auch wenn das Anbaugerät 'nur für einen Job' angebracht wird.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor jeder Last:\n\n"
                    "1. Gewicht der Last prüfen — Lieferschein, Etikett oder Waage\n"
                    "2. Lastschwerpunkt einschätzen — Standard 500 mm? Wenn nicht, langes Lastdiagramm prüfen\n"
                    "3. Hubhöhe einkalkulieren — soll die Last auf 5 m Regalebene?\n"
                    "4. Lastdiagramm am Stapler ablesen: passt Gewicht zu Schwerpunkt + Hubhöhe?\n"
                    "5. Im Zweifel: kleinere Teilladung oder größerer Stapler — niemals 'nur mal kurz' überladen\n"
                    "6. Beim Anbaugerät: passendes Lastdiagramm vorhanden? Sonst nicht fahren\n\n"
                    "Wer das Lastdiagramm ignoriert, riskiert nicht nur den eigenen Tod, "
                    "sondern haftet bei grobem Verstoß auch zivilrechtlich. Die Berufs"
                    "genossenschaft kann den Versicherungsschutz nach § 110 SGB VII teilweise "
                    "zurückfordern.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Zulieferbetrieb fertigt eine Sonderpalette mit Motorgehäusen, "
                    "Gesamtgewicht 1.800 kg, Lastschwerpunkt 750 mm statt der üblichen 500 mm. "
                    "Der Stapler hat eine Nenntragfähigkeit von 2.500 kg bei 500 mm. Der Fahrer "
                    "rechnet kurz: bei 750 mm Schwerpunkt reduziert das Lastdiagramm auf "
                    "1.650 kg. Die Palette wäre überladen. Er teilt die Motorgehäuse auf zwei "
                    "Standard-Paletten auf — 15 Minuten mehr Aufwand, aber keine "
                    "Kipp-Gefahr. Hätte er gehoben, wäre der Stapler beim Anheben über drei "
                    "Meter rückwärts auf den Fahrer gekippt — ein typischer tödlicher "
                    "Mechanismus, den Unfallchronik und DGUV-Statistik jedes Jahr mehrfach "
                    "verzeichnen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Information 208-004 *Gabelstapler* "
                    "(Ausgabe September 2012), DIN EN ISO 3691-1 *Sicherheit von "
                    "Flurförderzeugen* und § 110 SGB VII *Haftung bei grober Fahrlässigkeit*."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche drei Voraussetzungen müssen gleichzeitig vorliegen, bevor du einen Gabelstapler steuern darfst?",
                erklaerung="Die 3-Stufen-Voraussetzung nach DGUV V 68 § 7 + DGUV G 308-001 verlangt "
                "Befähigung (Staplerschein), schriftliche Beauftragung und jährliche Unterweisung.",
                optionen=_opts(
                    ("Pkw-Führerschein Klasse B, Sicherheitsschuhe, Warnweste", False),
                    ("Staplerschein, schriftliche Beauftragung, jährliche Unterweisung", True),
                    ("Mindestalter 21, ärztliches Attest, Probefahrt", False),
                    ("Praktikum, Genehmigung des Betriebsrats, eigene PSA", False),
                ),
            ),
            FrageDef(
                text="Wie heißt das maßgebliche DGUV-Regelwerk für die Qualifizierung von Stapler-Fahrer:innen?",
                erklaerung="Der DGUV Grundsatz 308-001 (Ausgabe Dezember 2022) regelt Inhalt, Umfang "
                "und Prüfung der Stapler-Ausbildung.",
                optionen=_opts(
                    ("DGUV Vorschrift 1", False),
                    ("DGUV Information 208-004", False),
                    ("DGUV Grundsatz 308-001", True),
                    ("BGI 545", False),
                ),
            ),
            FrageDef(
                text="Ab welchem Alter darfst du regulär einen Gabelstapler im Betrieb steuern?",
                erklaerung="Mindestalter ist 18 Jahre. Jugendliche ab 16 dürfen nur in Ausbildung "
                "und unter Aufsicht fahren.",
                optionen=_opts(
                    ("16 Jahre", False),
                    ("17 Jahre", False),
                    ("18 Jahre", True),
                    ("21 Jahre", False),
                ),
            ),
            FrageDef(
                text="Welche Höchstgeschwindigkeit gilt für Stapler im Personenbereich einer Halle nach üblicher Betriebsanweisung?",
                erklaerung="Im Personenbereich gilt Schritttempo, das mit maximal 6 km/h definiert ist. "
                "Die bauartbedingte Höchstgeschwindigkeit liegt bei den meisten Staplern bei 16 km/h.",
                optionen=_opts(
                    ("16 km/h", False),
                    ("6 km/h (Schritttempo)", True),
                    ("10 km/h", False),
                    ("3 km/h", False),
                ),
            ),
            FrageDef(
                text="Was ist der Standard-Lastschwerpunkt-Abstand für Frontstapler im Bereich 1 bis 5 Tonnen Nutzlast in Europa?",
                erklaerung="500 mm ist der europäische Referenz-Lastschwerpunkt für Standard-Frontstapler "
                "in dieser Klasse. Alle Lastdiagramme rechnen daran.",
                optionen=_opts(
                    ("400 mm", False),
                    ("500 mm", True),
                    ("600 mm", False),
                    ("800 mm", False),
                ),
            ),
            FrageDef(
                text="Wie oft muss ein Gabelstapler nach § 11 DGUV V 68 wiederkehrend geprüft werden (UVV-Prüfung)?",
                erklaerung="Mindestens einmal jährlich durch eine befähigte Person (Sachkundige:r), "
                "dokumentiert durch grüne Prüfplakette am Gerät.",
                optionen=_opts(
                    ("Alle zwei Jahre", False),
                    ("Mindestens einmal jährlich", True),
                    ("Alle fünf Jahre", False),
                    ("Nur bei sichtbaren Schäden", False),
                ),
            ),
            FrageDef(
                text="Welche Berufsgenossenschaftliche Information ist die zentrale Quelle für den sicheren Betrieb von Gabelstaplern?",
                erklaerung="DGUV Information 208-004 *Gabelstapler* (vormals BGI 545) ist das "
                "Praxis-Handbuch für Fahrer:innen.",
                optionen=_opts(
                    ("DGUV Information 208-004", True),
                    ("DGUV Information 205-001", False),
                    ("ASR A2.3", False),
                    ("TRGS 510", False),
                ),
            ),
            FrageDef(
                text="Du sollst ausnahmsweise auf der Gabel mitfahren, weil der Kollege oben in der vierten Regalebene Material kontrollieren will. Was tust du?",
                erklaerung="Personenbeförderung auf der Gabel ist nach § 25 DGUV V 68 strikt verboten. "
                "Erlaubt ist nur ein zugelassener Arbeitskorb nach DGUV Information 208-031.",
                optionen=_opts(
                    ("Ich fahre, aber nur ganz langsam und mit gespreizter Gabel", False),
                    ("Ich lehne ab und schlage einen zugelassenen Arbeitskorb oder Hubarbeitsbühne vor", True),
                    ("Ich fahre, wenn der Kollege sich an der Gabel festhält", False),
                    ("Ich fahre, weil die Schichtleitung es angewiesen hat", False),
                ),
            ),
            FrageDef(
                text="Beim Abfahrtcheck stellst du fest, dass die Bremse beim Bremstest deutlich nachzieht. Was machst du?",
                erklaerung="Sicherheitsrelevante Mängel bedeuten *sofortige Stilllegung*. Eintrag ins "
                "Mängelbuch und Meldung an die Schichtleitung — kein Fahren bis zur Reparatur.",
                optionen=_opts(
                    ("Ich fahre vorsichtig und melde es am Schichtende", False),
                    ("Ich stelle den Stapler still, trage den Mangel ein und melde an die Schichtleitung", True),
                    ("Ich vermeide Lastfahrten und transportiere nur leere Paletten", False),
                    ("Ich justiere die Bremse selbst nach", False),
                ),
            ),
            FrageDef(
                text="Du transportierst eine sperrige Last, die deine Sicht nach vorn vollständig verdeckt. Was tust du?",
                erklaerung="Wenn die Last die Sicht versperrt, fährst du rückwärts oder mit Einweiser. "
                "Vorwärtsfahren ohne Sicht ist ein klassischer Personenschaden-Mechanismus.",
                optionen=_opts(
                    ("Ich fahre vorwärts und hupe permanent", False),
                    ("Ich fahre rückwärts oder lasse mich von einem Einweiser leiten", True),
                    ("Ich hebe die Last höher, damit ich unten durchschauen kann", False),
                    ("Ich schicke einen Kollegen voraus, der die Bahn freiräumt", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine Palette mit Sonderlast (Schwerpunkt-Abstand 750 mm statt 500 mm) heben. Wie gehst du vor?",
                erklaerung="Bei abweichendem Lastschwerpunkt prüfst du das Lastdiagramm — die zulässige "
                "Tragfähigkeit sinkt drastisch. Im Zweifel die Last teilen oder größeren Stapler einsetzen.",
                optionen=_opts(
                    ("Ich hebe die Palette ganz langsam, das gleicht den Schwerpunkt aus", False),
                    ("Ich lese das Lastdiagramm ab und teile die Last bei Bedarf auf zwei Paletten auf", True),
                    ("Ich fahre rückwärts, dann wirkt der Lastschwerpunkt nicht", False),
                    ("Bei 750 mm darf ich ohnehin nur die halbe Nenntragfähigkeit heben — ich nehme sie ganz", False),
                ),
            ),
            FrageDef(
                text="Du fährst mit gehobener Last in eine Kurve. Was ist daran falsch?",
                erklaerung="Kurven nur mit *abgesenkter* Last und reduziertem Tempo fahren — gehobene "
                "Last verschiebt den Schwerpunkt nach oben und erhöht massiv das seitliche Kippmoment.",
                optionen=_opts(
                    ("Nichts — solange du das Lenkrad ruhig hältst", False),
                    ("Die Sicht ist nach vorn nicht eingeschränkt", False),
                    ("Mit gehobener Last droht seitliches Kippen — Last immer absenken vor der Kurve", True),
                    ("Die Hupe muss in jeder Kurve betätigt werden, sonst Verstoß", False),
                ),
            ),
            FrageDef(
                text="Beim Verlassen des Staplers willst du nur kurz aufs WC. Was musst du tun?",
                erklaerung="Auch bei kurzen Pausen: Gabel absenken, Feststellbremse anziehen, Schlüssel "
                "abziehen. Sonst können Unbefugte fahren oder der Stapler rollt weg.",
                optionen=_opts(
                    ("Motor laufen lassen, ist schneller wieder einsatzbereit", False),
                    ("Gabel oben lassen, dann ist sie nicht im Weg", False),
                    ("Gabel absenken, Feststellbremse, Schlüssel abziehen — auch bei kurzer Pause", True),
                    ("Nur Schlüssel abziehen, der Rest ist Kollegen-freundlich", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur Anschnallpflicht im Stapler ist richtig?",
                erklaerung="Sobald ein Beckengurt vorhanden ist, ist Anschnallen Pflicht. Bei einem "
                "Kipper wird der ungesicherte Fahrer sonst vom Fahrerschutzdach erschlagen.",
                optionen=_opts(
                    ("Anschnallen ist optional, der Fahrerschutz reicht aus", False),
                    ("Beckengurt anlegen ist Pflicht, sobald der Stapler einen hat", True),
                    ("Anschnallen nur bei Fahrten über 10 km/h", False),
                    ("Bügeltüren ersetzen den Gurt nicht — beide gemeinsam Pflicht", False),
                ),
            ),
            FrageDef(
                text="Welche Folgerung aus dem Lastdiagramm ist falsch?",
                erklaerung="Höhere Hubhöhe *verringert* die zulässige Last, weil sich der Gesamtschwerpunkt "
                "nach oben verschiebt und der Stapler kopflastiger wird.",
                optionen=_opts(
                    ("Je weiter der Lastschwerpunkt vorn, desto geringer die Tragfähigkeit", False),
                    ("Je höher die Hubhöhe, desto höher die zulässige Last", True),
                    ("Anbaugeräte erfordern ein eigenes Lastdiagramm", False),
                    ("Außerhalb der Kurve droht Kippen", False),
                ),
            ),
            FrageDef(
                text="Du fährst seit 14 Monaten keinen Stapler mehr, weil du in einer anderen Abteilung warst. Heute sollst du wieder fahren. Darfst du?",
                erklaerung="Nach § 7 Abs. 4 DGUV V 68 muss die Beauftragung entzogen werden, wenn keine "
                "ausreichende und regelmäßige Fahrpraxis im Jahr nachgewiesen ist — vorher praktische Bewertung nötig.",
                optionen=_opts(
                    ("Ja, der Staplerschein gilt unbefristet", False),
                    ("Nein — nach mehr als 12 Monaten Pause braucht es eine erneute praktische Bewertung", True),
                    ("Ja, aber nur bei Lasten unter 500 kg", False),
                    ("Nein, ich muss den kompletten Staplerschein wiederholen", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur jährlichen UVV-Prüfung ist falsch?",
                erklaerung="Die wiederkehrende Prüfung darf nur eine *befähigte Person* (Sachkundige:r) "
                "durchführen, nicht der Fahrer selbst. Die Abfahrtkontrolle vor Schichtbeginn ist davon getrennt.",
                optionen=_opts(
                    ("Die Prüfung erfolgt mindestens einmal jährlich", False),
                    ("Sie wird durch eine grüne Plakette am Stapler dokumentiert", False),
                    ("Der Fahrer darf die jährliche UVV-Prüfung selbst durchführen", True),
                    ("Sie prüft Bremsen, Lenkung, Hubmast, Hydraulik und Rückhaltesystem", False),
                ),
            ),
            FrageDef(
                text="Welcher Unfallmechanismus ist beim Gabelstapler besonders tödlich, wenn der Fahrer NICHT angeschnallt ist?",
                erklaerung="Beim seitlichen Kippen versucht der ungesicherte Fahrer instinktiv auszusteigen "
                "und wird vom Fahrerschutzdach (FOPS) erschlagen oder eingequetscht.",
                optionen=_opts(
                    ("Verbrennungen am Auspuff", False),
                    ("Erschlagen vom Fahrerschutzdach beim Kippen", True),
                    ("Stromschlag durch defekte Hydraulik", False),
                    ("Stürzen von der Gabel beim Rückwärtsfahren", False),
                ),
            ),
            FrageDef(
                text="Du transportierst eine schwere Last auf einer Rampe mit 8 Prozent Steigung. Wie führst du die Last?",
                erklaerung="Auf Steigungen wird die Last *bergauf* geführt, also beim Hochfahren mit der "
                "Last voran. Das verhindert Abrutschen und reduziert das Kippmoment.",
                optionen=_opts(
                    ("Last in Fahrtrichtung nach vorn, egal ob bergauf oder bergab", False),
                    ("Last immer bergauf — beim Hochfahren mit der Last voran, beim Runterfahren rückwärts", True),
                    ("Last so hoch wie möglich, damit sie nicht verrutscht", False),
                    ("Steigungen über 5 Prozent darf ich gar nicht befahren", False),
                ),
            ),
            FrageDef(
                text="Ein neuer Kollege hat einen Staplerschein aus seiner alten Firma. Darf er bei euch sofort fahren?",
                erklaerung="Der Staplerschein ist nur Stufe 1. Es braucht zusätzlich die schriftliche "
                "Beauftragung *durch den neuen Arbeitgeber* und die betriebliche Unterweisung auf das konkrete Gerät und die Halle.",
                optionen=_opts(
                    ("Ja, der Staplerschein ist firmenübergreifend gültig", False),
                    ("Nein — er braucht neue Beauftragung und betriebliche Unterweisung", True),
                    ("Ja, aber nur wenn der alte Arbeitgeber zustimmt", False),
                    ("Nein, er muss den Staplerschein in jeder Firma neu machen", False),
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
                    "## Worum geht's?\n\n"
                    "Das Lieferkettensorgfaltspflichtengesetz, kurz **LkSG**, ist seit 2023 in "
                    "Kraft und seit 2024 auf alle Unternehmen mit mindestens 1.000 Beschäftigten "
                    "in Deutschland anwendbar. Es verpflichtet diese Unternehmen, in ihrer eigenen "
                    "Geschäftstätigkeit und entlang ihrer Lieferkette Menschenrechts- und "
                    "bestimmte Umweltrisiken zu erkennen, zu vermeiden und zu beheben. Auch wenn "
                    "dein Arbeitgeber selbst unter 1.000 Beschäftigte hat, betrifft dich das "
                    "Thema fast sicher: als Tier-1-Zulieferer eines Konzern-Kunden musst du dessen "
                    "LkSG-Anforderungen durchreichen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 1 LkSG** — Anwendungsbereich: seit 01.01.2024 Unternehmen ab 1.000 Beschäftigten in Deutschland\n"
                    "- **§ 2 LkSG** — Begriffsbestimmungen: geschützte Rechtspositionen, Lieferkette, eigener Geschäftsbereich\n"
                    "- **§ 3 LkSG** — die neun Sorgfaltspflichten\n"
                    "- **EU-Richtlinie 2024/1760 (CSDDD)** — Nachfolge-Richtlinie, Umsetzung in nationales Recht bis 26.07.2027, Anwendung ab 26.07.2028\n\n"
                    "## Was musst du wissen\n\n"
                    "Das Gesetz schützt zwei Bereiche: **Menschenrechte** und ausgewählte "
                    "**Umweltrisiken**. Geschützt sind unter anderem das Verbot von Kinderarbeit, "
                    "Zwangsarbeit und Sklaverei, der Schutz vor Diskriminierung, der Arbeits- "
                    "und Gesundheitsschutz, das Recht auf faire Löhne, die Vereinigungsfreiheit "
                    "sowie das Verbot von Folter und widerrechtlicher Landenteignung. Im Umweltteil "
                    "geht es um die Konventionen zu Quecksilber (Minamata), persistenten organischen "
                    "Schadstoffen (POPs) und der grenzüberschreitenden Verbringung gefährlicher "
                    "Abfälle (Basler Übereinkommen).\n\n"
                    "Wichtig ist die Abstufung nach Nähe zum Risiko:\n\n"
                    "| Bereich | Was ist umfasst | Pflichten-Tiefe |\n"
                    "|---|---|---|\n"
                    "| Eigener Geschäftsbereich | Werke, Büros, Tochterunternehmen mit beherrschendem Einfluss | volle Sorgfaltspflicht |\n"
                    "| Unmittelbare Zulieferer (Tier 1) | Vertragspartner mit Liefervertrag | volle Sorgfaltspflicht inklusive Prävention |\n"
                    "| Mittelbare Zulieferer (Tier 2+) | alle weiteren Stufen bis zur Rohstoffquelle | anlassbezogene Pflicht bei substantiiertem Hinweis |\n\n"
                    "**Schwellenwerte:** Beschäftigte werden inklusive entsandter Konzernmitarbeiter "
                    "und in der Regel auch Leiharbeitnehmer mit mehr als sechs Monaten Einsatzdauer "
                    "gezählt. Auslandsstandorte zählen mit, soweit sie deutscher Konzern-Mutter "
                    "zuzurechnen sind.\n\n"
                    "Die EU-Nachfolge-Richtlinie **CSDDD** weitet den Kreis ab 2028 stufenweise "
                    "aus: zunächst große EU-Unternehmen ab 5.000 Beschäftigten und 1,5 Mrd. EUR "
                    "Umsatz, später ab 1.000 Beschäftigten und 450 Mio. EUR. Außerdem werden "
                    "zivilrechtliche Schadenersatzpflichten und Klima-Plan-Pflichten ergänzt — "
                    "deutlich schärfer als das LkSG.\n\n"
                    "## Was musst du tun\n\n"
                    "Auch ohne LkSG-Beauftragten-Funktion hat dein Verhalten Einfluss:\n\n"
                    "1. Beachte die Konzern-Vorgaben des Kunden, etwa den Code of Conduct, der mit "
                    "der Bestellung verschickt wird\n"
                    "2. Beantworte Lieferanten-Selbstauskünfte (z.B. EcoVadis, NQC SAQ 5.0) "
                    "wahrheitsgemäß und vollständig\n"
                    "3. Melde Risiko-Hinweise zu Sub-Zulieferern an die LkSG-Verantwortlichen, "
                    "nicht direkt an den Kunden\n"
                    "4. Akzeptiere keine Bargeld-Bezahlung oder ungewöhnliche Konditionen, wenn "
                    "du Auslandsmaterial bestellst — das sind klassische Indikatoren für Risiken\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein mittelständischer Zerspanungsbetrieb mit 180 Beschäftigten beliefert "
                    "einen Automobil-Konzern, der dem LkSG unterliegt. Im Quartals-Audit fragt der "
                    "Kunde nach: woher kommt das Wolfram in den Schneideinsätzen? Der Einkauf "
                    "muss die Lieferkette bis zur Mine zurückverfolgen — und stellt fest, dass "
                    "das Material über einen Zwischenhändler aus der Region der Großen Seen "
                    "stammt, einem Konflikt-Mineralien-Gebiet. Der Kunde verlangt einen "
                    "RMI-zertifizierten Lieferanten oder droht mit Sperrung. Der Betrieb wechselt "
                    "zu einem österreichischen Recyclingmaterial-Anbieter, dokumentiert den "
                    "Wechsel und schickt eine schriftliche Bestätigung an den Kunden — Vertrag "
                    "gerettet.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf das Lieferkettensorgfaltspflichtengesetz (LkSG, BGBl. "
                    "2021 I S. 2959, zuletzt geändert 2023), die EU-Richtlinie 2024/1760 *Corporate "
                    "Sustainability Due Diligence Directive* sowie die BAFA-Handreichung "
                    "*Anwendungsbereich des LkSG* (Stand 2024)."
                ),
            ),
            ModulDef(
                titel="Sorgfaltspflichten",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Das LkSG schreibt in § 3 neun konkrete Sorgfaltspflichten vor, die jedes "
                    "verpflichtete Unternehmen umsetzen muss. Diese Pflichten sind kein moralisches "
                    "Bekenntnis, sondern prüfbare Prozesse, die das **BAFA** (Bundesamt für "
                    "Wirtschaft und Ausfuhrkontrolle) jährlich kontrolliert. Wer die Pflichten "
                    "missachtet, riskiert Bußgelder bis 800.000 EUR im Einzelfall — bei "
                    "Konzernen mit über 400 Mio. EUR Jahresumsatz sogar bis zu **2 Prozent des "
                    "weltweiten Jahresumsatzes** — sowie den Ausschluss von öffentlichen "
                    "Aufträgen für bis zu drei Jahre.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 3 LkSG** — die neun Sorgfaltspflichten\n"
                    "- **§ 4 LkSG** — Risikomanagement-System\n"
                    "- **§ 5 LkSG** — Risikoanalyse, jährlich und anlassbezogen\n"
                    "- **§ 6 LkSG** — Präventionsmaßnahmen im eigenen Geschäftsbereich und bei Zulieferern\n"
                    "- **§ 7 LkSG** — Abhilfemaßnahmen bei Verletzungen\n"
                    "- **§ 9 LkSG** — Pflichten in Bezug auf mittelbare Zulieferer\n"
                    "- **§ 10 LkSG** — Dokumentation und jährliche Berichterstattung\n"
                    "- **§ 24 LkSG** — Bußgeldvorschriften\n\n"
                    "## Was musst du wissen\n\n"
                    "Die neun Sorgfaltspflichten bauen aufeinander auf:\n\n"
                    "| Nr. | Pflicht | Kurzbeschreibung |\n"
                    "|---|---|---|\n"
                    "| 1 | Risikomanagement | Prozess zur Identifikation und Steuerung von Risiken |\n"
                    "| 2 | Beauftragter | Menschenrechtsbeauftragter berichtet direkt an Geschäftsleitung |\n"
                    "| 3 | Risikoanalyse | jährlich und anlassbezogen, eigener Bereich + Tier 1 |\n"
                    "| 4 | Grundsatzerklärung | öffentlich, von der Leitung unterzeichnet |\n"
                    "| 5 | Präventionsmaßnahmen | Schulungen, Vertragsklauseln, Kontrollen |\n"
                    "| 6 | Abhilfemaßnahmen | bei festgestellter Verletzung sofort wirksam |\n"
                    "| 7 | Beschwerdeverfahren | siehe nächstes Modul |\n"
                    "| 8 | Mittelbare Zulieferer | anlassbezogene Prüfung bei substantiiertem Hinweis |\n"
                    "| 9 | Dokumentation und Bericht | mindestens 7 Jahre aufbewahren, Bericht ans BAFA |\n\n"
                    "Die **Risikoanalyse nach § 5** ist das Herzstück. Sie läuft typischerweise so: "
                    "zuerst werden alle direkten Zulieferer nach abstrakten Risiko-Indikatoren "
                    "gewichtet — Branche, Herkunftsland, Rohstoffart. Hoch-Risiko-Lieferanten "
                    "(z.B. Textil aus Südostasien, Kobalt aus DR Kongo, Naturstein aus Indien) "
                    "werden konkret geprüft, über Selbstauskunft, Audit oder Vor-Ort-Begehung. "
                    "Die Risikoanalyse muss mindestens einmal jährlich aktualisiert werden und "
                    "**anlassbezogen** bei wesentlichen Änderungen — neuer Lieferant, neue "
                    "Produktgruppe, neuer Beschwerdehinweis.\n\n"
                    "Eine wichtige Klarstellung: Das Gesetz fordert keine *Erfolgs-Pflicht*, "
                    "sondern eine **Bemühenspflicht**. Du musst nicht beweisen, dass es nirgends "
                    "in deiner Kette ein Problem gibt — aber du musst belegen, dass du angemessene "
                    "Schritte unternommen hast, um Risiken zu identifizieren, zu mindern und im "
                    "Schadensfall zu beheben. Dokumentation ist deshalb genauso wichtig wie das "
                    "Handeln selbst.\n\n"
                    "## Was musst du tun\n\n"
                    "Im operativen Tagesgeschäft setzt das LkSG folgendes voraus:\n\n"
                    "1. Lies und unterzeichne den Code of Conduct deines Arbeitgebers — er ist "
                    "die Umsetzung der Grundsatzerklärung nach § 6\n"
                    "2. Nimm an LkSG-Schulungen teil und dokumentiere die Teilnahme nachweisbar\n"
                    "3. Prüfe bei Neulieferanten-Anlage, ob eine Lieferanten-Selbstauskunft "
                    "vorliegt — kein Vertrag ohne ausgefüllten Fragebogen\n"
                    "4. Melde Auffälligkeiten (ungewöhnlich niedrige Preise, fehlende Audits, "
                    "Gerüchte über Arbeitsbedingungen) sofort an Einkauf oder Beauftragten\n"
                    "5. Aktualisiere die Risikobewertung deiner Lieferanten jährlich und "
                    "anlassbezogen, etwa nach Pressemeldungen\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Maschinenbauer entdeckt bei der Risikoanalyse, dass sein Schweißelektroden-"
                    "Lieferant aus China zwar selbst zertifiziert ist, aber das Vormaterial Mangan "
                    "aus einer Mine in Südafrika bezieht, die in einem NGO-Bericht wegen "
                    "Kinderarbeit erwähnt wurde. Das ist ein **substantiierter Hinweis** im Sinne "
                    "des § 9 — der Maschinenbauer ist als Tier-1-Auftraggeber jetzt verpflichtet, "
                    "der Sache nachzugehen, obwohl die Mine für ihn Tier 3 ist. Er fordert vom "
                    "chinesischen Lieferanten einen Nachweis zur Herkunft, beauftragt ein "
                    "Drittprüfer-Audit und nimmt das Ergebnis in seinen Jahresbericht ans BAFA "
                    "auf. Folgekosten: ca. 18.000 EUR — viel weniger als ein mögliches Bußgeld.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf §§ 3-10 und § 24 LkSG (BGBl. 2021 I S. 2959), die "
                    "BAFA-Handreichung *Risikoanalyse nach dem Lieferkettensorgfaltspflichten-"
                    "gesetz* (Stand 2023) sowie die *Fragen und Antworten zum LkSG* des BAFA "
                    "(Stand 2024)."
                ),
            ),
            ModulDef(
                titel="Beschwerdeverfahren in der Lieferkette",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Das **Beschwerdeverfahren** nach § 8 LkSG ist der Kanal, über den Beschäftigte "
                    "und Außenstehende auf Menschenrechts- und Umweltrisiken in der Lieferkette "
                    "hinweisen können. Es muss für eigene Beschäftigte, für Mitarbeiter der "
                    "Zulieferer und für betroffene Dritte (z.B. Anwohner einer Mine oder Plantage) "
                    "**erreichbar, vertraulich und wirksam** sein. Faktisch verschmilzt das "
                    "LkSG-Verfahren oft mit dem HinSchG-Hinweisgebersystem zu einem einzigen "
                    "Meldekanal — bei Vaeren erfüllt `hinweise.app.vaeren.de` beide Funktionen "
                    "gleichzeitig.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 8 LkSG** — Beschwerdeverfahren: Zuständigkeit, Verfahrensordnung, Schutz vor Benachteiligung\n"
                    "- **§ 9 Abs. 1 LkSG** — Beschwerde-Erstreckung auf mittelbare Zulieferer\n"
                    "- **§ 22 LkSG** — Pflicht zur Veröffentlichung der Verfahrensordnung\n"
                    "- **HinSchG** — bei Bedarf parallel anwendbar, identischer Kanal zulässig\n\n"
                    "## Was musst du wissen\n\n"
                    "Das Verfahren muss in der Praxis fünf Anforderungen erfüllen:\n\n"
                    "| Anforderung | Konkrete Ausprägung |\n"
                    "|---|---|\n"
                    "| Erreichbar | mehrsprachig, über das Internet, für Externe ohne Login |\n"
                    "| Vertraulich | Identität des Hinweisgebers wird geschützt, Pseudonym möglich |\n"
                    "| Unparteiisch | Bearbeiter ist nicht in das gemeldete Geschehen involviert |\n"
                    "| Wirksam | dokumentierter Prozess von Eingangsbestätigung bis Abschlussmeldung |\n"
                    "| Bekannt | Verfahrensordnung ist öffentlich auf der Website abrufbar |\n\n"
                    "Die **Fristen** sind festgeschrieben: Eingangsbestätigung **innerhalb von "
                    "sieben Tagen**, Rückmeldung an den Hinweisgeber zum Fortgang **innerhalb "
                    "von drei Monaten**. Diese Fristen entsprechen denen des HinSchG, daher die "
                    "Sinnhaftigkeit des kombinierten Kanals.\n\n"
                    "Das Verfahren erstreckt sich auf alle **geschützten Rechtspositionen** nach "
                    "§ 2 LkSG: Kinderarbeit, Zwangsarbeit, moderne Sklaverei, Missachtung des "
                    "Arbeitsschutzes, Vorenthalten eines angemessenen Lohns, Behinderung der "
                    "Vereinigungsfreiheit, Diskriminierung, Folter, widerrechtliche Landenteignung "
                    "und der Einsatz privater oder öffentlicher Sicherheitskräfte unter "
                    "Menschenrechtsverletzung. Auf der Umweltseite kommen Quecksilber-Verschmutzung "
                    "(Minamata-Konvention), persistente organische Schadstoffe (Stockholm-Konvention) "
                    "und gefährliche Abfallverbringung (Basler Konvention) hinzu.\n\n"
                    "Hinweisgeber dürfen **nicht benachteiligt** werden. Wer Repressalien "
                    "gegen einen Hinweisgeber ausübt — Kündigung, Versetzung, Mobbing, "
                    "Lieferanten-Sperrung als Strafe — handelt nach § 8 Abs. 4 LkSG und nach "
                    "§ 36 HinSchG widerrechtlich. Die Beweislast wird dabei umgekehrt: der "
                    "Arbeitgeber muss beweisen, dass die negative Maßnahme nichts mit der "
                    "Meldung zu tun hatte.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du in deinem Arbeitsumfeld einen Hinweis auf eine Lieferketten-Verletzung "
                    "wahrnimmst — sei es bei einem Lieferanten-Audit, durch ein Gespräch mit "
                    "einem Sub-Zulieferer-Mitarbeiter oder durch einen Pressebericht — gehe so vor:\n\n"
                    "1. Notiere die Beobachtung mit Datum, Ort, beteiligten Personen und Quelle\n"
                    "2. Nutze den offiziellen Meldekanal deines Arbeitgebers (Webformular oder Ombudsperson)\n"
                    "3. Bevorzuge den internen Weg vor externen Behörden — das LkSG erwartet die Erstmeldung intern\n"
                    "4. Vermerke, ob du anonym bleiben möchtest — die Verfahrensordnung erlaubt das\n"
                    "5. Reagiere auf Rückfragen der Prüfer, lieber zeitnah als perfekt formuliert\n"
                    "6. Sprich nicht öffentlich oder mit Wettbewerbern über den Vorgang, solange die Prüfung läuft\n\n"
                    "Als Bearbeiter einer Meldung gilt umgekehrt: Eingangsbestätigung sofort "
                    "rausschicken (auch bei Anonym-Meldungen mit Rückantwort-Token), Inhalte "
                    "verschlüsselt speichern, Zugriff streng nach Need-to-know-Prinzip, "
                    "Dokumentation revisionssicher.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Schichtführer in einem Kunststoffverarbeitungsbetrieb erfährt bei einem "
                    "Vor-Ort-Termin in der polnischen Niederlassung des Granulat-Lieferanten, dass "
                    "dort regelmäßig 14-stündige Schichten gefahren werden und zwei Mitarbeiter "
                    "deutlich jünger aussehen als 18. Er meldet den Verdacht über das interne "
                    "Hinweisgeber-Portal (anonym), die Bearbeiterin bestätigt den Eingang nach "
                    "zwei Tagen, leitet ein Audit ein und stellt fest: das Geburtsdatum eines "
                    "16-Jährigen wurde im HR-System manipuliert. Der Lieferant wird zu sofortigen "
                    "Abhilfemaßnahmen verpflichtet (§ 7 LkSG: Schicht-Reduzierung, Lohnnachzahlung, "
                    "externes Audit-Folgetermin in sechs Monaten). Bei Wiederholung wird der "
                    "Liefervertrag gekündigt. Der Schichtführer erfährt nach drei Monaten "
                    "vom Ergebnis, sein Name bleibt anonym, seine Position wird nicht berührt.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf § 8 LkSG sowie die BAFA-Handreichung *Beschwerdeverfahren "
                    "nach dem Lieferkettensorgfaltspflichtengesetz* (Stand 2023) und die UN "
                    "*Guiding Principles on Business and Human Rights*, Prinzip 31 (Effektivitäts-"
                    "kriterien für Beschwerdemechanismen)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Ab welcher Beschäftigtenzahl gilt das LkSG seit 2024?",
                erklaerung="Seit dem 01.01.2024 gilt das LkSG für Unternehmen mit mindestens "
                "1.000 Beschäftigten in Deutschland (zuvor 3.000 in 2023).",
                optionen=_opts(
                    ("Ab 250 Beschäftigten", False),
                    ("Ab 500 Beschäftigten", False),
                    ("Ab 1.000 Beschäftigten", True),
                    ("Ab 3.000 Beschäftigten", False),
                ),
            ),
            FrageDef(
                text="Welche Behörde kontrolliert in Deutschland die Einhaltung des LkSG?",
                erklaerung="Das Bundesamt für Wirtschaft und Ausfuhrkontrolle (BAFA) ist nach "
                "§ 19 LkSG für die behördliche Kontrolle zuständig.",
                optionen=_opts(
                    ("Die Bundesnetzagentur", False),
                    ("Das BAFA — Bundesamt für Wirtschaft und Ausfuhrkontrolle", True),
                    ("Das Bundeskartellamt", False),
                    ("Die zuständige Industrie- und Handelskammer", False),
                ),
            ),
            FrageDef(
                text="Welche Risikokategorie betrifft die Verbringung gefährlicher Abfälle?",
                erklaerung="Das Basler Übereinkommen über die grenzüberschreitende Verbringung "
                "gefährlicher Abfälle ist eine der drei Umwelt-Konventionen im LkSG.",
                optionen=_opts(
                    ("Menschenrechte allgemein", False),
                    ("Umweltrisiken — Basler Konvention", True),
                    ("Arbeitsschutz", False),
                    ("Korruptionsbekämpfung", False),
                ),
            ),
            FrageDef(
                text="Wie viele Sorgfaltspflichten zählt § 3 LkSG auf?",
                erklaerung="Es sind neun Pflichten: Risikomanagement, Beauftragter, Risikoanalyse, "
                "Grundsatzerklärung, Präventions-, Abhilfemaßnahmen, Beschwerdeverfahren, "
                "mittelbare Zulieferer, Dokumentation und Bericht.",
                optionen=_opts(
                    ("Fünf", False),
                    ("Sieben", False),
                    ("Neun", True),
                    ("Zwölf", False),
                ),
            ),
            FrageDef(
                text="In welchem Rhythmus muss die Risikoanalyse nach § 5 LkSG mindestens erfolgen?",
                erklaerung="Die Risikoanalyse ist jährlich und zusätzlich anlassbezogen "
                "(bei wesentlichen Änderungen) durchzuführen.",
                optionen=_opts(
                    ("Alle drei Jahre", False),
                    ("Jährlich plus anlassbezogen bei wesentlichen Änderungen", True),
                    ("Nur einmalig bei Inkrafttreten", False),
                    ("Nur bei Aufforderung durch das BAFA", False),
                ),
            ),
            FrageDef(
                text="Wie hoch ist das Bußgeld nach § 24 LkSG für einen Einzelfall maximal?",
                erklaerung="Bis zu 800.000 EUR im Einzelfall, bei Konzernumsatz über 400 Mio. EUR "
                "alternativ bis zu 2 Prozent des weltweiten Konzernumsatzes.",
                optionen=_opts(
                    ("Bis 50.000 EUR", False),
                    ("Bis 800.000 EUR (bzw. 2 Prozent Konzernumsatz)", True),
                    ("Bis 50 Mio. EUR pauschal", False),
                    ("Es gibt keine Geldbuße, nur Verwarnungen", False),
                ),
            ),
            FrageDef(
                text="Welche EU-Richtlinie folgt dem LkSG als europäische Erweiterung?",
                erklaerung="Die Corporate Sustainability Due Diligence Directive (CSDDD, "
                "Richtlinie 2024/1760), Anwendung ab 26.07.2028.",
                optionen=_opts(
                    ("CSRD — Corporate Sustainability Reporting Directive", False),
                    ("CSDDD — Corporate Sustainability Due Diligence Directive", True),
                    ("REACH-Verordnung", False),
                    ("DSGVO", False),
                ),
            ),
            FrageDef(
                text="Du bekommst von einem neuen Lieferanten ein auffallend niedriges Preisangebot für Textilien aus Bangladesch ohne jeden Sozial-Audit-Nachweis. Was tust du?",
                erklaerung="Auffällige Preise plus fehlende Audits sind klassische Risikoindikatoren. "
                "Erst Selbstauskunft und Audit anfordern, dann erst Vertrag.",
                optionen=_opts(
                    ("Sofort bestellen, der Einkaufspreis ist top", False),
                    ("Lieferanten-Selbstauskunft und ein Sozial-Audit anfordern, vorher kein Vertrag", True),
                    ("Anonym beim BAFA anzeigen", False),
                    ("Den Lieferanten ohne Prüfung beim Wettbewerber empfehlen", False),
                ),
            ),
            FrageDef(
                text="Du hörst von einem Sub-Sub-Lieferanten (Tier 3) über Kinderarbeit. Wie ist das einzuordnen?",
                erklaerung="Ein konkreter Hinweis zu einem mittelbaren Zulieferer ist ein "
                "substantiierter Hinweis nach § 9 LkSG — er löst die anlassbezogene Prüfpflicht aus.",
                optionen=_opts(
                    ("Tier 3 ist egal, das LkSG endet bei Tier 1", False),
                    ("Substantiierter Hinweis nach § 9 — anlassbezogene Prüfung auch für mittelbare Zulieferer", True),
                    ("Das ist ausschließlich Sache der örtlichen Behörden vor Ort", False),
                    ("Nur relevant, wenn die Presse berichtet", False),
                ),
            ),
            FrageDef(
                text="Eine Lieferanten-Selbstauskunft (z.B. EcoVadis, NQC SAQ) liegt auf deinem Tisch. Wie füllst du sie aus?",
                erklaerung="Falsche Angaben gefährden den Geschäftsverlust beim Kunden und können "
                "intern arbeitsrechtliche Folgen haben — Wahrheit ist nicht verhandelbar.",
                optionen=_opts(
                    ("Vollständig und wahrheitsgemäß, gegebenenfalls mit Hinweis auf laufende Verbesserungen", True),
                    ("Optimistisch alles auf grün setzen, damit der Kunde nicht zögert", False),
                    ("Nur die einfachen Felder ausfüllen, den Rest leer lassen", False),
                    ("Den Fragebogen ignorieren, niemand prüft das wirklich", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine Hinweisgeber-Meldung zu LkSG-Verstößen bearbeiten. Bis wann musst du den Eingang bestätigen?",
                erklaerung="Sieben Tage Eingangsbestätigung, drei Monate Fortgangsmeldung — "
                "identisch zum HinSchG.",
                optionen=_opts(
                    ("Innerhalb von 24 Stunden", False),
                    ("Innerhalb von sieben Tagen", True),
                    ("Innerhalb von drei Monaten", False),
                    ("Es gibt keine gesetzliche Frist", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege schlägt vor, einen Hinweisgeber wegen 'Loyalitätsmangel' zu versetzen. Was sagst du?",
                erklaerung="§ 8 Abs. 4 LkSG verbietet Repressalien gegen Hinweisgeber, "
                "die Beweislast liegt beim Arbeitgeber. Versetzung wäre ein Verstoß.",
                optionen=_opts(
                    ("Gute Idee, das schreckt andere ab", False),
                    ("Stopp — Repressalien gegen Hinweisgeber sind nach § 8 LkSG verboten, Beweislast-Umkehr droht", True),
                    ("Nur in Ordnung, wenn man es als Förderung tarnt", False),
                    ("Egal, das LkSG schützt nur externe Hinweisgeber", False),
                ),
            ),
            FrageDef(
                text="Du entdeckst, dass eure Brandschutz-Türen-Lieferung von einem Lieferanten mit fragwürdigen Audit-Berichten kommt. Wer ist dein erster Ansprechpartner?",
                erklaerung="Das LkSG erwartet die Erstmeldung intern — bei Beauftragten oder über "
                "das interne Beschwerdeverfahren. Externe Behörden sind letzte Eskalationsstufe.",
                optionen=_opts(
                    ("Das BAFA direkt", False),
                    ("Der LkSG-Beauftragte bzw. das interne Meldeportal", True),
                    ("Die lokale Polizei", False),
                    ("Ein Wettbewerber, um sich abzusichern", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur Pflicht-Tiefe ist richtig?",
                erklaerung="Das LkSG fordert eine Bemühenspflicht (Mittel) — du musst angemessene "
                "Schritte tun, aber kein Null-Risiko garantieren.",
                optionen=_opts(
                    ("Erfolgspflicht: jeder Verstoß in der Kette ist sofort eine Ordnungswidrigkeit", False),
                    ("Bemühenspflicht: angemessene Schritte sind verpflichtend, nicht das Ergebnis", True),
                    ("Wahlpflicht: Unternehmen können freiwillig teilnehmen", False),
                    ("Überwachungspflicht nur durch externe Auditoren, nicht durch das Unternehmen selbst", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Maßnahmen ist KEINE typische Präventionsmaßnahme nach § 6 LkSG?",
                erklaerung="Strafanzeige gegen einen Lieferanten ohne Beleg ist nicht Prävention, "
                "sondern eine missbräuchliche Eskalation. Schulungen, Vertragsklauseln und Audits "
                "dagegen sind klassische Präventionsmittel.",
                optionen=_opts(
                    ("Schulung der eigenen Beschäftigten", False),
                    ("Aufnahme von Menschenrechtsklauseln in Lieferantenverträge", False),
                    ("Lieferanten-Audits durch eigene oder externe Prüfer", False),
                    ("Sofortige Strafanzeige gegen den Lieferanten ohne Prüfung", True),
                ),
            ),
            FrageDef(
                text="Wie lange muss die LkSG-Dokumentation nach § 10 mindestens aufbewahrt werden?",
                erklaerung="Sieben Jahre Aufbewahrungsfrist für Risikoanalysen, Maßnahmen, "
                "Berichte und Beschwerden.",
                optionen=_opts(
                    ("Ein Jahr", False),
                    ("Drei Jahre", False),
                    ("Sieben Jahre", True),
                    ("Zwanzig Jahre", False),
                ),
            ),
            FrageDef(
                text="Ein interner Bericht behauptet 'Wir sind LkSG-konform, weil unser Lieferant ein ISO-9001-Zertifikat hat'. Ist das richtig?",
                erklaerung="ISO 9001 ist ein Qualitätsmanagement-Zertifikat, keine Aussage zu "
                "Menschenrechten. Verwechslung mit z.B. SA8000 (Sozial-Standard) wäre eine "
                "klassische Falsch-Äquivalenz.",
                optionen=_opts(
                    ("Ja, ISO 9001 deckt LkSG-Anforderungen ab", False),
                    ("Nein — ISO 9001 ist Qualitätsmanagement, kein Menschenrechts-Standard", True),
                    ("Ja, sofern das Zertifikat aktuell ist", False),
                    ("Nur in der Automobilindustrie", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden geschützten Rechtspositionen ist NICHT im LkSG ausdrücklich aufgeführt?",
                erklaerung="Tarifvertrags-Pflicht ist deutsches Arbeitsrecht, aber keine "
                "international-rechtlich geschützte Position im Sinne des § 2 LkSG. Kinderarbeit, "
                "Vereinigungsfreiheit und Diskriminierungsverbot sind ausdrücklich genannt.",
                optionen=_opts(
                    ("Verbot von Kinderarbeit", False),
                    ("Vereinigungsfreiheit und Recht auf Kollektivverhandlungen", False),
                    ("Verbot der Diskriminierung in Beschäftigung und Beruf", False),
                    ("Pflicht zum Abschluss eines deutschen Flächentarifvertrags", True),
                ),
            ),
            FrageDef(
                text="Du arbeitest in einem Mittelständler mit 180 Beschäftigten. Bist du vom LkSG betroffen?",
                erklaerung="Direkt unterliegt der Betrieb nicht — der Schwellenwert ist 1.000. "
                "Indirekt sehr wohl, sobald LkSG-pflichtige Konzern-Kunden beliefert werden und "
                "deren Anforderungen durchgereicht werden.",
                optionen=_opts(
                    ("Nein, weit unter 1.000 Beschäftigten", False),
                    ("Ja, das LkSG gilt für alle Unternehmen", False),
                    ("Nicht direkt, aber indirekt als Tier-1-Zulieferer der LkSG-pflichtigen Kunden", True),
                    ("Nur wenn ein Konzern-Kunde aus den USA kommt", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Maß-/Fehl-Praxis am Beschwerdeverfahren ist nach LkSG kritisch?",
                erklaerung="Das Verfahren muss vertraulich und unabhängig sein. Ein Bearbeiter, "
                "der selbst in das gemeldete Geschehen involviert ist, verletzt die "
                "Unparteilichkeits-Anforderung.",
                optionen=_opts(
                    ("Anonyme Meldungen werden über Rückantwort-Token bearbeitet", False),
                    ("Der LkSG-Beauftragte ist Mitglied der Geschäftsleitung", False),
                    ("Der Bearbeiter der Meldung ist selbst Teil des gemeldeten Geschäftsbereichs", True),
                    ("Die Verfahrensordnung ist auf der Firmen-Website veröffentlicht", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #15
    KursDef(
        titel="Geldwäscheprävention (GwG)",
        beschreibung="Grundlagen Geldwäschegesetz (§ 6 GwG) + § 261 StGB. Verdachtsmerkmale, KYC-Pflichten, Meldewege FIU.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Was ist Geldwäsche?",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Geldwäsche ist der Versuch, Geld aus Straftaten so durch den legalen "
                    "Wirtschaftskreislauf zu schleusen, dass die kriminelle Herkunft "
                    "verschleiert wird. Aus 'schmutzigem' Bargeld wird formal sauberes "
                    "Guthaben auf einem Konto, eine Immobilie oder eine quittierte "
                    "Maschinenrechnung. Das klingt nach Mafia-Film, betrifft aber jeden "
                    "Mittelständler, der Bargeschäfte über 10.000 Euro abwickelt — also "
                    "den Maschinenverkauf, den Edelmetall-Ankauf, den Auto-Handel und "
                    "den Schrott-Aufkauf. Du lernst, warum das Thema deine Firma direkt "
                    "betrifft, welche drei Phasen ein typischer Geldwäsche-Vorgang "
                    "durchläuft und welche Strafen drohen, wenn jemand bei euch "
                    "absichtlich oder leichtfertig mitwirkt.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 261 StGB** — Geldwäsche als Straftat, Freiheitsstrafe bis 5 "
                    "Jahre, in schweren Fällen bis 10 Jahre\n"
                    "- **§ 1 GwG** — Begriffsbestimmungen, Definition von Geldwäsche "
                    "und Terrorismusfinanzierung\n"
                    "- **§ 2 GwG** — Verpflichtete: u.a. Banken, Versicherungen, "
                    "Notare, Güterhändler ab Bargeldgrenze\n"
                    "- **§ 56 GwG** — Bußgelder bis 5 Mio. Euro oder 10 % des "
                    "Jahresumsatzes bei vorsätzlichen Verstößen\n\n"
                    "Seit der Reform 2021 ist *jede* Straftat eine Vortat zur "
                    "Geldwäsche — früher gab es einen abschließenden Katalog "
                    "(Drogen, Waffen, Menschenhandel). Heute reicht eine "
                    "Steuerhinterziehung, eine Bestechung oder ein Betrug. Damit ist "
                    "die Schwelle deutlich gesunken, und der Aufsichtsdruck auf "
                    "Verpflichtete entsprechend gestiegen.\n\n"
                    "## Was musst du wissen\n\n"
                    "Klassisch läuft Geldwäsche in drei Phasen ab:\n\n"
                    "1. **Placement** — das Bargeld kommt ins Finanzsystem, oft durch "
                    "Bareinzahlung, Wechselstube oder Kauf hochwertiger Güter\n"
                    "2. **Layering** — durch viele Transaktionen über Konten, Länder "
                    "und Strukturen wird die Herkunftsspur verwischt\n"
                    "3. **Integration** — das nun 'saubere' Geld wird investiert, "
                    "z.B. in Immobilien, Firmenbeteiligungen oder Luxusgüter\n\n"
                    "Für den Mittelstand ist Phase 1 die kritische Phase: ein "
                    "Käufer bietet plump Bargeld für eine gebrauchte CNC-Maschine, "
                    "ein Schrotthändler zahlt eine ungewöhnlich hohe Anzahlung in "
                    "bar, jemand will eine teure Sonderanfertigung *anonym* "
                    "abwickeln. Wer das wissentlich oder *leichtfertig* mitmacht, "
                    "macht sich nach § 261 StGB strafbar — Vorsatz ist nicht "
                    "nötig, grobe Fahrlässigkeit reicht.\n\n"
                    "Verpflichtete im Sinne des § 2 GwG sind nicht nur Banken. "
                    "Güterhändler werden ab einem Bargeldgeschäft von 10.000 "
                    "Euro erfasst (§ 2 Abs. 1 Nr. 16 GwG) — das gilt für eine "
                    "Einmal-Transaktion oder für mehrere wirtschaftlich "
                    "zusammenhängende Teilzahlungen. Wer Edelmetalle handelt, ist "
                    "schon ab 2.000 Euro Bargeld verpflichtet. Auch Kunsthändler, "
                    "Immobilienmakler und Versicherungsvermittler stehen auf der "
                    "Liste.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Prüfe vor jedem Bargeschäft, ob die 10.000-Euro-Schwelle "
                    "(bzw. 2.000 Euro bei Edelmetall) im Spiel ist\n"
                    "2. Lehne 'künstliche' Stückelung ab — zwei Rechnungen über "
                    "je 9.500 Euro statt einer über 19.000 sind ein klares Warnsignal\n"
                    "3. Sprich bei Unsicherheit *vor* Vertragsschluss mit dem "
                    "GwG-Beauftragten deiner Firma\n"
                    "4. Dokumentiere Identität und Hintergrund des Geschäfts "
                    "sauber — Aufbewahrungsfrist beträgt 5 Jahre (§ 8 GwG)\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Maschinenbauer aus Schwaben verkauft eine gebrauchte "
                    "Drehmaschine für 38.000 Euro. Der Käufer, eine GmbH aus dem "
                    "Ausland, schlägt vor, in vier Teilzahlungen je 9.500 Euro bar "
                    "über zwei Wochen abzuwickeln — 'wegen der Steuer'. Der "
                    "Vertriebsleiter erkennt die Stückelung knapp unter der "
                    "10.000-Euro-Schwelle, holt den GwG-Beauftragten dazu und lehnt "
                    "die Bargeldzahlung ab. Stattdessen wird auf Überweisung "
                    "umgestellt, der wirtschaftlich Berechtigte der Käufer-GmbH "
                    "identifiziert. Später stellt sich heraus, dass die GmbH "
                    "Ermittlungsverfahren wegen Umsatzsteuerbetrug am Hals hat — "
                    "der saubere Umgang hat dem Maschinenbauer eine "
                    "Bußgeldverfügung der BaFin und Mittäterschaft erspart.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf das Geldwäschegesetz (GwG, Stand 2025), "
                    "§ 261 StGB sowie die *Auslegungs- und Anwendungshinweise* der "
                    "BaFin zum GwG (Allgemeiner Teil, Stand 2024)."
                ),
            ),
            ModulDef(
                titel="Verdachtsmerkmale erkennen",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Geldwäsche kommt selten als plumper Koffer mit Bargeld daher. "
                    "Sie versteckt sich hinter normal aussehenden Geschäftsvorgängen, "
                    "die nur in der Summe ein 'nicht erklärbares Bild' ergeben. Du "
                    "lernst, welche Muster typische Warnzeichen sind, warum kein "
                    "einzelnes Merkmal allein ausreicht und wie du den Schritt vom "
                    "Bauchgefühl zum dokumentierten Verdachtsfall machst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 43 GwG** — Verdachtsmeldepflicht bei Tatsachen, die auf "
                    "Geldwäsche, Terrorismusfinanzierung oder eine Vortat hindeuten\n"
                    "- **§ 15 GwG** — Verstärkte Sorgfaltspflichten bei höherem "
                    "Risiko (Hochrisikoländer, PEPs, undurchsichtige Strukturen)\n"
                    "- **Anlage 2 GwG** — Faktoren für ein potenziell höheres "
                    "Risiko (Bargeld-Intensität, anonyme Strukturen, geografische "
                    "Risiken)\n\n"
                    "Maßgeblich sind die *Auslegungs- und Anwendungshinweise* der "
                    "BaFin und die FATF-Listen der Hochrisikodrittstaaten — beide "
                    "werden regelmäßig aktualisiert.\n\n"
                    "## Was musst du wissen\n\n"
                    "Typische Verdachtsmuster im Mittelstand:\n\n"
                    "- Ungewöhnlich hohe Bargeldzahlungen ohne plausiblen Grund, "
                    "vor allem an Stelle gängiger Überweisung\n"
                    "- *Smurfing* — künstliche Aufteilung in Teilbeträge knapp "
                    "unter 10.000 Euro, z.B. drei Mal 9.800 Euro statt einmal 29.400\n"
                    "- Auffällige Eile, Druck auf schnellen Abschluss, kein "
                    "Interesse an Preisverhandlung oder Qualität\n"
                    "- *Drittzahlungen* — Rechnung geht an Firma A, Zahlung kommt "
                    "von Firma B oder einer Privatperson ohne erkennbare Verbindung\n"
                    "- Wirtschaftlich Berechtigter unklar oder kurzfristig "
                    "wechselnd, verschachtelte Konzernstrukturen in Offshore-Orten\n"
                    "- Zahlungen aus oder über Hochrisiko-Drittstaaten (FATF-Liste, "
                    "z.B. Iran, Nordkorea, Myanmar — Stand 2025)\n"
                    "- Politisch exponierte Personen (PEPs) ohne plausible Erklärung "
                    "der Mittelherkunft\n"
                    "- Geschäftspartner verweigert die Identifizierung oder reicht "
                    "auffällig schlecht gefälschte Ausweisdokumente ein\n\n"
                    "Geografische Risiken sind ein eigener Faktor. Die FATF "
                    "(Financial Action Task Force) veröffentlicht zweimal jährlich "
                    "die Liste der *high-risk jurisdictions*. Wer regelmäßig mit "
                    "diesen Ländern Geschäfte macht, muss verstärkte Sorgfalt "
                    "anwenden — Mittelherkunft, Geschäftshintergrund, weitere "
                    "Beteiligte werden detaillierter geprüft.\n\n"
                    "Ein einzelnes Merkmal ist *kein* Verdacht. Bargeld plus Eile "
                    "kann ein Tourist sein, der seine Maschine schnell brauchen "
                    "möchte. Erst das Zusammentreffen mehrerer Merkmale, für das "
                    "es keine plausible Erklärung gibt, begründet die "
                    "Meldepflicht nach § 43 GwG. Der gesetzliche Maßstab sind "
                    "*Tatsachen, die darauf hindeuten* — keine Beweise, keine "
                    "Gewissheit.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Notiere Auffälligkeiten sofort schriftlich mit Datum, "
                    "Uhrzeit und konkreten Beobachtungen — kein Bauchgefühl, "
                    "sondern Fakten\n"
                    "2. Frage höflich nach Hintergrund und Mittelherkunft, lass "
                    "Antworten dokumentieren\n"
                    "3. Informiere den GwG-Beauftragten oder die "
                    "Geschäftsführung *bevor* du den Vorgang abschließt\n"
                    "4. Sprich den Verdacht *niemals* gegenüber dem "
                    "Geschäftspartner an — das verstößt gegen das "
                    "Tipping-off-Verbot (§ 47 GwG) und ist strafbar\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Metallrecycling-Betrieb in NRW soll für 26.000 Euro "
                    "Altmetall an einen neuen Kunden verkaufen, der mit "
                    "tschechischer Firma auftritt, aber bar in Euro bezahlen will. "
                    "Er erscheint in einem Mietwagen ohne Firmenlogo, drängt auf "
                    "Abschluss heute noch und will keine Quittung auf den "
                    "Firmennamen, sondern auf einen 'Mitarbeiter'. Drei Merkmale "
                    "häufen sich: Bargeld weit über Schwelle, Eile, unklarer "
                    "wirtschaftlich Berechtigter. Der Verkaufsleiter unterbricht "
                    "das Gespräch, ruft den GwG-Beauftragten, der noch am selben "
                    "Tag eine Verdachtsmeldung per goAML an die FIU absetzt — und "
                    "den Kunden mit der korrekten Begründung 'interne Prüfung "
                    "läuft' vertröstet.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf §§ 15, 43 GwG (Stand 2025), die "
                    "*Anlage 2 zum GwG* sowie die FATF *High-Risk Jurisdictions "
                    "List* und die BaFin-Auslegungshinweise zum GwG (2024)."
                ),
            ),
            ModulDef(
                titel="KYC & Meldepflicht",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "*Know Your Customer* (KYC) ist die Pflicht, vor und während "
                    "einer Geschäftsbeziehung zu wissen, mit wem man Geschäfte "
                    "macht — wer hinter einer Firma steht, woher das Geld kommt, "
                    "wofür es eingesetzt wird. Wenn trotz aller Sorgfalt ein "
                    "Verdacht entsteht, greift die Meldepflicht an die FIU. Du "
                    "lernst, welche Schritte die KYC-Prüfung im Mittelstand "
                    "umfasst, wie eine Verdachtsmeldung über goAML funktioniert "
                    "und welcher Schutz für dich als Meldende oder Meldender "
                    "besteht.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 10 GwG** — Allgemeine Sorgfaltspflichten "
                    "(Identifizierung, Zweck, fortlaufende Überwachung)\n"
                    "- **§ 11 GwG** — Identifizierung von Vertragspartner und "
                    "wirtschaftlich Berechtigtem\n"
                    "- **§ 15 GwG** — Verstärkte Sorgfaltspflichten bei höherem "
                    "Risiko\n"
                    "- **§ 43 GwG** — Meldepflicht an die FIU bei Verdacht\n"
                    "- **§ 47 GwG** — Verbot der Informationsweitergabe an den "
                    "Betroffenen (Tipping-off-Verbot)\n"
                    "- **§ 48 GwG** — Haftungsfreistellung für gutgläubige "
                    "Meldungen\n\n"
                    "## Was musst du wissen\n\n"
                    "Die KYC-Prüfung umfasst nach § 10 GwG drei Blöcke:\n\n"
                    "| Schritt | Inhalt | Beleg |\n"
                    "|---|---|---|\n"
                    "| Identifizierung Vertragspartner | Name, Geburtsdatum, Adresse, Staatsangehörigkeit | Ausweis oder Reisepass, Handelsregister |\n"
                    "| Wirtschaftlich Berechtigte ermitteln | Natürliche Person mit >25 % Anteil oder Kontrolle | Transparenzregister-Auszug, Eigenangabe |\n"
                    "| Zweck und Hintergrund | Geschäftsmodell, erwarteter Umfang, Mittelherkunft | Verträge, Plausibilitätsprüfung |\n\n"
                    "Bei politisch exponierten Personen (PEPs), Hochrisiko-Drittstaaten "
                    "oder undurchsichtigen Strukturen kommen *verstärkte "
                    "Sorgfaltspflichten* nach § 15 GwG dazu: Genehmigung durch die "
                    "Geschäftsleitung vor Geschäftsabschluss, vertiefte "
                    "Mittelherkunfts-Prüfung und engere fortlaufende Überwachung.\n\n"
                    "Die Identifizierung muss *vor* Begründung der "
                    "Geschäftsbeziehung oder spätestens beim Erreichen der "
                    "Schwelle abgeschlossen sein. Akzeptiert werden Ausweis, "
                    "Reisepass oder gleichwertige Dokumente — bei juristischen "
                    "Personen Handelsregisterauszug plus Identifizierung der "
                    "vertretungsberechtigten natürlichen Person. Alle Belege "
                    "sind 5 Jahre aufzubewahren (§ 8 GwG).\n\n"
                    "Bei Verdacht meldet der Verpflichtete *unverzüglich* an die "
                    "Financial Intelligence Unit (FIU), die beim Zoll angesiedelt "
                    "ist. Der Meldeweg läuft elektronisch über das Portal "
                    "*goAML*. Wichtig:\n\n"
                    "- Die Meldung muss erfolgen, auch wenn die Transaktion "
                    "letztlich nicht ausgeführt wird\n"
                    "- Beweise sind nicht erforderlich — *Tatsachen, die "
                    "hindeuten* reichen aus\n"
                    "- Solange die FIU nicht zustimmt oder drei Werktage verstreichen, "
                    "darf die Transaktion *nicht* durchgeführt werden (§ 46 GwG)\n"
                    "- Der Geschäftspartner darf weder direkt noch indirekt "
                    "über die Meldung informiert werden (§ 47 GwG, *Tipping-off-Verbot*)\n\n"
                    "Wer in gutem Glauben meldet, ist nach § 48 GwG umfassend "
                    "geschützt: weder zivil- noch strafrechtliche Haftung, auch "
                    "wenn sich der Verdacht im Nachhinein als unbegründet "
                    "erweist. Wer dagegen meldepflichtige Sachverhalte verschweigt, "
                    "riskiert nach § 56 GwG Bußgelder bis 5 Mio. Euro und "
                    "persönliche Strafbarkeit nach § 261 StGB.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Identifiziere bei jedem Schwellenwert-Geschäft Vertragspartner "
                    "*und* wirtschaftlich Berechtigte vor Vertragsschluss\n"
                    "2. Prüfe Transparenzregister oder fordere eine Eigenangabe "
                    "des Kunden zur Beteiligungsstruktur an\n"
                    "3. Wende verstärkte Prüfung an, sobald PEP, "
                    "Hochrisikoland oder verdächtige Struktur ins Spiel kommt\n"
                    "4. Melde Verdachtsfälle umgehend über den GwG-Beauftragten "
                    "an die FIU via goAML — niemals selbstständig den "
                    "Geschäftspartner damit konfrontieren\n"
                    "5. Bewahre alle KYC-Belege und Meldungen 5 Jahre revisionssicher auf\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Anlagenbauer schließt einen Liefervertrag über 480.000 "
                    "Euro mit einer neu gegründeten GmbH ab. Das Transparenzregister "
                    "zeigt eine Holding auf Zypern als Alleingesellschafterin, deren "
                    "wirtschaftlich Berechtigter eine Person ist, die in einer "
                    "internationalen Sanktionsliste auftaucht. Die "
                    "Geldwäschebeauftragte verweigert den Vertragsabschluss, "
                    "dokumentiert alle Prüfschritte, meldet den Sachverhalt über "
                    "goAML an die FIU und informiert die Bank, dass eine geplante "
                    "Eingangszahlung zurückzuhalten ist. Der Kunde wird mit "
                    "neutraler Begründung 'interne Compliance-Prüfung dauert "
                    "an' vertröstet. Die FIU bestätigt nach zwei Werktagen — "
                    "die Transaktion findet nicht statt, ein "
                    "Bußgeldrisiko in sechsstelliger Höhe wird vermieden.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf §§ 8, 10, 11, 15, 43-48 GwG (Stand 2025), "
                    "das *goAML-Handbuch* der FIU beim Zoll sowie die BaFin "
                    "*Auslegungs- und Anwendungshinweise zum GwG* (2024)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Was beschreibt die Phase 'Placement' im klassischen Drei-Phasen-Modell der Geldwäsche?",
                erklaerung="Placement ist die erste Phase: das Bargeld aus Straftaten gelangt in das legale Finanzsystem, oft durch Bareinzahlung oder Kauf hochwertiger Güter.",
                optionen=_opts(
                    ("Das Einbringen von Bargeld in das Finanzsystem", True),
                    ("Die Verschleierung durch viele kleine Transaktionen", False),
                    ("Die Reinvestition in Immobilien und Firmen", False),
                    ("Die Anzeige bei der Aufsichtsbehörde", False),
                ),
            ),
            FrageDef(
                text="Ab welcher Bargeldgrenze ist ein Güterhändler nach § 2 GwG verpflichtet?",
                erklaerung="§ 2 Abs. 1 Nr. 16 GwG: ab 10.000 Euro Bargeld pro Transaktion oder verbundenen Teilzahlungen. Bei Edelmetallen gilt eine niedrigere Schwelle von 2.000 Euro.",
                optionen=_opts(
                    ("Ab 1.000 Euro Bargeld", False),
                    ("Ab 10.000 Euro Bargeld pro Transaktion oder verbundenen Teilzahlungen", True),
                    ("Ab 50.000 Euro Bargeld", False),
                    ("Es gibt keine Bargeldgrenze", False),
                ),
            ),
            FrageDef(
                text="Welche Strafe sieht § 261 StGB für Geldwäsche im Grundtatbestand vor?",
                erklaerung="§ 261 StGB sieht Freiheitsstrafe bis zu 5 Jahren oder Geldstrafe vor, in besonders schweren Fällen bis zu 10 Jahren.",
                optionen=_opts(
                    ("Verwarnung mit Verwarnungsgeld", False),
                    ("Bußgeld bis 100 Euro", False),
                    ("Freiheitsstrafe bis zu 5 Jahren oder Geldstrafe", True),
                    ("Ausschließlich Verbandsgeldbuße", False),
                ),
            ),
            FrageDef(
                text="Seit der Reform 2021 sind Vortaten der Geldwäsche...",
                erklaerung="Seit 2021 ist *jede* Straftat Vortat zur Geldwäsche — früher gab es einen abschließenden Vortatenkatalog. Damit ist die Schwelle deutlich gesunken.",
                optionen=_opts(
                    ("auf Drogenhandel und Terrorismusfinanzierung begrenzt", False),
                    ("nur Straftaten aus einem abschließenden Katalog", False),
                    ("alle Straftaten — der Katalog wurde aufgegeben", True),
                    ("nur Steuerstraftaten", False),
                ),
            ),
            FrageDef(
                text="Was bezeichnet der Begriff *Smurfing* im GwG-Kontext?",
                erklaerung="Smurfing ist die künstliche Aufteilung einer Summe in mehrere kleinere Beträge knapp unter der Meldegrenze, um die KYC-Pflicht zu umgehen.",
                optionen=_opts(
                    ("Aufteilung einer Geldsumme in kleinere Beträge knapp unter der Meldegrenze", True),
                    ("Geheime Codewörter im Banking", False),
                    ("Eine zulässige Form der Steueroptimierung", False),
                    ("Bargeldeinzahlung in Wechselstuben", False),
                ),
            ),
            FrageDef(
                text="Du erhältst eine Anfrage, eine Maschinenrechnung in vier Teilzahlungen von je 9.500 Euro bar zu kassieren. Was tust du?",
                erklaerung="Die Stückelung knapp unter der 10.000-Euro-Schwelle ist ein klassisches Smurfing-Muster — Bargeld ablehnen oder als einheitliches Geschäft KYC-pflichtig behandeln.",
                optionen=_opts(
                    ("Annehmen, da jede Einzelzahlung unter der Schwelle liegt", False),
                    ("Annehmen und nichts dokumentieren", False),
                    ("Bargeld ablehnen oder die Teilzahlungen als zusammenhängendes Geschäft mit voller KYC-Prüfung behandeln", True),
                    ("Annehmen, aber den Kunden um Verschwiegenheit bitten", False),
                ),
            ),
            FrageDef(
                text="Wer ist *wirtschaftlich Berechtigter* einer GmbH nach § 3 GwG?",
                erklaerung="Wirtschaftlich Berechtigter ist die natürliche Person, die letztlich mehr als 25 % der Anteile hält oder die Kontrolle in vergleichbarer Weise ausübt.",
                optionen=_opts(
                    ("Die Hausbank der GmbH", False),
                    ("Jede natürliche Person, die mehr als 25 % der Anteile hält oder Kontrolle ausübt", True),
                    ("Der Steuerberater", False),
                    ("Der Vorsitzende des Aufsichtsrats", False),
                ),
            ),
            FrageDef(
                text="An welche Behörde wird ein Geldwäsche-Verdacht in Deutschland gemeldet?",
                erklaerung="Die Meldung geht an die Financial Intelligence Unit (FIU) beim Zoll, elektronisch über das Portal goAML.",
                optionen=_opts(
                    ("Direkt an das Bundeskriminalamt", False),
                    ("An die Financial Intelligence Unit (FIU) über das Portal goAML", True),
                    ("An die eigene Hausbank", False),
                    ("An die Staatsanwaltschaft per Brief", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet das *Tipping-off-Verbot* nach § 47 GwG?",
                erklaerung="Das Tipping-off-Verbot untersagt, den Betroffenen oder Dritte über eine Verdachtsmeldung oder ein Ermittlungsverfahren zu informieren — Verstoß ist strafbar.",
                optionen=_opts(
                    ("Verbot, Trinkgelder anzunehmen", False),
                    ("Pflicht, in jedem Falle Anzeige zu erstatten", False),
                    ("Verbot, den Betroffenen oder Dritte über eine Verdachtsmeldung zu informieren", True),
                    ("Verbot von Bargeldgeschäften unter 1.000 Euro", False),
                ),
            ),
            FrageDef(
                text="Eine *politisch exponierte Person* (PEP) ist im Sinne des GwG...",
                erklaerung="PEPs sind Personen in herausgehobener öffentlicher Funktion (z.B. Minister, Botschafter, Parlamentarier) sowie deren engste Familienangehörige und enge Geschäftspartner — mit erhöhtem Korruptionsrisiko.",
                optionen=_opts(
                    ("jede Person mit aktiver Mitgliedschaft in einer Partei", False),
                    ("eine Person in herausgehobener öffentlicher Funktion plus engste Angehörige und enge Geschäftspartner", True),
                    ("eine Person mit öffentlichem Social-Media-Profil", False),
                    ("ausschließlich Staatsoberhäupter", False),
                ),
            ),
            FrageDef(
                text="Du verkaufst Edelmetall im Wert von 3.500 Euro gegen Bargeld an einen Privatkunden. Was gilt?",
                erklaerung="Für den Edelmetallhandel gilt nach § 2 GwG eine niedrigere Bargeldschwelle von 2.000 Euro — KYC-Pflichten greifen also bereits.",
                optionen=_opts(
                    ("Keine Pflichten, da die 10.000-Euro-Schwelle nicht überschritten ist", False),
                    ("KYC-Pflichten greifen, da für Edelmetallhandel die 2.000-Euro-Schwelle gilt", True),
                    ("Nur eine Quittung ausstellen reicht", False),
                    ("Geschäft komplett ablehnen verpflichtend", False),
                ),
            ),
            FrageDef(
                text="Wie lange müssen Identifizierungs-Unterlagen nach § 8 GwG aufbewahrt werden?",
                erklaerung="§ 8 GwG schreibt eine Aufbewahrungsfrist von 5 Jahren nach Ende der Geschäftsbeziehung vor, höchstens 10 Jahre.",
                optionen=_opts(
                    ("6 Monate", False),
                    ("2 Jahre", False),
                    ("5 Jahre", True),
                    ("30 Jahre", False),
                ),
            ),
            FrageDef(
                text="Welcher der folgenden Sachverhalte ist *kein* eigenständiges Verdachtsmerkmal nach Anlage 2 GwG?",
                erklaerung="Bargeldzahlung allein ist im Mittelstand kein Verdacht — entscheidend ist immer die Gesamtschau mehrerer Auffälligkeiten ohne plausible Erklärung.",
                optionen=_opts(
                    ("Eine ungewöhnliche Drittzahlung ohne wirtschaftliche Verbindung", False),
                    ("Eine einzelne Bargeldzahlung von 800 Euro im normalen Geschäftsbetrieb", True),
                    ("Zahlung aus einem Hochrisiko-Drittstaat", False),
                    ("Ein unklarer oder kurzfristig wechselnder wirtschaftlich Berechtigter", False),
                ),
            ),
            FrageDef(
                text="Du bemerkst bei einem Vorgang Auffälligkeiten. Was darfst du auf *keinen* Fall tun?",
                erklaerung="Den Kunden auf den Verdacht ansprechen ist ein Verstoß gegen § 47 GwG (Tipping-off-Verbot) und persönlich strafbar.",
                optionen=_opts(
                    ("Den Verdacht intern an den GwG-Beauftragten weitergeben", False),
                    ("Den Vorgang detailliert schriftlich dokumentieren", False),
                    ("Den Kunden auf den Verdacht ansprechen und um Aufklärung bitten", True),
                    ("Die Transaktion bis zur Klärung anhalten", False),
                ),
            ),
            FrageDef(
                text="Welche Folge hat eine gutgläubig erstattete Verdachtsmeldung, die sich später als unbegründet erweist?",
                erklaerung="§ 48 GwG stellt gutgläubig Meldende umfassend von zivil- und strafrechtlicher Haftung frei — auch wenn der Verdacht nicht bestätigt wird.",
                optionen=_opts(
                    ("Schadenersatzpflicht gegenüber dem Kunden", False),
                    ("Strafbarkeit wegen falscher Verdächtigung", False),
                    ("Keine Haftung — der Meldende ist nach § 48 GwG umfassend geschützt", True),
                    ("Bußgeld der Aufsichtsbehörde", False),
                ),
            ),
            FrageDef(
                text="Welches der folgenden Bußgelder kann gegen ein Unternehmen bei vorsätzlichem GwG-Verstoß verhängt werden?",
                erklaerung="§ 56 GwG sieht bei vorsätzlichen Verstößen Bußgelder bis 5 Mio. Euro oder bis 10 % des Jahresumsatzes des Unternehmens vor.",
                optionen=_opts(
                    ("Maximal 1.000 Euro", False),
                    ("Maximal 50.000 Euro", False),
                    ("Bis 5 Mio. Euro oder 10 % des Jahresumsatzes", True),
                    ("Es gibt kein Bußgeld, nur eine Verwarnung", False),
                ),
            ),
            FrageDef(
                text="Ein neuer Kunde mit komplexer Konzernstruktur in einem Offshore-Standort will Geschäftsbeziehung aufnehmen. Was ist die richtige Reaktion?",
                erklaerung="Nach § 15 GwG sind verstärkte Sorgfaltspflichten anzuwenden — inklusive Genehmigung der Geschäftsleitung und vertiefter Mittelherkunfts-Prüfung.",
                optionen=_opts(
                    ("Wie üblich Identifizieren und akzeptieren", False),
                    ("Verstärkte Sorgfaltspflichten nach § 15 GwG anwenden und Geschäftsleitung einbinden", True),
                    ("Geschäft ohne Prüfung ablehnen", False),
                    ("Nur den Vertragspartner identifizieren, nicht den Berechtigten", False),
                ),
            ),
            FrageDef(
                text="Welche Phase der Geldwäsche beschreibt das *Layering*?",
                erklaerung="Layering ist die zweite Phase: durch viele Transaktionen über Konten, Länder und Strukturen wird die Herkunftsspur des Geldes verwischt.",
                optionen=_opts(
                    ("Erstmaliges Einbringen von Bargeld ins Finanzsystem", False),
                    ("Verschleierung durch viele Transaktionen über Konten und Länder", True),
                    ("Reinvestition in legale Wirtschaftsgüter", False),
                    ("Anzeige bei der FIU", False),
                ),
            ),
            FrageDef(
                text="Innerhalb welcher Frist nach Verdachtsmeldung darf eine angehaltene Transaktion *grundsätzlich* nicht ausgeführt werden?",
                erklaerung="§ 46 GwG: drei Werktage ab Eingang der Meldung bei der FIU, sofern die FIU der Ausführung nicht vorher zustimmt.",
                optionen=_opts(
                    ("Drei Werktage, sofern die FIU nicht vorher zustimmt", True),
                    ("Sofort ausführbar, die Meldung hat keine aufschiebende Wirkung", False),
                    ("Sechs Monate", False),
                    ("Bis zur Anklageerhebung", False),
                ),
            ),
            FrageDef(
                text="Welche Informationsquelle hilft, den wirtschaftlich Berechtigten einer deutschen GmbH zu ermitteln?",
                erklaerung="Das Transparenzregister erfasst seit 2017 verpflichtend die wirtschaftlich Berechtigten deutscher Gesellschaften und ist seit 2021 ein Vollregister mit Pflicht zur Eintragung.",
                optionen=_opts(
                    ("Das Handelsblatt-Archiv", False),
                    ("Das Transparenzregister", True),
                    ("Die Insolvenzbekanntmachungen", False),
                    ("Die Liste der DAX-Vorstände", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #16
    KursDef(
        titel="Schweißen & Heißarbeiten",
        beschreibung="Schutzunterweisung Schweißen/Brennschneiden/Trennen nach DGUV Regel 100-500 Kapitel 2.26. "
        "Erlaubnisschein, Brand-/Explosionsschutz, Atemwege/Strahlung.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Erlaubnisschein für feuergefährliche Arbeiten",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Ein Funke einer Trennscheibe fliegt bis zu zehn Meter weit und ist beim Aufschlag "
                    "noch rund 1.000 Grad heiß. Wenn du außerhalb eines festen Schweißplatzes "
                    "MAG-, WIG-, E-Hand- oder Brennschneid-Arbeiten ausführst, brauchst du deshalb "
                    "vor Arbeitsbeginn einen schriftlichen Erlaubnisschein. Er ist keine Bürokratie, "
                    "sondern eine kurze Checkliste, die Auftraggeber und Schweißer gemeinsam "
                    "durchgehen, damit keine Brand- oder Explosionsgefahr übersehen wird.\n\n"
                    "Statistik der VdS: rund 30 Prozent aller Großbrände in der Industrie gehen auf "
                    "feuergefährliche Arbeiten zurück, fast immer mit demselben Muster — kein "
                    "Erlaubnisschein, keine Brandwache, brennbares Material in der Nähe.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **DGUV Regel 100-500 Kapitel 2.26** Abschnitt 3.18 — schriftliche Schweißerlaubnis "
                    "  außerhalb fester Schweißplätze\n"
                    "- **DGUV Information 205-002** *Brandschutz bei feuergefährlichen Arbeiten*\n"
                    "- **DGUV Information 205-026** *Brandschutz beim Schweißen* — Brandwache, "
                    "  Nachkontrolle\n"
                    "- **VdS 2008** und **VdS 2036** — Muster-Erlaubnisschein der Sachversicherer\n"
                    "- **§ 5 ArbSchG** — Gefährdungsbeurteilung vor Arbeitsbeginn\n\n"
                    "## Was musst du wissen\n\n"
                    "Ein Erlaubnisschein ist ein A4-Formular mit vier Unterschriften: Auftraggeber, "
                    "ausführende Person, Brandwache und Verantwortliche für die Nachkontrolle. Er "
                    "ist ortsbezogen, zeitlich begrenzt und gilt nur für die beschriebene Tätigkeit.\n\n"
                    "Pflichtfelder auf dem Schein:\n\n"
                    "| Feld | Inhalt |\n"
                    "|---|---|\n"
                    "| Ort und Datum | Halle, Anlage, Datum, Gültigkeit max. 1 Arbeitstag |\n"
                    "| Arbeitsverfahren | MAG, WIG, E-Hand, Brennschneiden, Trennschleifen, Löten |\n"
                    "| Schutzmaßnahmen | Brandlast entfernt, abgedeckt, abgedichtet, befeuchtet |\n"
                    "| Brandwache | Name und Erreichbarkeit während der Arbeit |\n"
                    "| Nachkontrolle | mindestens 2 h nach Arbeitsende, dokumentiert |\n\n"
                    "**Brandwache** heißt: eine namentlich benannte Person ist während der Arbeit "
                    "und mindestens zwei Stunden danach vor Ort, mit Feuerlöscher (mind. 6 kg "
                    "ABC-Pulver oder Schaum), Mobiltelefon und Brandmelder-Zugang. In besonders "
                    "gefährdeten Bereichen wie Holzdecken oder Dämmung kann die Nachkontrolle bis "
                    "zu 24 Stunden dauern.\n\n"
                    "Vorbereitung des Arbeitsbereichs im Umkreis von **mindestens zehn Metern**:\n\n"
                    "- Brennbare Stoffe entfernen oder mit nicht brennbaren Decken abdecken\n"
                    "- Fugen, Ritzen, Wandöffnungen abdichten (Funkenflug-Wege)\n"
                    "- Holzböden befeuchten, brennbare Dämmung gegebenenfalls freilegen\n"
                    "- Geeignete Löscher in Griffweite, Wasserschlauch wenn möglich\n\n"
                    "## Was musst du tun\n\n"
                    "Bevor du den Brenner zündest:\n\n"
                    "1. Erlaubnisschein vom Auftraggeber oder Vorgesetzten ausfüllen und unterschreiben lassen\n"
                    "2. Den Arbeitsbereich gemeinsam mit der Brandwache begehen und Brandlasten beseitigen\n"
                    "3. Prüfen, ob die genannten Löscher tatsächlich am angegebenen Platz hängen\n"
                    "4. Brandmelder im Bereich gegebenenfalls per Erlaubnis stilllegen lassen (Dokumentation!)\n"
                    "5. Erst dann mit den Heißarbeiten beginnen\n\n"
                    "Nach Arbeitsende den Bereich nicht sofort verlassen — die Brandwache übernimmt "
                    "die Nachkontrolle, dokumentiert die Endzeit und gibt den Erlaubnisschein an die "
                    "Schichtleitung zurück. Auch eine vermeintlich erloschene Glutstelle in Dämmung "
                    "kann Stunden später aufflammen.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem Metallverarbeitungsbetrieb soll ein Stahlträger in der Lagerhalle "
                    "abgetrennt werden — kein fester Schweißplatz, also Erlaubnisschein-pflichtig. "
                    "Der Meister füllt den Schein vor Ort aus: Trennschleifer, Brandlast in zwei "
                    "Metern Entfernung sind Holzpaletten, die werden entfernt, ein Funkenschutzvorhang "
                    "wird aufgestellt, ein Lehrling übernimmt als Brandwache mit zwei 6-kg-Pulver"
                    "löschern. Der Schein wird unterschrieben, die Arbeit dauert 40 Minuten. Zwei "
                    "Stunden nach Arbeitsende geht die Brandwache noch einmal die Stelle ab — ein "
                    "kleiner Schwelfunke in einem Wandritz hätte ohne diese Nachkontrolle den "
                    "Dämmstreifen entzündet.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Regel 100-500 Kapitel 2.26 Abschnitt 3.18 *Schweißen, "
                    "Schneiden und verwandte Verfahren* (Ausgabe 2008, aktualisiert 2017), "
                    "DGUV Information 205-002 *Brandschutz bei feuergefährlichen Arbeiten*, "
                    "DGUV Information 205-026 *Brandschutz beim Schweißen* sowie "
                    "VdS-Richtlinie 2008 *Feuergefährliche Arbeiten* (Ausgabe 2020)."
                ),
            ),
            ModulDef(
                titel="Brand- und Explosionsschutz",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Beim Schweißen und Brennschneiden entstehen Temperaturen von 3.000 bis 6.000 Grad, "
                    "Funken fliegen bis zu zehn Meter weit, glühende Schlackeperlen können durch "
                    "schmale Spalten in Hohlräume fallen und dort Schwelbrände auslösen, die "
                    "Stunden später zum Vollbrand werden. Hinzu kommt die Explosionsgefahr in "
                    "Bereichen mit Lösemitteldämpfen, Stäuben oder Brenngasen. Du lernst, welche "
                    "Gefahren konkret entstehen und wie du sie technisch und organisatorisch beherrschst.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **BetrSichV** und **GefStoffV** — Gefährdungsbeurteilung, Explosionsschutz-Dokument\n"
                    "- **TRBS 2152 / TRGS 720-722** — Vermeidung von Zündgefahren in "
                    "  explosionsfähiger Atmosphäre\n"
                    "- **DGUV Regel 100-500 Kapitel 2.26** Abschnitte 3.13 bis 3.20 — Brand- und "
                    "  Explosionsschutz beim Schweißen\n"
                    "- **DGUV Information 205-026** *Brandschutz beim Schweißen*\n\n"
                    "## Was musst du wissen\n\n"
                    "Vier typische Brand-Auslöser beim Schweißen, die in der Unfallstatistik immer "
                    "wieder auftauchen:\n\n"
                    "- Funkenflug durch Wandritz, Schacht oder Bodenfuge in einen Nachbarraum\n"
                    "- Glühende Schlackeperlen, die durch Roste oder Lüftungsöffnungen fallen\n"
                    "- Wärmeleitung im Bauteil: ein verzinkter Stahlträger kann auf der Rückseite "
                    "  ein Holzbalken-Auflager auf 300 Grad bringen\n"
                    "- Brenngase und Sauerstoff aus undichten Schläuchen oder offenen Flaschenventilen\n\n"
                    "Besondere Gefahrenbereiche im Mittelstand:\n\n"
                    "| Bereich | Hauptgefahr | Maßnahme |\n"
                    "|---|---|---|\n"
                    "| Lackiererei, Lager Lösemittel | Lösemitteldämpfe (Ex-Zone) | Freimessen, lüften |\n"
                    "| Silo, Tank, Behälter | Reste brennbarer Stoffe | Reinigen, freimessen, Spülung |\n"
                    "| Dämmwände, abgehängte Decke | Hohlraum-Schwelbrand | öffnen, Nachkontrolle 24 h |\n"
                    "| Förderbänder, Staubsammler | Staub-Ex-Atmosphäre | reinigen, abdecken |\n"
                    "| Lagerhalle mit Holzpaletten | Funkenflug | 10 m Abstand, Schutzvorhang |\n\n"
                    "Bei Arbeiten an Behältern, die brennbare Stoffe enthielten, ist **Freimessen** "
                    "Pflicht — also Messung der Atmosphäre im Inneren mit einem Ex-Messgerät vor "
                    "Arbeitsbeginn. Eine sichtbare Leere des Behälters reicht nicht: ein Tank, der "
                    "Diesel enthielt, hat noch tagelang explosionsfähige Dämpfe in jeder Schweiß"
                    "naht. Mehrere Schweißer im Mittelstand sind genau so gestorben.\n\n"
                    "**Brenngas-Flaschen** (Acetylen, Propan) gehören niemals waagerecht liegend oder "
                    "im Hohlraum, Sauerstoff-Flaschen niemals in Kontakt mit Öl oder Fett — "
                    "Sauerstoff plus Fett kann ohne Zündquelle explosionsartig reagieren. Flaschen "
                    "sind außerhalb der Arbeitspause gegen Umfallen zu sichern und am Ende des "
                    "Arbeitstages aus dem Arbeitsbereich zu entfernen.\n\n"
                    "## Was musst du tun\n\n"
                    "Bei jeder Heißarbeit außerhalb eines festen Schweißplatzes:\n\n"
                    "1. Brandlast in 10 m Umkreis prüfen und entfernen oder mit Schweißerschutzdecke abdecken\n"
                    "2. Wandritzen, Fugen und Bodenöffnungen abdichten (Mineralwolle, feuchte Lappen)\n"
                    "3. Rückseite des Werkstücks prüfen — bei Wärmeleitung Gegenseite kühlen oder freilegen\n"
                    "4. Mindestens einen geeigneten Löscher (6 kg ABC oder Schaum) in Griffweite\n"
                    "5. Bei Behälterarbeit Freimessung dokumentieren, Spülung mit Inertgas wenn nötig\n"
                    "6. Schläuche und Flaschenventile vor Arbeitsbeginn auf Dichtheit prüfen\n\n"
                    "Wenn dir auch nur eine dieser Bedingungen unklar ist: nicht anfangen, sondern "
                    "den Vorgesetzten holen. Ein Brand kostet im Mittel rund 500.000 Euro Schaden "
                    "und kann Existenzen vernichten.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einem Automotive-Zulieferer soll ein verzinktes Geländer im Treppenhaus "
                    "verschweißt werden. Der Schweißer bereitet alles vor: Funkenschutzdecke unten, "
                    "Löscher in Reichweite, Brandwache informiert. Was er übersieht: hinter der "
                    "Treppenwand läuft ein Kabelschacht mit alter PVC-Dämmung. Eine glühende "
                    "Schlackeperle fällt durch einen unsichtbaren Spalt zwischen Bodenblech und "
                    "Wand in den Schacht und entzündet die Dämmung. Nur weil die Brandwache zwei "
                    "Stunden nach Arbeitsende noch einmal mit Wärmebildkamera den Bereich begeht, "
                    "wird der Schwelbrand entdeckt, bevor er das ganze Treppenhaus erfasst.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Regel 100-500 Kapitel 2.26 Abschnitte 3.13 bis 3.20, "
                    "DGUV Information 205-026 *Brandschutz beim Schweißen*, "
                    "TRBS 2152 *Gefährliche explosionsfähige Atmosphäre* sowie "
                    "DGUV Information 205-002 *Brandschutz bei feuergefährlichen Arbeiten*."
                ),
            ),
            ModulDef(
                titel="Atemwege & Strahlenschutz",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Schweißrauche sind seit 2017 von der **IARC** als krebserzeugend für den "
                    "Menschen eingestuft (Gruppe 1) — dieselbe Kategorie wie Asbest und Tabakrauch. "
                    "Gleichzeitig erzeugt der Lichtbogen UV-Strahlung, die schon nach Sekunden "
                    "ungeschützter Belichtung zur schmerzhaften Hornhautentzündung ('Verblitzen') "
                    "führt und langfristig Hautkrebs auslösen kann. Beide Gefahren sind unsichtbar, "
                    "tun beim Arbeiten nicht weh und entfalten ihre Wirkung erst Jahre später — "
                    "deshalb sind sie tückisch.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **TRGS 528** *Schweißtechnische Arbeiten* (Ausgabe 02/2020) — Schutz vor "
                    "  Gefahrstoffen, Stufenplan\n"
                    "- **GefStoffV § 9** — Schutzmaßnahmen-Hierarchie (TOP: technisch vor "
                    "  organisatorisch vor persönlich)\n"
                    "- **OStrV** *Verordnung zum Schutz vor künstlicher optischer Strahlung*\n"
                    "- **DGUV Information 209-010** *Lichtbogenschweißen*\n"
                    "- **DGUV Information 209-049** *Strahlung beim Schweißen und bei verwandten "
                    "  Verfahren*\n\n"
                    "## Was musst du wissen\n\n"
                    "Schweißrauch ist ein Aerosol aus ultrafeinen Metalloxid-Partikeln (unter 0,1 "
                    "Mikrometer). Diese Partikel gehen direkt bis in die Lungenbläschen und über "
                    "die Blutbahn ins ganze Körpersystem. Besonders kritisch beim Schweißen von "
                    "legierten Stählen und Edelstahl:\n\n"
                    "| Stoff | Quelle | Grenzwert (TRGS 900 / AGW) |\n"
                    "|---|---|---|\n"
                    "| Chrom(VI) | Edelstahl, Hochlegiert | 0,01 mg/m3 (seit 01/2025 verschärft) |\n"
                    "| Nickel | Edelstahl, Schutzgas | 0,006 mg/m3 (E-Fraktion) |\n"
                    "| Mangan | Baustahl, MAG | 0,02 mg/m3 (A-Fraktion) |\n"
                    "| Eisenoxid | alle Stahlarbeiten | Allgemeiner Staubgrenzwert 1,25 mg/m3 |\n"
                    "| Ozon | WIG Aluminium | 0,1 mg/m3 |\n\n"
                    "Der **Stufenplan** der TRGS 528 ist verpflichtend in dieser Reihenfolge "
                    "abzuarbeiten:\n\n"
                    "1. Substitution: alternative Verfahren (z.B. mechanisches Fügen statt Schweißen)\n"
                    "2. Erfassung an der Quelle: Brennerabsaugung oder Trichterabsaugung max. 30 cm "
                    "   vom Lichtbogen\n"
                    "3. Raumlüftung: technische Hallenlüftung, Schichtströmung\n"
                    "4. Atemschutz als letzte Stufe: Gebläsehelm TH2P oder TH3P, frischluftunabhängiges "
                    "   Gerät bei beengten Räumen\n\n"
                    "Reine Atemschutzmasken ohne Gebläse (Halbmaske P3) sind nur für kurze Arbeiten "
                    "zulässig und erfordern eine **G26-Eignungsuntersuchung** des Trägers.\n\n"
                    "**UV-Strahlung** des Lichtbogens ist um Größenordnungen stärker als die Sonne. "
                    "Schon zehn Sekunden ungeschützter Blick in einen MAG-Lichtbogen reichen für "
                    "Verblitzen — schmerzhafte Augenentzündung, die 6 bis 24 Stunden nach Exposition "
                    "auftritt. Unbedeckte Haut bekommt nach wenigen Minuten einen 'Schweißerbrand' "
                    "wie schwerer Sonnenbrand. Daher: Schweißerschutzschild mit passender Schutzstufe "
                    "(DIN EN 169, je nach Stromstärke 9 bis 14), Lederhandschuhe, langärmlige "
                    "schwer entflammbare Kleidung, Hals und Nacken bedecken.\n\n"
                    "Auch **Umstehende** sind gefährdet — der reflektierte UV-Anteil verblitzt noch "
                    "in mehreren Metern Entfernung. Deshalb: Schweißplatz mit Schutzvorhängen oder "
                    "Stellwänden abschirmen.\n\n"
                    "## Was musst du tun\n\n"
                    "Vor und während jeder Schweißarbeit:\n\n"
                    "1. Brennerabsaugung oder Trichter direkt am Lichtbogen positionieren, vor jedem Schweißstart\n"
                    "2. Bei beengten Räumen oder Edelstahl-Arbeit zusätzlich Gebläsehelm TH2P/TH3P tragen\n"
                    "3. Schweißerschutzschild mit korrekter Schutzstufe verwenden (Tabelle am Gerät)\n"
                    "4. Lederhandschuhe, Lederschürze, lange Kleidung, Nackentuch — keine offene Haut\n"
                    "5. Schutzvorhänge aufstellen, Kollegen warnen ('Achtung Lichtbogen!')\n"
                    "6. Bei beengten Räumen oder Aluminium-WIG zusätzlich Sauerstoffmessung\n\n"
                    "Bei Verblitzen am Abend: Augen mit kühlen feuchten Tüchern abdecken, "
                    "Schmerzmittel, nicht reiben, am nächsten Tag zum Augenarzt. Nicht selbst "
                    "weiterschweißen — das verschlimmert die Entzündung.\n\n"
                    "## Praxisbeispiel\n\n"
                    "In einer Edelstahl-verarbeitenden Werkstatt schweißt ein Kollege mehrere Wochen "
                    "WIG an Edelstahl-Behältern, ohne die Brennerabsaugung konsequent zu nutzen — "
                    "'der Schlauch stört beim Manövrieren'. Nach einem Jahr Untersuchung beim "
                    "Betriebsarzt: erhöhte Chrom(VI)-Werte im Urin, beginnende Atemwegsreizung. "
                    "Die Geschäfts­führung reagiert: Anschaffung von vier Brenner-Absaugpistolen mit "
                    "integrierter Erfassung, Pflicht-Tragen eines TH3P-Gebläsehelms bei Edelstahl, "
                    "monatliche Wirksamkeitsprüfung der Absaugung dokumentiert. Beim nächsten "
                    "Biomonitoring sechs Monate später ist der Chrom(VI)-Wert wieder im Normbereich.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf TRGS 528 *Schweißtechnische Arbeiten* (BAuA, Ausgabe "
                    "02/2020 mit Änderung 08/2020), TRGS 900 *Arbeitsplatzgrenzwerte* (Stand 2025 "
                    "mit verschärftem Chrom(VI)-Grenzwert), DGUV Information 209-010 *Lichtbogen"
                    "schweißen* (Ausgabe 2017), DGUV Information 209-049 *Strahlung beim Schweißen* "
                    "sowie IARC-Monographie Vol. 118 *Welding, Molybdenum Trioxide, and Indium Tin "
                    "Oxide* (Einstufung Schweißrauch als Gruppe 1, 2017)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wann ist beim Schweißen ein schriftlicher Erlaubnisschein verpflichtend?",
                erklaerung="Nach DGUV Regel 100-500 Kapitel 2.26 ist die schriftliche Schweißerlaubnis "
                "immer dann Pflicht, wenn die Arbeit außerhalb eines fest eingerichteten Schweißplatzes "
                "stattfindet.",
                optionen=_opts(
                    ("Nur, wenn ein Behälter geschweißt wird", False),
                    ("Bei jeder Schweißarbeit außerhalb eines festen Schweißplatzes", True),
                    ("Nur bei Arbeiten über zwei Stunden Dauer", False),
                    ("Nur, wenn ausdrücklich vom Versicherer verlangt", False),
                ),
            ),
            FrageDef(
                text="Wer muss einen Erlaubnisschein für feuergefährliche Arbeiten typischerweise unterschreiben?",
                erklaerung="Standard sind vier Unterschriften: Auftraggeber, ausführende Person, Brandwache "
                "und Verantwortliche für die Nachkontrolle.",
                optionen=_opts(
                    ("Nur der Schweißer", False),
                    ("Auftraggeber, Schweißer, Brandwache und Nachkontroll-Verantwortliche", True),
                    ("Nur die Geschäftsführung", False),
                    ("Schweißer und Betriebsrat", False),
                ),
            ),
            FrageDef(
                text="Wie lange muss die Brandwache nach Ende der Schweißarbeit mindestens vor Ort bleiben?",
                erklaerung="DGUV Information 205-026 fordert eine Nachkontrolle von mindestens zwei Stunden, "
                "bei besonders gefährdeten Bereichen (Holz, Dämmung, Hohlraum) bis zu 24 Stunden.",
                optionen=_opts(
                    ("15 Minuten", False),
                    ("Nicht zwingend, wenn keine Flamme mehr sichtbar ist", False),
                    ("Mindestens 2 Stunden", True),
                    ("Maximal 30 Minuten, damit die Arbeitszeit eingehalten wird", False),
                ),
            ),
            FrageDef(
                text="Wie weit kann ein Schweißfunke maximal fliegen?",
                erklaerung="Funken bzw. glühende Schlackeperlen erreichen rund zehn Meter, bei Trennschleif"
                "arbeiten sogar noch mehr. Deshalb muss in 10 m Umkreis brandlastenfrei gearbeitet werden.",
                optionen=_opts(
                    ("Maximal 2 Meter", False),
                    ("Maximal 5 Meter", False),
                    ("Bis rund 10 Meter, bei Trennschleifern noch weiter", True),
                    ("Nur so weit wie der Lichtbogen", False),
                ),
            ),
            FrageDef(
                text="In welche IARC-Kategorie wurde Schweißrauch 2017 eingestuft?",
                erklaerung="Die IARC stuft Schweißrauch seit 2017 als Gruppe 1 ein — krebserzeugend für "
                "den Menschen, also dieselbe Klasse wie Asbest und Tabakrauch.",
                optionen=_opts(
                    ("Gruppe 3 (nicht klassifizierbar)", False),
                    ("Gruppe 2B (möglicherweise krebserregend)", False),
                    ("Gruppe 1 (krebserregend beim Menschen)", True),
                    ("Nicht klassifiziert", False),
                ),
            ),
            FrageDef(
                text="Welche Reihenfolge schreibt die TRGS 528 für Schutzmaßnahmen vor?",
                erklaerung="Der Stufenplan ist verbindlich: erst Substitution, dann technische Erfassung an "
                "der Quelle, dann Raumlüftung, und Atemschutz erst als letzte Stufe.",
                optionen=_opts(
                    ("Atemschutz, Lüftung, Absaugung, Substitution", False),
                    ("Substitution, Quell-Absaugung, Raumlüftung, Atemschutz", True),
                    ("Persönliche Schutzausrüstung hat immer Vorrang", False),
                    ("Es gibt keine vorgeschriebene Reihenfolge", False),
                ),
            ),
            FrageDef(
                text="Welcher Atemschutz wird beim Edelstahl-Schweißen in der Werkstatt typischerweise empfohlen?",
                erklaerung="Wegen Chrom(VI) und Nickel im Rauch ist ein gebläseunterstützter Schutzhelm "
                "der Klasse TH2P oder TH3P die Regel — kombinierbar mit dem Schweißerschutzschild.",
                optionen=_opts(
                    ("Einfache OP-Maske", False),
                    ("Gebläsehelm TH2P oder TH3P mit Partikelfilter", True),
                    ("Stoffmaske aus dem Haushalt", False),
                    ("Atemschutz ist beim Schweißen nie erforderlich", False),
                ),
            ),
            FrageDef(
                text="Was ist 'Verblitzen' und wie entsteht es?",
                erklaerung="Verblitzen ist eine Hornhautentzündung durch UV-Strahlung des Lichtbogens. "
                "Symptome treten erst 6 bis 24 Stunden später auf — Schmerz, Lichtempfindlichkeit, "
                "Fremdkörpergefühl im Auge.",
                optionen=_opts(
                    ("Ein Stromschlag durch defekte Schweißgeräte", False),
                    ("Eine schmerzhafte Hornhautentzündung durch UV-Strahlung des Lichtbogens", True),
                    ("Das Aufblitzen einer Sicherung im Schweißgerät", False),
                    ("Eine Hautreaktion auf Schweißrauch", False),
                ),
            ),
            FrageDef(
                text="Du sollst einen Tank verschweißen, der früher Diesel enthielt — er ist optisch leer. Was tust du?",
                erklaerung="Optische Leere reicht NIE. In den Schweißnähten und Restschmierschichten "
                "verbleiben tagelang explosionsfähige Dämpfe. Pflicht: Reinigen, Freimessen, ggf. "
                "Inertgasspülung — dokumentiert im Erlaubnisschein.",
                optionen=_opts(
                    ("Sofort schweißen, der Tank ist ja leer", False),
                    ("Reinigen, freimessen, ggf. mit Inertgas spülen und im Erlaubnisschein dokumentieren", True),
                    ("Den Tank fluten und unter Wasser schweißen", False),
                    ("Tank umdrehen und Dämpfe ausgießen", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege schweißt ohne Schutzschild kurz 'mal eben einen Tropfen'. Was ist deine Reaktion?",
                erklaerung="Selbst Sekunden ungeschützter UV-Exposition können Verblitzen auslösen, und "
                "nach § 16 ArbSchG bist du verpflichtet, sicherheitswidriges Verhalten zu melden.",
                optionen=_opts(
                    ("Wegschauen, das ist seine Sache", False),
                    ("Stoppen, auf das Schild verweisen, bei Wiederholung dem Vorgesetzten melden", True),
                    ("Mitfotografieren für die Pinnwand", False),
                    ("Selbst auch ohne Schild mitschweißen, um Solidarität zu zeigen", False),
                ),
            ),
            FrageDef(
                text="Du fängst eine Schweißarbeit außerhalb des festen Schweißplatzes an — der Erlaubnisschein liegt nicht vor. Was tust du?",
                erklaerung="Ohne unterschriebenen Erlaubnisschein ist die Arbeit nach DGUV Regel 100-500 "
                "Kapitel 2.26 unzulässig. Anfangen wäre eine Ordnungswidrigkeit und persönliche Haftung.",
                optionen=_opts(
                    ("Anfangen und den Schein nachreichen lassen", False),
                    ("Nicht beginnen, Vorgesetzten holen und den Schein vor Arbeitsbeginn ausfüllen", True),
                    ("Selbst einen ankreuzen und unterschreiben", False),
                    ("Nur kurz schweißen, dann zählt es nicht", False),
                ),
            ),
            FrageDef(
                text="Du schweißt über einem Holzboden in einer alten Werkstatt. Welche Vorkehrung ist zwingend?",
                erklaerung="Holzboden ist Brandlast. Pflicht: Funkenschutzdecke unterlegen oder Boden "
                "befeuchten plus Brandwache mit verlängerter Nachkontrolle.",
                optionen=_opts(
                    ("Nichts Besonderes, ein Holzboden brennt erst bei direkter Flamme", False),
                    ("Funkenschutzdecke unterlegen, Boden befeuchten und Brandwache stellen", True),
                    ("Den Boden mit Olivenöl einlassen, das senke die Reibung", False),
                    ("Nur einen Eimer Wasser bereitstellen, damit reicht es", False),
                ),
            ),
            FrageDef(
                text="Wie wird die Brennerabsaugung beim MAG-Schweißen typischerweise positioniert?",
                erklaerung="Die Erfassung muss möglichst nah am Entstehungsort sein — etwa 20 bis 30 cm "
                "vom Lichtbogen. Je weiter weg, desto unwirksamer (Quadratabnahme).",
                optionen=_opts(
                    ("Etwa 2 Meter über dem Schweißer", False),
                    ("Maximal 20 bis 30 cm vom Lichtbogen entfernt", True),
                    ("Hinter dem Schweißer auf dem Boden", False),
                    ("Egal — Hauptsache, sie ist eingeschaltet", False),
                ),
            ),
            FrageDef(
                text="Ist es zulässig, eine Sauerstoff-Flasche zur Schmierung kurz mit Maschinenöl einzureiben?",
                erklaerung="Sauerstoff plus Fett oder Öl kann ohne Zündquelle explosionsartig reagieren. "
                "Kontakt von Sauerstoff-Armaturen mit Öl ist strikt verboten.",
                optionen=_opts(
                    ("Ja, wenn nur wenig Öl verwendet wird", False),
                    ("Ja, das verhindert Korrosion", False),
                    ("Nein, Sauerstoff plus Öl kann explosionsartig reagieren", True),
                    ("Nur bei Reinsauerstoff", False),
                ),
            ),
            FrageDef(
                text="Welches Löschmittel ist beim klassischen Schweißfunken-Brand (Holz, Papier) richtig?",
                erklaerung="Brennende Holzpaletten oder Papier sind Brandklasse A — geeignet sind Wasser, "
                "Schaum oder ABC-Pulver. Mindestens ein 6-kg-ABC-Löscher gehört in Griffweite.",
                optionen=_opts(
                    ("D-Pulver", False),
                    ("ABC-Pulver, Schaum oder Wasser (Brandklasse A)", True),
                    ("CO2 ausschließlich", False),
                    ("Klasse-F-Löscher", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zum Arbeitsplatzgrenzwert (AGW) für Chrom(VI) ist seit 2025 korrekt?",
                erklaerung="Seit Januar 2025 gilt der verschärfte AGW von 0,01 mg/m3 für Chrom(VI) "
                "(TRGS 900). Edelstahl-Schweißen ohne wirksame Erfassung erreicht diesen Wert nicht.",
                optionen=_opts(
                    ("Der Grenzwert wurde 2025 abgeschafft", False),
                    ("Der AGW beträgt seit 2025 0,01 mg/m3 — er wurde verschärft", True),
                    ("Es gibt keinen Grenzwert für Chrom(VI)", False),
                    ("Der Grenzwert gilt nur für Kraftwerke", False),
                ),
            ),
            FrageDef(
                text="Du arbeitest in einem engen Behälter und sollst dort 30 Minuten schweißen. Was ist zwingend zu beachten?",
                erklaerung="In engen Räumen ist neben Absaugung auch Sauerstoff-Messung und in der Regel "
                "ein frischluftunabhängiger Atemschutz Pflicht, plus Sicherungsposten außerhalb.",
                optionen=_opts(
                    ("Nichts Besonderes, Hauptsache der Helm sitzt", False),
                    ("Freimessung, Sauerstoffüberwachung, frischluftunabhängiger Atemschutz, Sicherungsposten außen", True),
                    ("Nur eine Halbmaske P2 genügt", False),
                    ("Die Tür offen lassen und schnell arbeiten", False),
                ),
            ),
            FrageDef(
                text="Welcher Schutzstufen-Bereich für Schweißerschutzfilter ist beim MAG-Schweißen mit hoher Stromstärke typisch?",
                erklaerung="Nach DIN EN 169 reichen die Schutzstufen 9 bis 14 — je höher die Stromstärke, "
                "desto höher die nötige Stufe. Bei rund 250 A typischerweise Stufe 12.",
                optionen=_opts(
                    ("Stufe 1 bis 3 reichen aus", False),
                    ("Schutzstufe 9 bis 14, je nach Stromstärke", True),
                    ("Eine normale Sonnenbrille ist ausreichend", False),
                    ("Stufe 5 bis 7", False),
                ),
            ),
            FrageDef(
                text="Eine Brandschutztür in der Werkhalle wird mit einem Keil aufgehalten, damit der Schweißer leichter ein- und ausgehen kann. Wie bewertest du das?",
                erklaerung="Eine offen gekeilte Brandschutztür hebt den ganzen Brandabschnitt auf — "
                "Ordnungswidrigkeit mit Bußgeld bis 50.000 Euro nach LBO. Beim Heißarbeiten ist das "
                "doppelt fahrlässig.",
                optionen=_opts(
                    ("Pragmatisch und in Ordnung", False),
                    ("Ordnungswidrigkeit; Tür sofort schließen und Vorgesetzten informieren", True),
                    ("Nur problematisch, wenn der Schweißer nicht aufpasst", False),
                    ("Egal, solange die Brandwache da ist", False),
                ),
            ),
            FrageDef(
                text="Du siehst nach Ende der Schweißarbeit am Stahlträger einen leichten Rauchgeruch an einer Wandfuge. Was tust du?",
                erklaerung="Rauchgeruch nach Heißarbeit ist Alarmzeichen — könnte ein Schwelbrand im "
                "Hohlraum sein. Pflicht: Bereich öffnen, mit Wärmebildkamera prüfen, Feuerwehr "
                "informieren wenn unklar.",
                optionen=_opts(
                    ("Ignorieren, nach Schweißarbeit riecht es immer", False),
                    ("Bereich öffnen, mit Wärmebildkamera kontrollieren, im Zweifel Feuerwehr alarmieren", True),
                    ("Mit Wasser überkippen und gehen", False),
                    ("Sofort Feierabend machen und morgen prüfen", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #17
    KursDef(
        titel="Ladungssicherung",
        beschreibung="Pflichtunterweisung Versand-/Fahrpersonal nach § 22 StVO + DGUV Vorschrift 70. "
        "Physik der Sicherung, Hilfsmittel & Stauplan.",
        gueltigkeit_monate=12,
        module=(
            ModulDef(
                titel="Physik der Ladungssicherung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Eine EUR-Palette mit Maschinenteilen wiegt schnell 800 kg. Bei einer "
                    "Vollbremsung aus 50 km/h verhält sich diese Palette wie ein Geschoss "
                    "von rund 640 kg, das nach vorne in Richtung Fahrerhaus rutscht — "
                    "wenn sie nicht gesichert ist. Du lernst, warum die Physik der "
                    "Ladungssicherung kein Bauchgefühl ist, sondern eine Berechnung mit "
                    "festen Beschleunigungsfaktoren, und welche Rolle der Reibbeiwert "
                    "und die Antirutschmatte dabei spielen.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 22 Abs. 1 StVO** — Ladung muss so verstaut und gesichert sein, "
                    "dass sie selbst bei Vollbremsung oder plötzlicher Ausweichbewegung "
                    "nicht verrutscht, umfällt, hin- und herrollt, herabfällt oder "
                    "vermeidbaren Lärm erzeugt\n"
                    "- **§ 23 Abs. 1 StVO** — Pflicht des Fahrzeugführers, vor Fahrt"
                    "antritt die vorschriftsmäßige Verladung zu prüfen\n"
                    "- **VDI 2700 ff.** — anerkannte Regel der Technik für Ladungs"
                    "sicherung auf Straßenfahrzeugen\n"
                    "- **DIN EN 12195-1** — Berechnung von Zurrkräften, europäische Norm\n\n"
                    "## Was musst du wissen\n\n"
                    "Die Norm rechnet mit festen *Beschleunigungsfaktoren*, die die "
                    "auftretenden Kräfte in Bruchteilen der Erdbeschleunigung g "
                    "(9,81 m/s²) angeben. Die Ladung muss so gesichert sein, dass "
                    "sie diese Kräfte aushält:\n\n"
                    "| Richtung | Beschleunigungsfaktor | Bedeutung |\n"
                    "|---|---|---|\n"
                    "| nach vorne | 0,8 g | Vollbremsung — 80 Prozent des Eigengewichts drücken nach vorne |\n"
                    "| nach hinten | 0,5 g | starkes Anfahren oder Rückwärtsfahren |\n"
                    "| zur Seite | 0,5 g | Kurvenfahrt oder Ausweichmanöver |\n"
                    "| nach oben | 0,2 g | Schlagloch, Bodenwelle |\n\n"
                    "Konkret heißt das: eine 1.000 kg schwere Palette will bei einer "
                    "Vollbremsung mit 800 daN (rund 800 kg Kraft) nach vorne rutschen. "
                    "Dieser Kraft muss die Sicherung standhalten — sonst rutscht die "
                    "Ladung in die Fahrerkabine.\n\n"
                    "Zwei *Sicherungsverfahren* stehen zur Wahl: Niederzurrung (kraft"
                    "schlüssig) und Direktsicherung (formschlüssig). Bei der "
                    "**Niederzurrung** wird die Ladung von oben mit Zurrgurten "
                    "auf die Ladefläche gepresst — die Reibung hält sie an Ort und "
                    "Stelle. Bei der **Direktsicherung** geht die Kraft direkt durch "
                    "die Gurte in die Zurrpunkte (Diagonal-, Kopflot- oder Schrägzurren).\n\n"
                    "Der *Reibbeiwert* mü (µ) entscheidet bei der Niederzurrung "
                    "über die Anzahl nötiger Gurte. Holz auf Holz hat mü rund 0,2 "
                    "bis 0,3, Holz auf einer geriffelten Stahlpritsche oft nur 0,2. "
                    "Mit einer **Antirutschmatte (RH-Matte)** steigt der Beiwert auf "
                    "rund 0,6 — die Sicherungswirkung mehr als verdoppelt sich, ohne "
                    "dass du einen Gurt mehr brauchst.\n\n"
                    "Rechen-Faustregel Niederzurrung: ohne Antirutschmatte brauchst "
                    "du für eine 1.000-kg-Palette etwa vier bis sechs Gurte vorne, "
                    "mit Antirutschmatte oft nur zwei. Die genaue Zahl liefert die "
                    "VDI 2700 Blatt 2 oder ein geprüfter Berechnungs-App-Rechner.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor jedem Beladen die Pritsche auf Sauberkeit und Trockenheit prüfen — Öl, Eis oder Staub senken den Reibbeiwert\n"
                    "2. Antirutschmatten unter jede Palette und jedes Halbzeug-Bund legen, auch unter den Stapel im zweiten Stock\n"
                    "3. Schwere Ladung nach unten und nach vorne stellen, über der Achse zentriert, nicht auf einer Seite\n"
                    "4. Zurrgurte vor dem Einsatz sichten: keine Risse, kein UV-Schaden, Etikett mit LC-Wert lesbar\n"
                    "5. Gurte stramm vorspannen — die Vorspannkraft STF steht auf dem Etikett und sollte bei Niederzurrung mindestens 300 daN erreichen\n"
                    "6. Nach 50 km und bei jeder Pause nachspannen — Ladung setzt sich, Gurte werden locker\n\n"
                    "Diese Schritte sind nicht Kür, sondern Pflicht aus § 22 StVO und "
                    "der Gefährdungsbeurteilung deines Arbeitgebers.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Versand-Mitarbeiter eines Maschinenbau-Zulieferers verlädt "
                    "drei EUR-Paletten mit Getriebewellen (je rund 700 kg) auf eine "
                    "Sattel-Pritsche. Er stellt die Paletten direkt auf das nackte "
                    "Holz, weil 'die Zeit knapp ist' und 'die Gurte schon halten "
                    "werden'. Bei der Vollbremsung auf der A7 vor einem Stauende "
                    "rutschen alle drei Paletten zusammen einen halben Meter nach "
                    "vorne und durchschlagen die Stirnwand. Die Polizei misst nach: "
                    "Reibbeiwert auf dem trockenen Holz nur 0,2, vier Gurte mit je "
                    "250 daN Vorspannkraft — rechnerisch reichte das für rund "
                    "1.000 kg, gesichert wurden aber 2.100 kg. Bußgeld 75 Euro plus "
                    "ein Punkt für den Fahrer nach § 22 StVO, dazu ein Bußgeld nach "
                    "§ 130 OWiG für die Geschäftsführung wegen Aufsichtspflicht"
                    "verletzung. Mit einer Antirutschmatte (Reibbeiwert 0,6) und der "
                    "doppelten Vorspannkraft wäre die Ladung gesichert gewesen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf § 22 StVO (Stand 2024), VDI 2700 Blatt 2 "
                    "*Berechnung von Sicherungskräften* (Ausgabe 2014, Ergänzungs"
                    "blatt 2.1 von 2025) und DIN EN 12195-1:2010 *Zurrkräfte — "
                    "Berechnungsmethoden*."
                ),
            ),
            ModulDef(
                titel="Hilfsmittel, Stauplan, Verantwortung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Wer haftet, wenn die Ladung verrutscht? Im Straßenverkehr nicht "
                    "nur der Fahrer. Verlader, Verfrachter und Fahrzeugführer bilden "
                    "die **Verantwortungs-Trias** — und alle drei können mit "
                    "Bußgeld, Punkten und im schlimmen Fall mit einem Strafverfahren "
                    "wegen fahrlässiger Körperverletzung belangt werden. Du lernst, "
                    "welche Hilfsmittel zur Verfügung stehen, wie ein Stauplan "
                    "aussieht und wo deine eigene Pflicht beginnt und endet.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **§ 22 Abs. 1 StVO** — Ladungssicherung als objektive Pflicht\n"
                    "- **§ 23 Abs. 1 StVO** — Fahrer prüfen Verkehrssicherheit vor Fahrtantritt\n"
                    "- **§ 31 Abs. 2 StVZO** — Halter darf Inbetriebnahme nicht anordnen, wenn Ladung nicht sicher ist\n"
                    "- **§ 130 OWiG** — Aufsichtspflichtverletzung in Betrieben, bis 1 Mio. Euro\n"
                    "- **DGUV Vorschrift 70 § 37** — Be- und Entladen, Pflicht zur sicheren Verladung\n"
                    "- **§ 412 HGB** — Verfrachter (Spediteur) muss beförderungssicher verladen\n\n"
                    "## Was musst du wissen\n\n"
                    "Die drei verantwortlichen Rollen haben jeweils klare Pflichten:\n\n"
                    "| Rolle | Hauptpflicht | Wer ist das im Betrieb |\n"
                    "|---|---|---|\n"
                    "| Verlader | beförderungssichere Verladung, § 412 HGB | Versand-Mitarbeiter, der Palette auf LKW stellt |\n"
                    "| Verfrachter | Disposition, geeignetes Fahrzeug | Spediteur oder eigene Fuhrpark-Disposition |\n"
                    "| Fahrzeugführer | Endkontrolle, Fahrt nur bei sicherer Ladung | LKW-Fahrer oder Mitarbeiter mit Führerschein |\n\n"
                    "Alle drei haften nebeneinander. Der Fahrer kann sich nicht darauf "
                    "berufen, dass der Verlader die Palette aufgesetzt hat — er muss "
                    "vor Fahrtantritt selbst prüfen.\n\n"
                    "Wichtige *Hilfsmittel* für Ladungssicherung im Industriebetrieb:\n\n"
                    "- **Zurrgurte** nach DIN EN 12195-2 mit LC-Wert (Lashing Capacity) auf dem Etikett\n"
                    "- **Antirutschmatten** (RH-Matten) zur Erhöhung des Reibbeiwerts auf mü 0,6\n"
                    "- **Kantenschoner** schützen Gurt und Ladung an scharfen Kanten\n"
                    "- **Sperrstangen und Sperrbalken** in der Pritsche für Formschluss\n"
                    "- **Lochrasterung der Bordwand** für schnelles Einhängen von Zurrpunkten\n"
                    "- **Stauhölzer und Keile** gegen Rollen von Bünden und Rohren\n\n"
                    "Der *Stauplan* legt fest, wo welche Ladung steht. Faustregeln: "
                    "schwer nach unten, formstabil nach außen, druckempfindlich nach "
                    "oben. Halbzeug-Bunde (z. B. Stahlrohre, Coils) werden mit Keilen "
                    "gegen Rollen gesichert und zusätzlich direkt gezurrt — "
                    "Niederzurrung allein reicht bei rollenden Lasten nicht.\n\n"
                    "**Bußgelder** nach Tatbestandskatalog (Stand 2025):\n\n"
                    "| Verstoß | Bußgeld | Punkte |\n"
                    "|---|---|---|\n"
                    "| Ladung nicht ausreichend gesichert (PKW) | 35 Euro | 0 |\n"
                    "| Ladung nicht ausreichend gesichert (LKW) | 60 Euro | 1 |\n"
                    "| Mit Gefährdung | 75 bis 100 Euro | 1 |\n"
                    "| Mit Unfall / Sachbeschädigung | 120 bis 240 Euro | 1 |\n"
                    "| Verlader / Halter zugelassen | 75 bis 525 Euro | je nach Schwere |\n\n"
                    "Dazu kommen bei betrieblichen Verstößen die Geschäftsleitung "
                    "selbst — § 130 OWiG erlaubt bis zu 1 Mio. Euro Bußgeld bei "
                    "Aufsichtspflichtverletzung, wenn keine ausreichende Unterweisung "
                    "und Kontrolle nachgewiesen werden kann.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor dem Beladen den Stauplan oder Lieferschein lesen — schwere und stabile Stücke zuerst, druckempfindliche obenauf\n"
                    "2. Hilfsmittel vor jeder Tour prüfen: Gurte sichten, Antirutschmatten auf Risse prüfen, Kantenschoner bereitlegen\n"
                    "3. Beim Verladen Ladelückenbildung vermeiden — Spalt zwischen Ladung und Bordwand maximal 1 cm laut VDI 2700\n"
                    "4. Nach dem Verladen visuell prüfen: kein Gurt verdreht, keine scharfe Kante ohne Schoner, kein Stück steht ungesichert\n"
                    "5. Verladevorgang im Frachtbrief oder Lieferschein quittieren — das ist deine Dokumentation im Streitfall\n"
                    "6. Bei Zweifel den Fahrer ansprechen oder die Schichtleitung holen, NIE eine unsichere Ladung mit Schweigen durchwinken\n\n"
                    "Als Verlader bist du in der Pflicht, auch wenn der Fahrer drückt "
                    "oder es eilig ist. Der § 412 HGB nimmt dich in die Mithaftung.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Zulieferer für Automotive verlädt zwei Stahlrohr-Bunde "
                    "(je 1,2 Tonnen) längs auf einen Sattel-LKW. Der Verlader legt "
                    "zwei Antirutschmatten unter und zurrt mit vier Niederzurrgurten. "
                    "Keile gegen Rollen werden vergessen — 'die Matten halten schon'. "
                    "Bei einer Ausweichbewegung auf der Autobahn gehen die Bunde in "
                    "Rollen, einer durchschlägt die Bordwand und rollt auf die "
                    "Gegenfahrbahn. Sachschaden 80.000 Euro. Bußgeldbescheid an drei "
                    "Adressen: Fahrer 120 Euro plus ein Punkt, Verlader 240 Euro, "
                    "Geschäftsführung 4.500 Euro nach § 130 OWiG wegen fehlender "
                    "dokumentierter Unterweisung. Beim nächsten Audit sind Sperrkeile "
                    "auf jedem Sattel-LKW serienmäßig montiert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DGUV Vorschrift 70 *Fahrzeuge* (Ausgabe "
                    "2017), § 22 und § 23 StVO (Stand 2024), § 412 HGB sowie den "
                    "Tatbestandskatalog des Bundesverkehrsministeriums zur "
                    "Ladungssicherung (Stand 2025)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welcher Beschleunigungsfaktor ist nach VDI 2700 für die Sicherung in Fahrtrichtung anzusetzen?",
                erklaerung="Bei einer Vollbremsung treten Kräfte in Höhe von 0,8 g auf — die Sicherung "
                "muss 80 Prozent des Ladungsgewichts als nach vorne wirkende Kraft auffangen.",
                optionen=_opts(
                    ("0,5 g", False),
                    ("0,8 g", True),
                    ("1,0 g", False),
                    ("0,3 g", False),
                ),
            ),
            FrageDef(
                text="Welcher Beschleunigungsfaktor gilt für seitliche Kräfte (Kurvenfahrt, Ausweichmanöver)?",
                erklaerung="Seitlich und nach hinten rechnet die VDI 2700 mit 0,5 g — die Hälfte des "
                "Ladungsgewichts wirkt als seitliche Kraft.",
                optionen=_opts(
                    ("0,2 g", False),
                    ("0,5 g", True),
                    ("0,8 g", False),
                    ("1,0 g", False),
                ),
            ),
            FrageDef(
                text="Welche Vorschrift verlangt, dass Ladung selbst bei Vollbremsung nicht verrutschen darf?",
                erklaerung="§ 22 Abs. 1 StVO ist die zentrale Pflicht — Ladung muss Vollbremsung und "
                "Ausweichbewegung aushalten, ohne zu verrutschen oder vermeidbaren Lärm zu erzeugen.",
                optionen=_opts(
                    ("§ 5 ArbSchG", False),
                    ("§ 22 Abs. 1 StVO", True),
                    ("§ 130 GewO", False),
                    ("DGUV Vorschrift 1 § 4", False),
                ),
            ),
            FrageDef(
                text="Welchen Reibbeiwert mü erreichst du typischerweise mit einer Antirutschmatte (RH-Matte)?",
                erklaerung="Eine geeignete Antirutschmatte hebt den Reibbeiwert auf rund 0,6 — die "
                "Sicherungswirkung verdoppelt sich gegenüber Holz auf Holz (mü rund 0,2 bis 0,3).",
                optionen=_opts(
                    ("Rund 0,2", False),
                    ("Rund 0,4", False),
                    ("Rund 0,6", True),
                    ("Rund 1,0", False),
                ),
            ),
            FrageDef(
                text="Worin unterscheiden sich Niederzurrung und Direktsicherung?",
                erklaerung="Bei der Niederzurrung wirkt die Sicherung kraftschlüssig über Reibung "
                "(Gurt drückt Ladung auf die Pritsche). Bei der Direktsicherung geht die Kraft direkt "
                "durch den Gurt in den Zurrpunkt — formschlüssig.",
                optionen=_opts(
                    ("Niederzurrung wirkt durch Reibung, Direktsicherung leitet die Kraft direkt in den Zurrpunkt", True),
                    ("Niederzurrung ist nur für leichte Ladung, Direktsicherung nur für schwere", False),
                    ("Niederzurrung ist im LKW verboten, Direktsicherung Pflicht", False),
                    ("Es gibt keinen technischen Unterschied", False),
                ),
            ),
            FrageDef(
                text="Welche drei Rollen bilden die Verantwortungs-Trias bei der Ladungssicherung?",
                erklaerung="Verlader (verlädt), Verfrachter (transportiert) und Fahrzeugführer "
                "(fährt) haften nebeneinander — alle drei können Bußgeld und Punkte bekommen.",
                optionen=_opts(
                    ("Geschäftsführer, Betriebsrat, Sicherheitsbeauftragter", False),
                    ("Verlader, Verfrachter, Fahrzeugführer", True),
                    ("Hersteller, Spediteur, Kunde", False),
                    ("Fahrer, Versicherung, TÜV", False),
                ),
            ),
            FrageDef(
                text="Welcher Paragraf belegt die Geschäftsführung bei Aufsichtspflichtverletzung mit Bußgeld bis 1 Mio. Euro?",
                erklaerung="§ 130 OWiG (Ordnungswidrigkeitengesetz) sanktioniert Aufsichtspflicht"
                "verletzungen in Betrieben — fehlt dokumentierte Unterweisung und Kontrolle, haftet "
                "die Leitung mit.",
                optionen=_opts(
                    ("§ 22 StVO", False),
                    ("§ 130 OWiG", True),
                    ("§ 5 ArbSchG", False),
                    ("§ 280 BGB", False),
                ),
            ),
            FrageDef(
                text="Du sollst eine EUR-Palette mit 800 kg Maschinenteilen auf eine LKW-Pritsche laden. Was tust du zuerst?",
                erklaerung="Pritsche prüfen (sauber, trocken) und Antirutschmatte legen — beides ist "
                "die Grundlage für einen hohen Reibbeiwert und damit für die Wirksamkeit der "
                "Niederzurrung.",
                optionen=_opts(
                    ("Sofort die Palette mit dem Stapler aufsetzen", False),
                    ("Pritsche auf Sauberkeit prüfen und Antirutschmatte legen", True),
                    ("Zwei Gurte griffbereit auflegen, Reihenfolge ist sekundär", False),
                    ("Den Fahrer fragen, wie viele Gurte er braucht", False),
                ),
            ),
            FrageDef(
                text="Du bemerkst, dass ein Zurrgurt einen Riss hat. Was tust du?",
                erklaerung="Beschädigte Gurte sind sofort auszusondern (DGUV Vorschrift 70 § 37 i. V. "
                "m. DIN EN 12195-2). Reparatur oder 'noch eine Tour' ist verboten — der Gurt geht in "
                "den Müll, ein neuer wird benutzt.",
                optionen=_opts(
                    ("Den Gurt einmal noch verwenden und danach entsorgen", False),
                    ("Den Gurt sofort aussondern und einen neuen verwenden", True),
                    ("Den Riss mit Klebeband sichern und benutzen", False),
                    ("Den Gurt umdrehen, dann ist der Riss auf der unbelasteten Seite", False),
                ),
            ),
            FrageDef(
                text="Du bist Verlader und der Fahrer drückt, weil er los muss. Du bist dir aber unsicher, ob die Ladung hält. Was ist richtig?",
                erklaerung="Als Verlader haftest du mit (§ 412 HGB i. V. m. § 22 StVO). Wenn du eine "
                "unsichere Ladung durchwinkst, kann das Bußgeld bis 525 Euro für dich persönlich "
                "bedeuten — Zeitdruck ist keine Rechtfertigung.",
                optionen=_opts(
                    ("Den Fahrer fahren lassen, ab Pritsche ist es sein Problem", False),
                    ("Den Vorgang stoppen, Schichtleitung holen, erst bei sicherer Ladung quittieren", True),
                    ("Im Frachtbrief notieren, dass die Ladung 'auf Risiko des Fahrers' geht", False),
                    ("Den Fahrer einen Disclaimer unterschreiben lassen", False),
                ),
            ),
            FrageDef(
                text="Du verlädst Stahlrohr-Bunde längs auf einen LKW. Welche Sicherung ist Pflicht?",
                erklaerung="Rollende Lasten (Rohre, Coils) brauchen Formschluss durch Keile oder "
                "Sperrbalken plus zusätzliche Direktsicherung. Niederzurrung allein reicht nicht, "
                "weil der Gurt das Rollen nicht aufhalten kann.",
                optionen=_opts(
                    ("Vier Niederzurrgurte reichen, Antirutschmatte optional", False),
                    ("Keile gegen Rollen plus Direktsicherung, zusätzlich Antirutschmatten", True),
                    ("Nur eine Antirutschmatte unterlegen", False),
                    ("Die Bunde quer statt längs stellen, dann braucht es keine Sicherung", False),
                ),
            ),
            FrageDef(
                text="Du fährst eine erste längere Strecke nach dem Beladen. Was musst du nach rund 50 km tun?",
                erklaerung="Ladung setzt sich auf den ersten Kilometern, Gurte werden locker. VDI 2700 "
                "und DGUV V70 fordern eine Kontrolle und ggf. Nachspannen nach kurzer Fahrtstrecke und "
                "an jeder Pause.",
                optionen=_opts(
                    ("Nichts — die Gurte halten von selbst", False),
                    ("Anhalten, Gurte kontrollieren und nachspannen", True),
                    ("Erst am Ziel kontrollieren", False),
                    ("Nur kontrollieren, wenn die Ladung sichtbar verrutscht ist", False),
                ),
            ),
            FrageDef(
                text="Die Polizei hält dich an und stellt fest, dass deine LKW-Ladung unzureichend gesichert war, aber kein Schaden entstand. Welches Bußgeld droht dem Fahrer typisch?",
                erklaerung="Tatbestandskatalog 2025: nicht ausreichend gesicherte Ladung beim LKW liegt "
                "bei 60 Euro plus 1 Punkt — mit Gefährdung steigt es auf 75-100 Euro plus 1 Punkt.",
                optionen=_opts(
                    ("10 Euro, keine Punkte", False),
                    ("60 Euro plus 1 Punkt", True),
                    ("500 Euro plus Fahrverbot", False),
                    ("Verwarnung ohne weitere Folgen", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage über Antirutschmatten ist richtig?",
                erklaerung="Antirutschmatten erhöhen den Reibbeiwert deutlich (auf ca. 0,6) und "
                "reduzieren damit die Anzahl der nötigen Gurte — sie ersetzen aber nicht die Zurrung, "
                "sondern multiplizieren ihre Wirkung.",
                optionen=_opts(
                    ("Sie ersetzen die Zurrgurte vollständig", False),
                    ("Sie erhöhen den Reibbeiwert und reduzieren die nötige Gurt-Anzahl", True),
                    ("Sie sind nur für PKW-Transport vorgeschrieben", False),
                    ("Sie wirken nur bei trockenem Wetter", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur Gewichtsverteilung auf der Pritsche ist richtig?",
                erklaerung="Schwere Ladung gehört nach unten und zentriert über die Achsen — "
                "asymmetrische Verteilung gefährdet die Achslasten und das Fahrverhalten.",
                optionen=_opts(
                    ("Schwere Ladung nach oben, damit unten Platz für mehr ist", False),
                    ("Schwere Ladung nach unten und zentriert über die Achsen", True),
                    ("Schwere Ladung immer ganz hinten, weil dort die meiste Stabilität ist", False),
                    ("Die Verteilung spielt keine Rolle, solange die zulässige Gesamtmasse stimmt", False),
                ),
            ),
            FrageDef(
                text="Du siehst am Sattel-LKW eines Kollegen einen Gurt, der über eine scharfe Kante einer Maschinenkomponente läuft — ohne Kantenschoner. Was ist falsch?",
                erklaerung="Ohne Kantenschoner kann der Gurt schon bei normaler Vorspannung einreißen "
                "und versagt in der Fahrt. DGUV V70 § 37 und VDI 2700 schreiben Kantenschoner an "
                "scharfen Kanten vor.",
                optionen=_opts(
                    ("Nichts — Gurte halten viel aus", False),
                    ("Der Gurt kann an der Kante einreißen, ein Kantenschoner ist Pflicht", True),
                    ("Die Spannung ist zu hoch, der Gurt muss gelockert werden", False),
                    ("Es ist eine Ordnungswidrigkeit nur dann, wenn ein Unfall passiert", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet die Abkürzung LC auf dem Etikett eines Zurrgurts?",
                erklaerung="LC = Lashing Capacity, die zulässige Zurrkraft des Gurts in daN. Sie ist "
                "die Bemessungsgrundlage für die Direktsicherung und steht zusammen mit der STF "
                "(Standard Tension Force, Vorspannkraft bei Niederzurrung) auf dem Etikett.",
                optionen=_opts(
                    ("Lashing Capacity — die zulässige Zurrkraft in daN", True),
                    ("Load Class — eine Brandklasse", False),
                    ("Length Coefficient — die Länge in Metern", False),
                    ("Local Code — der Herstellerort", False),
                ),
            ),
            FrageDef(
                text="Eine EUR-Palette mit 1.000 kg steht auf nackter Holzpritsche (Reibbeiwert 0,2). Wie viele Niederzurrgurte (STF 350 daN) brauchst du grob, um die 0,8 g nach vorne zu sichern?",
                erklaerung="Faustregel: nötige Vorspannkraft = (cx - mü) / mü * Ladungsgewicht. "
                "Bei cx=0,8, mü=0,2 und 1.000 kg ergeben sich rund 3.000 daN Vorspannkraft — geteilt "
                "durch 350 daN STF und Faktor 2 (zwei Gurthälften) sind das etwa vier bis fünf "
                "Gurte. Mit Antirutschmatte (mü 0,6) reichen ein bis zwei.",
                optionen=_opts(
                    ("Einer reicht", False),
                    ("Vier bis fünf, mit Antirutschmatte ein bis zwei", True),
                    ("Zwölf", False),
                    ("Niederzurrung wirkt hier gar nicht", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Aussagen ist FALSCH?",
                erklaerung="Niederzurrung ist nicht 'immer ausreichend' — bei rollenden Lasten oder "
                "sehr glatter Pritsche reicht sie nicht. Dann ist Direktsicherung oder Formschluss "
                "(Keile, Sperrbalken) Pflicht.",
                optionen=_opts(
                    ("Der Fahrer muss vor Fahrtantritt die Ladungssicherung prüfen", False),
                    ("Niederzurrung ist immer ausreichend, egal welche Ladung", True),
                    ("Antirutschmatten erhöhen den Reibbeiwert", False),
                    ("Der Verlader haftet mit nach § 412 HGB", False),
                ),
            ),
            FrageDef(
                text="Du quittierst als Verlader den Frachtbrief mit 'Ladung gesichert'. Welche Bedeutung hat das?",
                erklaerung="Mit der Unterschrift bestätigst du, dass die Ladung beförderungssicher "
                "verstaut ist. Das ist die Dokumentation deiner Pflicht aus § 412 HGB und kann im "
                "Streitfall vor Gericht als Beweis dienen — eine unsichere Ladung darfst du also "
                "nicht quittieren.",
                optionen=_opts(
                    ("Es ist nur eine Formalität ohne rechtliche Bedeutung", False),
                    ("Du bestätigst rechtsverbindlich die beförderungssichere Verladung", True),
                    ("Es entlastet den Fahrer von jeglicher Verantwortung", False),
                    ("Es gilt nur intern und hat keine Außenwirkung", False),
                ),
            ),
        ),
    ),
    # ------------------------------------------------------------------- #18
    KursDef(
        titel="Exportkontrolle & Sanktionen",
        beschreibung="Pflichtschulung für Versand/Vertrieb nach AWG + EU-Dual-Use-VO 2021/821. Embargos, Sanktionslisten-Prüfung, Dual-Use-Güter.",
        gueltigkeit_monate=24,
        module=(
            ModulDef(
                titel="Wer ist betroffen, was ist Exportkontrolle?",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Exportkontrolle klingt nach Speditions-Bürokratie, ist aber harte Strafrechts-Materie. "
                    "Wer ein CNC-Bearbeitungszentrum, einen Hochfrequenz-Sensor oder eine selbst geschriebene "
                    "Verschlüsselungs-Software an den falschen Empfänger schickt, riskiert nicht nur "
                    "Bußgelder für die Firma, sondern bis zu zehn Jahre Haft persönlich. Betroffen ist "
                    "nicht nur der Vertrieb, sondern jede Person, die über Versand, technische Auskünfte "
                    "oder Ersatzteil-Lieferungen mitentscheidet.\n\n"
                    "Du lernst in diesem Modul, was Exportkontrolle eigentlich abdeckt, welche Behörden "
                    "die Aufsicht führen und warum auch ein scheinbar harmloser Schraubenversand an einen "
                    "Maschinenbau-Kunden in Drittland eine Genehmigung brauchen kann.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **Außenwirtschaftsgesetz (AWG)** — §§ 4-6 Ermächtigung zu Beschränkungen, §§ 17-19 Straf- und Bußgeldvorschriften\n"
                    "- **Außenwirtschaftsverordnung (AWV)** — §§ 7-10 Beschränkungen einzelner Rechtsgeschäfte, § 76 Ordnungswidrigkeiten\n"
                    "- **EU-Dual-Use-Verordnung 2021/821** — direkt geltendes EU-Recht, kontrolliert die Ausfuhr von Gütern mit doppeltem Verwendungszweck\n"
                    "- **EU-Sanktionsverordnungen** — z.B. VO 269/2014 und 833/2014 (Russland), VO 2580/2001 (Terrorismus), länderspezifische Embargos\n"
                    "- Zuständige Behörde Deutschland: **BAFA** (Bundesamt für Wirtschaft und Ausfuhrkontrolle), Eschborn\n\n"
                    "## Was musst du wissen\n\n"
                    "Exportkontrolle bedeutet: bestimmte Güter, Technologien und Dienstleistungen dürfen "
                    "nicht ohne staatliche Genehmigung ins Ausland gehen. Sie hat drei große Säulen:\n\n"
                    "1. **Gütergebundene Kontrolle** — bestimmte Güter sind 'gelistet' (Ausfuhrliste, EU-Dual-Use-Anhang I) und immer genehmigungspflichtig\n"
                    "2. **Empfängergebundene Kontrolle** — Lieferungen an gelistete Personen, Organisationen oder Länder (Embargos, Sanktionslisten) sind verboten oder genehmigungspflichtig\n"
                    "3. **Verwendungsgebundene Kontrolle** — auch nicht gelistete Güter können bei militärischer oder proliferationsrelevanter Endverwendung kontrollpflichtig werden ('Catch-all')\n\n"
                    "Der Begriff *Ausfuhr* meint nicht nur den klassischen LKW oder Container. Kontrolliert "
                    "sind auch: Technologie-Transfer per E-Mail, Cloud-Upload, Remote-Wartung, Mitnahme "
                    "eines Laptops auf eine Dienstreise, ein technisches Gespräch mit einem ausländischen "
                    "Kollegen auf der Messe. Das nennt sich *technische Unterstützung* und fällt unter "
                    "§ 49 ff. AWV.\n\n"
                    "Im Industrie-Mittelstand sind besonders häufig betroffen:\n\n"
                    "- Werkzeugmaschinen mit vier oder mehr simultan gesteuerten Achsen\n"
                    "- Hochpräzisions-Mess- und Prüfgeräte (z.B. Koordinaten-Messmaschinen)\n"
                    "- Halbleiter-Fertigungstechnik, Reinraum-Komponenten\n"
                    "- Drohnen-Technologie, hochfeste Werkstoffe, Spezial-Sensorik\n"
                    "- Kryptografische Software und Hardware\n"
                    "- Frequenzwandler, Hochleistungs-Laser, Vakuum-Pumpen\n\n"
                    "Auch *Brokering* (Vermittlung) und *Durchfuhr* fallen unter die Verordnung. Wenn ein "
                    "deutscher Vertriebler einen Deal zwischen einem US-Hersteller und einem Kunden im "
                    "Iran einfädelt, ist er ohne deutsche Genehmigung strafbar — auch wenn die Ware nie "
                    "Deutschland berührt.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Bei jedem Auftrag mit Auslandsbezug die Exportkontroll-Prüfung anstoßen, bevor du eine Lieferzusage gibst\n"
                    "2. Die internen Prüfungsschritte (Sanktionslisten-Prüfung, Güterklassifizierung, Endverwendung) gemeinsam mit dem oder der Exportkontroll-Beauftragten dokumentieren\n"
                    "3. Bei Unsicherheit über Güterstatus oder Empfänger immer rückfragen, niemals 'auf eigene Faust' entscheiden\n"
                    "4. Auch interne Technologie-Transfers (E-Mail-Anhang, Cloud-Freigabe, Fernzugriff) als mögliche Ausfuhr behandeln\n"
                    "5. Auf Anzeichen achten, die auf verdeckte Endverwendung oder Umgehung hindeuten (siehe Catch-all)\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein mittelständischer Werkzeugmaschinen-Bauer aus Baden-Württemberg erhält eine "
                    "Anfrage aus Kasachstan über zwei 5-Achs-Fräszentren. Der Vertriebsleiter ist "
                    "begeistert: hoher Auftragswert, neuer Kunde, schnelle Lieferung gewünscht. Der "
                    "Exportkontroll-Beauftragte prüft und stellt fest: die Maschinen fallen unter Position "
                    "*2B001* der EU-Dual-Use-Liste (Werkzeugmaschinen mit vier oder mehr Achsen-Simultan"
                    "steuerung). Genehmigungspflicht beim BAFA. Die Endverbleibs-Erklärung des Kunden "
                    "weist als Verwender ein 'Forschungsinstitut' aus, dessen Adresse identisch ist mit "
                    "einem in der EU-Sanktionsliste geführten russischen Rüstungs-Konzern. Das Geschäft "
                    "wird abgelehnt. Ohne diese Prüfung hätte der Vertriebsleiter persönlich eine "
                    "Haftstrafe nach § 18 AWG riskiert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf das Außenwirtschaftsgesetz (AWG, Stand 2025) und die "
                    "Außenwirtschaftsverordnung (AWV), die EU-Dual-Use-Verordnung (EU) 2021/821, "
                    "sowie die Informationsangebote des Bundesamtes für Wirtschaft und Ausfuhrkontrolle "
                    "(BAFA, bafa.de)."
                ),
            ),
            ModulDef(
                titel="Sanktionslisten-Prüfung",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Sanktionslisten sind keine 'nice to have'-Compliance, sondern strafbewehrte Pflicht. "
                    "Wer mit einer gelisteten Person, einem gelisteten Unternehmen oder einer Tarn-Firma "
                    "Geschäftsbeziehungen unterhält, macht sich strafbar — auch bei grober Fahrlässigkeit. "
                    "Seit der AWG-Verschärfung 2024 entfällt die frühere Zwei-Tage-Karenz: neue Listungen "
                    "gelten ab dem Moment ihrer Veröffentlichung im Amtsblatt der EU.\n\n"
                    "Du lernst, welche Listen es gibt, wer wann zu prüfen ist und warum 'haben wir mal vor "
                    "drei Monaten gemacht' nicht reicht.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **VO (EG) 2580/2001** — Terrorismus-Sanktionen, EU-Liste der gelisteten Personen und Gruppen\n"
                    "- **VO (EU) 269/2014** + **833/2014** — Russland-Sanktionen seit 2014, massiv erweitert ab 2022\n"
                    "- **VO (EU) 881/2002** — Al-Qaida- und ISIL-Sanktionen (umgesetzt aus UN-Resolutionen)\n"
                    "- **§ 18 AWG** — Strafvorschriften: Verstoß gegen Bereitstellungs- und Verfügungsverbote, drei Monate bis fünf Jahre Haft, in besonders schweren Fällen sechs Monate bis zehn Jahre\n"
                    "- **§ 19 AWG** — fahrlässige Begehung, bis drei Jahre Haft oder Geldstrafe\n"
                    "- **§ 30 OWiG** — Verbandsgeldbuße gegen das Unternehmen, bis zehn Millionen Euro plus Gewinnabschöpfung\n\n"
                    "## Was musst du wissen\n\n"
                    "Eine *Sanktionslistenprüfung* (oft SaP genannt) gleicht jeden Geschäftspartner — "
                    "Kunde, Lieferant, Spediteur, Bankverbindung, technischer Ansprechpartner — gegen die "
                    "konsolidierten EU- und UN-Sanktionslisten ab. Erfasst werden Name, Adresse, "
                    "Geburtsdatum, gegebenenfalls Schiff/Flugzeug oder Tarnname.\n\n"
                    "Wichtig ist die Vollständigkeit der zu prüfenden Listen:\n\n"
                    "| Liste | Inhalt | Quelle |\n"
                    "|---|---|---|\n"
                    "| EU-Finanz-Sanktionsliste (CFSP) | konsolidierte Liste aller EU-Sanktionen | EU-Sanctions Map / FSF-Datenbank |\n"
                    "| UN Consolidated List | UN-Sicherheitsrats-Sanktionen | un.org |\n"
                    "| US OFAC SDN List | US-Sanktionen mit extraterritorialer Wirkung | treasury.gov |\n"
                    "| UK Sanctions List | nach Brexit eigenständig | gov.uk |\n"
                    "| Embargo-Länderlisten | Iran, Nordkorea, Syrien, Belarus, Russland u.a. | BAFA-Übersicht |\n\n"
                    "Eine US-Liste wie die OFAC SDN ist für deutsche Firmen nicht direkt bindend, kann "
                    "aber bei US-Dollar-Zahlungen oder US-Hardware-Komponenten über das *Secondary "
                    "Sanctions*-Regime treffen. Banken kündigen Konten oder blockieren Zahlungen.\n\n"
                    "Die Prüfung muss in drei Situationen erfolgen:\n\n"
                    "- **Initial** bei der Anlage jedes neuen Geschäftspartners\n"
                    "- **Kontinuierlich**, also Re-Prüfung des gesamten Stammdaten-Bestands gegen jede Listen-Aktualisierung\n"
                    "- **Anlassbezogen** vor jeder konkreten Transaktion, Lieferung oder Zahlung\n\n"
                    "Auch *mittelbare* Beziehungen sind kontrolliert: gehört eine nicht gelistete Firma "
                    "zu mehr als 50 Prozent einer gelisteten Person, ist sie ebenfalls gesperrt. Das "
                    "macht die Prüfung in komplexen Konzern-Strukturen schwierig — kommerzielle "
                    "Datenbanken lösen Beteiligungs-Ketten auf.\n\n"
                    "Ein **Treffer** ist nicht automatisch ein Verbot, aber ein 'roter Halt'. Bevor "
                    "irgendetwas weitergeht, klärt der oder die Exportkontroll-Beauftragte, ob es sich "
                    "um einen echten Treffer, eine Namensgleichheit oder eine zulässige Ausnahme handelt.\n\n"
                    "## Was musst du tun\n\n"
                    "1. Bei jedem neuen Geschäftspartner sofort die Sanktionslisten-Prüfung anstoßen, bevor Angebot oder Bestellbestätigung rausgehen\n"
                    "2. Niemals 'die Prüfung lief schon mal' akzeptieren — die Liste hat sich seitdem geändert\n"
                    "3. Bei jedem Treffer oder Verdachtsfall sofort an Exportkontrolle eskalieren, nichts versenden, keine Zahlung freigeben\n"
                    "4. Auch indirekte Beteiligte (Spediteur, Empfangs-Bank, technischer Partner) in die Prüfung einbeziehen\n"
                    "5. Treffer und Prüfungsergebnisse dokumentiert ablegen, mindestens fünf Jahre archivieren\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Kunststoff-Verarbeiter im Sauerland liefert seit Jahren Spezial-Kabelbinder an "
                    "einen langjährigen Händler in Tschechien. Im März 2025 wird der Händler in die "
                    "EU-Russland-Sanktionsliste aufgenommen, weil er als Strohmann für Umgehungslieferungen "
                    "identifiziert wurde. Der Buchhaltung fällt das nicht auf, weil der Stammdaten-Bestand "
                    "seit 2019 nicht mehr neu gegen die Listen abgeglichen wurde. Drei Tage nach Listung "
                    "geht eine reguläre Lieferung raus. Die Zollkontrolle in Frankfurt stoppt die Sendung. "
                    "Es folgen Hausdurchsuchung, Ermittlungsverfahren gegen den Geschäftsführer wegen "
                    "fahrlässiger Begehung nach § 19 AWG, Verbandsgeldbuße gegen die GmbH. Eine "
                    "automatisierte tägliche SaP hätte den Vorfall verhindert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf VO (EG) 2580/2001, VO (EU) 269/2014 und 833/2014, die "
                    "konsolidierten EU-Sanktionslisten (sanctionsmap.eu) sowie auf §§ 18-19 AWG (Stand 2025) "
                    "und die Embargo-Übersichten des BAFA (bafa.de)."
                ),
            ),
            ModulDef(
                titel="Dual-Use-Güter & Genehmigungspflicht",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Dual-Use-Güter sind Güter, Software und Technologien, die sowohl zivil als auch "
                    "militärisch oder proliferationsrelevant verwendet werden können. Ein typisches "
                    "Beispiel: eine Werkzeugmaschine zur Herstellung von Auto-Motorblocken, mit der man "
                    "aber auch Zentrifugen-Bauteile für Uran-Anreicherung fertigen könnte. Genau dort "
                    "setzt die EU-Dual-Use-VO 2021/821 an.\n\n"
                    "Du lernst, wie die Güterliste aufgebaut ist, was 'Catch-all' bedeutet und wie eine "
                    "Ausfuhrgenehmigung beim BAFA praktisch abläuft.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **EU-Dual-Use-VO (EU) 2021/821** — direkt anwendbares EU-Recht seit September 2021, letzte große Anhang-Aktualisierung November 2025 (VO 2025/2003)\n"
                    "- **Anhang I der Dual-Use-VO** — Güterliste mit zehn Kategorien (0 bis 9)\n"
                    "- **Anhang IV** — besonders sensible Güter, EU-interne Verbringung genehmigungspflichtig\n"
                    "- **Artikel 4 EU-Dual-Use-VO** — Catch-all bei militärischer Endverwendung, Massenvernichtungswaffen, Menschenrechtsverletzungen\n"
                    "- **§ 8 AWV** — nationale Ergänzungen der deutschen Ausfuhrliste (Teil I Abschnitt A)\n"
                    "- **§ 18 AWG** — Strafbarkeit der ungenehmigten Ausfuhr\n\n"
                    "## Was musst du wissen\n\n"
                    "Anhang I der Dual-Use-VO ist in zehn Kategorien gegliedert. Jede Kategorie zerfällt "
                    "in fünf Unterkategorien (A bis E):\n\n"
                    "| Kategorie | Inhalt |\n"
                    "|---|---|\n"
                    "| 0 | Kerntechnik und kerntechnische Anlagen |\n"
                    "| 1 | Besondere Werkstoffe und zugehörige Ausrüstung |\n"
                    "| 2 | Werkstoffbearbeitung (z.B. Mehrachs-Werkzeugmaschinen) |\n"
                    "| 3 | Allgemeine Elektronik |\n"
                    "| 4 | Rechner (Hochleistungs-Computing) |\n"
                    "| 5 | Telekommunikation und Informationssicherheit (Kryptografie) |\n"
                    "| 6 | Sensoren und Laser |\n"
                    "| 7 | Luftfahrt-Elektronik und Navigation |\n"
                    "| 8 | Meeres- und Schiffstechnik |\n"
                    "| 9 | Luft- und Raumfahrt sowie Antriebssysteme |\n\n"
                    "Die Unterkategorien sind: A Anlagen/Ausrüstung, B Prüf- und Produktionseinrichtungen, "
                    "C Werkstoffe, D Datenverarbeitungsprogramme, E Technologie. Ein Listenposten wie "
                    "*2B001* steht also für: Kategorie 2 (Werkstoffbearbeitung), B (Prüf-/Produktions"
                    "ausrüstung), laufende Nummer 001 (mehrachsige Werkzeugmaschinen).\n\n"
                    "Die Klassifizierung eines konkreten Produkts geschieht über die *ECCN* (Export "
                    "Control Classification Number). Der Hersteller liefert die Klassifizierung in den "
                    "technischen Datenblättern; im Zweifel hilft eine Auskunft des BAFA (sogenannter "
                    "Null-Bescheid oder Auskunft zur Genehmigungspflicht).\n\n"
                    "Das **Catch-all-Prinzip** nach Artikel 4 Dual-Use-VO ist die wichtigste 'Falle'. "
                    "Auch ein nicht gelistetes Gut ist genehmigungspflichtig, wenn du weißt oder vom "
                    "BAFA unterrichtet wirst, dass es bestimmt ist für:\n\n"
                    "- die Entwicklung oder Herstellung von Massenvernichtungs- oder Trägerwaffen\n"
                    "- eine militärische Endverwendung in einem Embargo-Land\n"
                    "- die Verletzung von Menschenrechten (z.B. Überwachungs-Software, seit 2021 in der VO verankert)\n\n"
                    "'Wissen' heißt nicht nur sichere Kenntnis, sondern auch positive Anzeichen (*red "
                    "flags*): unüblicher Kunde, ungewöhnlicher Endverwender, untypische Liefer-Route, "
                    "Bar-Vorauszahlung, Kunde will keine Endverbleibs-Erklärung unterschreiben.\n\n"
                    "Genehmigungsarten beim BAFA, in zunehmender Aufwand-Stufe:\n\n"
                    "- **Allgemeine Genehmigung (AGG)** — pauschale Erlaubnis für bestimmte Güter/Länder, nur Registrierung und Meldung nötig\n"
                    "- **Sammelgenehmigung** — für wiederkehrende Geschäfte mit bekannten Endverwendern\n"
                    "- **Einzelgenehmigung** — für konkrete Lieferung, Bearbeitungszeit Wochen bis Monate\n\n"
                    "## Was musst du tun\n\n"
                    "1. Vor jeder Auslandslieferung prüfen, ob das Produkt eine Listenposition (Dual-Use-Anhang I oder Ausfuhrliste Teil I A) hat\n"
                    "2. Bei jedem Auftrag eine **Endverbleibs-Erklärung** vom Kunden einholen, in der Endverwender, Endverwendung und Re-Exportverbot bestätigt werden\n"
                    "3. Auf Catch-all-Anzeichen achten (military end-use, unüblicher Endverwender, Drittland-Tarnung) und sofort Exportkontrolle informieren\n"
                    "4. Vor Lieferung prüfen, ob eine Allgemeine Genehmigung passt oder Einzelgenehmigung beantragt werden muss\n"
                    "5. Niemals Lieferungen 'splitten', um unter Schwellenwerte zu kommen — das ist Umgehungs-Tatbestand und strafbar\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Sensorik-Hersteller aus Bayern liefert hochempfindliche Beschleunigungs-Sensoren "
                    "an einen türkischen Drohnen-Bauer. Die Sensoren fallen knapp unter die Anhang-I-"
                    "Schwelle der Kategorie 7 (Navigations-Sensorik). Der Vertrieb sieht keine "
                    "Genehmigungspflicht. Wenige Wochen später berichtet die Presse, dass der türkische "
                    "Kunde militärische Drohnen baut, die in einem Konflikt eingesetzt werden. Damit "
                    "greift Catch-all: positive Anzeichen für militärische Endverwendung hätten beachtet "
                    "werden müssen. Das BAFA leitet Ermittlungen ein. Der Vertriebsleiter haftet persönlich, "
                    "die Firma riskiert Verbandsgeldbuße und Ausschluss von öffentlichen Aufträgen. "
                    "Hier wäre eine *Catch-all-Anfrage* beim BAFA der richtige Weg gewesen: schriftliche "
                    "Anfrage, ob Genehmigungspflicht besteht, mit verbindlicher Antwort innerhalb weniger "
                    "Wochen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf die EU-Dual-Use-VO (EU) 2021/821 inklusive Anhang I (zuletzt "
                    "geändert durch Delegierte VO (EU) 2025/2003 vom 8. September 2025), das BAFA-"
                    "Merkblatt *Die neue EU-Dual-Use-Verordnung* (bafa.de) sowie die deutsche Ausfuhrliste "
                    "nach § 8 AWV."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Behörde ist in Deutschland für Exportkontroll-Genehmigungen zuständig?",
                erklaerung="Das BAFA (Bundesamt für Wirtschaft und Ausfuhrkontrolle) in Eschborn ist die "
                "zentrale Genehmigungsbehörde für Dual-Use- und Rüstungsgüter-Ausfuhren.",
                optionen=_opts(
                    ("Bundesamt für Verfassungsschutz (BfV)", False),
                    ("Bundesamt für Wirtschaft und Ausfuhrkontrolle (BAFA)", True),
                    ("Zollkriminalamt (ZKA)", False),
                    ("Bundesnetzagentur (BNetzA)", False),
                ),
            ),
            FrageDef(
                text="Welches Strafmaß droht in besonders schweren Fällen nach § 18 AWG?",
                erklaerung="In besonders schweren Fällen sieht § 18 Abs. 7 AWG eine Freiheitsstrafe "
                "von sechs Monaten bis zu zehn Jahren vor.",
                optionen=_opts(
                    ("Bis zu 1 Jahr Haft oder Geldstrafe", False),
                    ("Bis zu 3 Jahre Haft", False),
                    ("Sechs Monate bis 10 Jahre Haft", True),
                    ("Ausschließlich Bußgeld bis 100.000 Euro", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet der Begriff 'Dual-Use-Gut'?",
                erklaerung="Dual-Use-Güter sind Güter, Software und Technologien mit doppeltem "
                "Verwendungszweck — sowohl zivil als auch militärisch oder proliferationsrelevant einsetzbar.",
                optionen=_opts(
                    ("Ein Gut, das in zwei verschiedene Länder geliefert wird", False),
                    ("Ein Gut mit ziviler UND möglicher militärischer Verwendung", True),
                    ("Ein Gut, das zwei Genehmigungen braucht", False),
                    ("Ein Gut, das zwei Mal pro Jahr verschickt wird", False),
                ),
            ),
            FrageDef(
                text="Wie viele Kategorien (0 bis ?) hat Anhang I der EU-Dual-Use-Verordnung?",
                erklaerung="Anhang I gliedert sich in zehn Kategorien, nummeriert von 0 (Kerntechnik) "
                "bis 9 (Luft-/Raumfahrt und Antriebssysteme).",
                optionen=_opts(
                    ("Fünf Kategorien (0-4)", False),
                    ("Zehn Kategorien (0-9)", True),
                    ("Zwanzig Kategorien (0-19)", False),
                    ("Drei Kategorien (A, B, C)", False),
                ),
            ),
            FrageDef(
                text="Was beschreibt das sogenannte 'Catch-all'-Prinzip nach Artikel 4 Dual-Use-VO?",
                erklaerung="Catch-all macht auch nicht gelistete Güter genehmigungspflichtig, sobald "
                "Anhaltspunkte für militärische Endverwendung, MVW-Bezug oder Menschenrechtsverletzungen vorliegen.",
                optionen=_opts(
                    ("Alle Güter, die im Anhang I aufgelistet sind, brauchen Genehmigung", False),
                    ("Auch nicht gelistete Güter werden genehmigungspflichtig bei kritischer Endverwendung", True),
                    ("Der Zoll kann jede Sendung beliebig stoppen", False),
                    ("Eine Sammelgenehmigung deckt alle Lieferungen eines Jahres ab", False),
                ),
            ),
            FrageDef(
                text="Wann muss eine Sanktionslisten-Prüfung neuer EU-Listungen erfolgen?",
                erklaerung="Seit der AWG-Verschärfung 2024 gilt: neue Listungen sind ab Veröffentlichung "
                "im Amtsblatt der EU sofort bindend, die früheren zwei Karenztage entfallen.",
                optionen=_opts(
                    ("Innerhalb von zwei Werktagen nach Veröffentlichung", False),
                    ("Sofort ab Veröffentlichung im EU-Amtsblatt", True),
                    ("Erst nach amtlicher Zustellung an das Unternehmen", False),
                    ("Einmal pro Quartal reicht aus", False),
                ),
            ),
            FrageDef(
                text="Welche EU-Verordnung regelt die Russland-bezogenen Sanktionen seit 2014?",
                erklaerung="Die VO (EU) 269/2014 (personenbezogene Sanktionen) und 833/2014 "
                "(sektorale Wirtschaftssanktionen) sind die Kernverordnungen, seit 2022 stark erweitert.",
                optionen=_opts(
                    ("VO (EU) 269/2014 und 833/2014", True),
                    ("VO (EG) 2580/2001", False),
                    ("VO (EU) 2021/821", False),
                    ("VO (EU) 881/2002", False),
                ),
            ),
            FrageDef(
                text="Du arbeitest im Vertrieb. Eine Anfrage aus dem Iran erreicht dich per E-Mail. Was tust du?",
                erklaerung="Iran-Geschäfte unterliegen umfangreichen Embargos. Eigenmächtige Lieferzusagen "
                "sind strafbar — die Anfrage gehört sofort an die Exportkontroll-Funktion.",
                optionen=_opts(
                    ("Direkt ein Angebot schicken, weil der Kunde Eile signalisiert", False),
                    ("Anfrage ignorieren, Löschen, nichts dokumentieren", False),
                    ("An die Exportkontroll-Funktion eskalieren und Prüfung anstoßen", True),
                    ("Auf Englisch höflich absagen, ohne den Vorgang zu melden", False),
                ),
            ),
            FrageDef(
                text="Du sollst einer ausländischen Kollegin per Cloud-Link technische Konstruktions-Zeichnungen eines kontrollierten Bauteils schicken. Was gilt?",
                erklaerung="Auch elektronische Technologie-Transfers (Cloud, E-Mail, Remote-Zugriff) sind "
                "exportkontrollrechtliche Ausfuhren und genehmigungspflichtig.",
                optionen=_opts(
                    ("Cloud-Links sind keine Ausfuhr, weil keine physische Ware bewegt wird", False),
                    ("Elektronischer Technologie-Transfer ist Ausfuhr und kann genehmigungspflichtig sein", True),
                    ("Nur bei mehr als 100 MB Datenmenge relevant", False),
                    ("Nur bei Versand per Post relevant", False),
                ),
            ),
            FrageDef(
                text="Ein Bestandskunde aus einem Drittland will eine 5-Achs-Fräse kaufen. Endverbleibs-Erklärung wird verweigert. Was machst du?",
                erklaerung="Die Verweigerung der Endverbleibs-Erklärung ist eine klassische Red-Flag. "
                "Geschäft stoppen, Exportkontrolle einschalten, dokumentieren.",
                optionen=_opts(
                    ("Liefern, weil der Kunde lange bekannt ist", False),
                    ("Geschäft stoppen, Sachverhalt an Exportkontrolle melden", True),
                    ("Eine andere, weniger empfindliche Variante anbieten", False),
                    ("Den Auftrag in zwei kleinere splitten, damit es unauffälliger läuft", False),
                ),
            ),
            FrageDef(
                text="Ein Kollege schlägt vor, einen Großauftrag in drei Teillieferungen unterhalb eines Schwellenwerts aufzuteilen. Wie reagierst du?",
                erklaerung="Das Aufsplitten zur Umgehung von Schwellenwerten ist ein eigener Umgehungs-"
                "Tatbestand nach § 18 AWG und strafbar.",
                optionen=_opts(
                    ("Gute Idee, das spart Bürokratie", False),
                    ("Lehnen ab, das wäre strafbare Umgehung; Exportkontrolle informieren", True),
                    ("Nur, wenn der Kunde sich damit einverstanden erklärt", False),
                    ("Nur, wenn die Geschäftsführung mündlich zustimmt", False),
                ),
            ),
            FrageDef(
                text="Bei der Sanktionsprüfung erscheint ein 'Treffer' für einen langjährigen Lieferanten. Was ist der erste richtige Schritt?",
                erklaerung="Ein Treffer ist ein 'roter Halt': sofort innehalten, Exportkontrolle eskalieren "
                "und klären, ob echter Treffer oder Namensgleichheit. Niemals selbst freigeben.",
                optionen=_opts(
                    ("Sofort weiterliefern, der Lieferant ist ja seit Jahren bekannt", False),
                    ("Innehalten, Exportkontrolle informieren, Prüfung dokumentieren", True),
                    ("Lieferanten anrufen und fragen, ob das stimmt", False),
                    ("Den Treffer ignorieren, wenn er erstmals erscheint", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Aussagen zur Endverbleibs-Erklärung (EVE) ist KORREKT?",
                erklaerung="Die EVE bestätigt Endverwender, Endverwendung und das Re-Exportverbot. "
                "Sie ist Bestandteil der Pflicht-Dokumentation bei kontrollierten Güter-Lieferungen.",
                optionen=_opts(
                    ("Die EVE ist eine freiwillige Höflichkeitsfloskel", False),
                    ("Die EVE bestätigt Endverwender, Endverwendung und Re-Exportverbot", True),
                    ("Die EVE ist nur bei Lieferungen über 1 Mio. Euro nötig", False),
                    ("Die EVE ersetzt die BAFA-Genehmigung", False),
                ),
            ),
            FrageDef(
                text="Ein Spediteur soll für eine Sendung beauftragt werden. Muss er auch in der Sanktionsprüfung berücksichtigt werden?",
                erklaerung="Auch indirekte Beteiligte wie Spediteure, Empfangsbanken und technische Partner "
                "müssen geprüft werden — sonst greift das Bereitstellungsverbot mittelbar.",
                optionen=_opts(
                    ("Nein, Spediteure sind keine Geschäftspartner im engeren Sinne", False),
                    ("Ja, auch indirekte Beteiligte sind zu prüfen", True),
                    ("Nur bei See-Fracht relevant", False),
                    ("Nur bei Lieferungen über EU-Außengrenzen", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu US-Sanktionen (OFAC SDN) ist korrekt?",
                erklaerung="OFAC-Listen sind für deutsche Firmen nicht direkt bindend, können aber über "
                "Secondary Sanctions Banken zur Kontosperre oder Zahlungsblockaden zwingen.",
                optionen=_opts(
                    ("OFAC-Listen sind in Deutschland direkt anwendbares Recht", False),
                    ("OFAC-Listen sind irrelevant für deutsche Firmen", False),
                    ("OFAC-Listen können über Secondary Sanctions und US-Banken treffen", True),
                    ("OFAC-Listen sind nur für US-Tochterfirmen relevant", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zur Beteiligungs-Schwelle bei gelisteten Personen stimmt?",
                erklaerung="Wenn eine gelistete Person mehr als 50 Prozent an einer Firma hält, gilt die "
                "Firma auch ohne eigene Listung als gesperrt — *50-Prozent-Regel* der EU-Sanktionen.",
                optionen=_opts(
                    ("Eine Beteiligung der gelisteten Person hat keine Auswirkungen", False),
                    ("Eine Beteiligung von mehr als 50 Prozent macht das Tochter-Unternehmen ebenfalls gesperrt", True),
                    ("Erst ab 100 Prozent Beteiligung greift die Sperre", False),
                    ("Beteiligungen sind nur bei Bank-Transaktionen relevant", False),
                ),
            ),
            FrageDef(
                text="Ein Mitarbeiter aus der Produktion erklärt auf einer Fachmesse einem ausländischen Besucher die Funktionsweise eines kontrollierten Geräts im Detail. Was liegt vor?",
                erklaerung="Mündliche oder schriftliche technische Auskunft an Ausländer über kontrollierte "
                "Technologie ist *technische Unterstützung* nach § 49 AWV und kann genehmigungspflichtig sein.",
                optionen=_opts(
                    ("Nichts, ein Messegespräch ist nie exportrechtlich relevant", False),
                    ("Eine mögliche technische Unterstützung, die genehmigungspflichtig sein kann", True),
                    ("Eine reine Marketing-Maßnahme", False),
                    ("Eine Ordnungswidrigkeit nur, wenn der Besucher die Information aufschreibt", False),
                ),
            ),
            FrageDef(
                text="Welche der folgenden Praktiken ist eine typische Compliance-Schwäche bei der Sanktionsprüfung?",
                erklaerung="Stammdaten müssen kontinuierlich gegen jede Listen-Aktualisierung neu abgeglichen "
                "werden — ein 'Einmal-Check vor Jahren' bietet keinen Schutz.",
                optionen=_opts(
                    ("Kontinuierliche Re-Prüfung des Stammdaten-Bestands", False),
                    ("Prüfung nur einmal bei Anlage des Kunden, danach nie wieder", True),
                    ("Dokumentation der Prüfungs-Ergebnisse", False),
                    ("Einbeziehung von Banken und Spediteuren", False),
                ),
            ),
            FrageDef(
                text="Du möchtest sicher wissen, ob ein Produkt unter eine Listenposition fällt. Was ist der richtige Weg?",
                erklaerung="Eine schriftliche Auskunft des BAFA (Null-Bescheid oder Auskunft zur "
                "Genehmigungspflicht) gibt verbindliche Klarheit und schützt vor Fehleinschätzungen.",
                optionen=_opts(
                    ("Auf das Bauchgefühl der Vertriebsleitung verlassen", False),
                    ("BAFA-Auskunft schriftlich einholen (Null-Bescheid)", True),
                    ("Bei einem Wettbewerber anrufen und nachfragen", False),
                    ("Im Internet-Forum die Frage stellen", False),
                ),
            ),
            FrageDef(
                text="Eine ungenehmigte Ausfuhr eines gelisteten Gutes wird entdeckt. Wer kann persönlich haften?",
                erklaerung="Strafrechtlich haftet die Person, die gehandelt hat (Vertrieb, Versand, "
                "Geschäftsführung). Zusätzlich trifft die Firma eine Verbandsgeldbuße nach § 30 OWiG.",
                optionen=_opts(
                    ("Nur die GmbH als juristische Person", False),
                    ("Nur der Zoll, weil er die Ausfuhr abgewickelt hat", False),
                    ("Die handelnde Person persönlich, zusätzlich die Firma per Verbandsgeldbuße", True),
                    ("Niemand, weil Exportkontrolle reine Verwaltungssache ist", False),
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
                    "## Worum geht's?\n\n"
                    "Abfall ist in deutschen Industriebetrieben einer der größten "
                    "Umweltkosten-Posten und gleichzeitig einer der am stärksten regulierten "
                    "Bereiche. Wer Späne, Öl oder Lack falsch eingestuft oder unsortiert "
                    "entsorgt, verstößt gegen das Kreislaufwirtschaftsgesetz und riskiert "
                    "Bußgelder bis 100.000 Euro pro Verstoß. Du lernst die fünfstufige "
                    "Abfallhierarchie kennen und warum die Reihenfolge entscheidet, was mit "
                    "deinen Werkhallen-Abfällen passieren darf.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **KrWG § 6** — fünfstufige Abfallhierarchie als verbindliche Rangfolge\n"
                    "- **KrWG § 7** — Grundpflichten der Abfallbewirtschaftung, Vorrang der Verwertung\n"
                    "- **KrWG § 8** — Rangfolge der Verwertungsmaßnahmen, Hochwertigkeitsgebot\n"
                    "- **KrWG § 69** — Bußgeldkatalog: bis 100.000 Euro je Ordnungswidrigkeit\n"
                    "- **AVV** — Abfallverzeichnis-Verordnung mit sechsstelligem Abfallschlüssel\n\n"
                    "## Was musst du wissen\n\n"
                    "Das *Kreislaufwirtschaftsgesetz* (KrWG) ist das deutsche Umsetzungsgesetz "
                    "der EU-Abfallrahmenrichtlinie. Sein Herzstück ist die fünfstufige "
                    "Abfallhierarchie in § 6. Jede Stufe hat Vorrang vor der nächsten — "
                    "Beseitigung im Restmüll ist die letzte Option, nicht die erste.\n\n"
                    "| Stufe | Maßnahme | Beispiel Werkhalle |\n"
                    "|---|---|---|\n"
                    "| 1 | Vermeidung | Mehrweg-Transportkisten statt Einweg-Folie |\n"
                    "| 2 | Vorbereitung zur Wiederverwendung | Paletten reparieren statt verschrotten |\n"
                    "| 3 | Recycling | Aluminium-Späne sortenrein zum Verwerter |\n"
                    "| 4 | Sonstige Verwertung | Heizwertige Lacke energetisch nutzen |\n"
                    "| 5 | Beseitigung | Deponierung, Verbrennung ohne Energienutzung |\n\n"
                    "Jeder Abfall bekommt nach der *Abfallverzeichnis-Verordnung* (AVV) einen "
                    "sechsstelligen **Abfallschlüssel** zugeordnet. Ein Sternchen hinter der "
                    "Nummer kennzeichnet **gefährliche Abfälle** — für diese gelten "
                    "verschärfte Pflichten (Begleitschein, Andienung, sichere Lagerung). "
                    "Typische Schlüssel im Maschinenbau sind 12 01 09* (halogenfreie "
                    "Kühlschmierstoff-Emulsion), 13 02 05* (nicht-chlorierte Maschinen- und "
                    "Schmieröle), 15 01 10* (Verpackungen mit Schadstoffrückständen), "
                    "16 01 07* (Ölfilter), 08 01 11* (Farb- und Lackabfälle mit Lösemitteln) "
                    "und 20 01 21* (Leuchtstoffröhren).\n\n"
                    "Wichtig: der Abfallschlüssel hängt am *Entstehungsprozess*, nicht am "
                    "Material allein. Eine Aluminium-Folie aus dem Büro ist 15 01 04, "
                    "Aluminium-Späne aus der CNC-Fräse sind 12 01 03 — beide Aluminium, "
                    "aber unterschiedlich klassifiziert.\n\n"
                    "## Was musst du tun\n\n"
                    "Bevor du irgendetwas in eine Tonne wirfst:\n\n"
                    "1. Prüfe, ob es vermieden oder wiederverwendet werden kann (Stufen 1 und 2)\n"
                    "2. Lies das Etikett der Tonne oder des Containers — Abfallschlüssel und Materialgruppe\n"
                    "3. Bei gefährlichen Abfällen (Sternchen-Schlüssel) niemals in den Restmüll\n"
                    "4. Bei Zweifel die Vorgesetzte oder den Abfallbeauftragten fragen — nicht raten\n"
                    "5. Verschmutzte Verpackungen (z.B. mit Lackresten) gehören in die Sondermüll-Tonne\n\n"
                    "Pro Betrieb ab einer bestimmten Größe muss ein **Abfallbeauftragter** "
                    "nach § 59 KrWG bestellt sein — meist die Person, die auch das "
                    "Umweltmanagement nach ISO 14001 koordiniert. Diese Person ist deine "
                    "Anlaufstelle bei jeder Unsicherheit.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Zulieferbetrieb für Karosserieteile entsorgte jahrelang lackbehaftete "
                    "Putzlappen über den normalen Industriemüll-Container. Bei einer Kontrolle "
                    "durch die untere Abfallbehörde fielen die roten Lackspuren auf. Die "
                    "Lappen waren AVV 15 02 02* (mit gefährlichen Stoffen verunreinigte "
                    "Aufsaugmaterialien) — also gefährlicher Abfall, für den ein Begleitschein "
                    "und eine zugelassene Entsorgungsfirma nötig gewesen wären. Der Betrieb "
                    "bekam 18.000 Euro Bußgeld plus Nachversteuerung der entgangenen "
                    "Entsorgungs-Gebühren der letzten drei Jahre. Heute steht in jeder Werkbank "
                    "eine separate UN-zugelassene Sammelbox für benutzte Lappen.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf Kreislaufwirtschaftsgesetz (KrWG) §§ 6-8, 59 und 69 "
                    "(Stand 2025), Abfallverzeichnis-Verordnung (AVV) und die "
                    "UBA-Informationsseite *Gefährliche Abfälle* "
                    "(umweltbundesamt.de/themen/abfall-ressourcen)."
                ),
            ),
            ModulDef(
                titel="Trennung & Dokumentation",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Die getrennte Erfassung von Abfällen ist keine Empfehlung, sondern "
                    "gesetzliche Pflicht. Wer Aluminium-Späne, Stahl-Späne und Kühlschmierstoff "
                    "in einen Container kippt, macht aus drei verwertbaren Wertstoffen einen "
                    "minderwertigen Mischabfall — und verstößt gegen § 11 KrWG sowie die "
                    "Gewerbeabfallverordnung. Du lernst die konkreten Trennpflichten und welche "
                    "Dokumentation dein Betrieb führen muss.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **KrWG § 11** — Getrennthaltung von Abfällen zur Verwertung\n"
                    "- **GewAbfV §§ 3-4** — Trennpflicht und Vorbehandlung für Gewerbeabfälle\n"
                    "- **GewAbfV § 13** — 50-Prozent-Quote bei Vorbehandlung, Dokumentationspflicht\n"
                    "- **KrWG §§ 47-50** — Nachweisverfahren für gefährliche Abfälle\n"
                    "- **NachwV** — Nachweisverordnung mit eANV-Pflicht seit 2010\n\n"
                    "## Was musst du wissen\n\n"
                    "Die *Gewerbeabfallverordnung* (GewAbfV) verlangt, dass folgende Fraktionen "
                    "an der Anfallstelle getrennt gesammelt werden, sobald es technisch möglich "
                    "und wirtschaftlich zumutbar ist:\n\n"
                    "- Papier, Pappe, Karton\n"
                    "- Glas\n"
                    "- Kunststoffe\n"
                    "- Metalle\n"
                    "- Holz\n"
                    "- Bioabfälle\n"
                    "- Textilien\n\n"
                    "Im Maschinenbau kommen dazu **prozessspezifische Fraktionen**: "
                    "Metallspäne sortenrein nach Material (Aluminium, Stahl, Buntmetall wie "
                    "Kupfer und Messing), Kühlschmierstoff-Emulsionen, Hydraulik- und "
                    "Maschinenöle, Schleifschlämme, Säuren und Laugen aus der "
                    "Oberflächenbehandlung, sowie Aerosoldosen und Lackabfälle aus der "
                    "Lackiererei. Sortenreine Aluminium-Späne bringen 1,50 bis 2,00 Euro pro "
                    "Kilo, vermischte Metallspäne nur 0,20 bis 0,50 Euro — die Trennung "
                    "lohnt sich nicht nur rechtlich.\n\n"
                    "Für Gewerbeabfälle gilt seit 2017 die **50-Prozent-Quote** nach "
                    "GewAbfV § 13: wer die fünf Pflichtfraktionen nicht getrennt sammelt, muss "
                    "den gemischten Restabfall an eine Vorbehandlungsanlage liefern, die "
                    "mindestens 50 Prozent zur Verwertung aussortiert. Diese Vorbehandlung "
                    "ist deutlich teurer als die getrennte Sammlung.\n\n"
                    "Für **gefährliche Abfälle** ist die Dokumentation am strengsten geregelt. "
                    "Jeder Transport braucht einen *Begleitschein* nach Nachweisverordnung. "
                    "Seit 2010 läuft das ausschließlich elektronisch über das "
                    "**eANV** (elektronisches Nachweisverfahren) — eine zentrale Plattform "
                    "der Länder. Erzeuger, Beförderer und Entsorger signieren digital, der "
                    "Begleitschein wandert in Echtzeit durch die Beteiligten. Die Dokumente "
                    "müssen drei Jahre aufbewahrt werden, bei manchen Abfällen sogar zehn "
                    "Jahre.\n\n"
                    "## Was musst du tun\n\n"
                    "In der Werkhalle ist deine Aufgabe:\n\n"
                    "1. Späne und Bohrspäne direkt am Werkzeug in die richtige Sammelwanne (Material-getrennt)\n"
                    "2. Kühlschmierstoff niemals in den Bodenablauf oder die Späne-Tonne — gehört in den KSS-Tank\n"
                    "3. Ölfilter und ölverschmierte Lappen in die rote UN-Sammelbox, nicht in den Restmüll\n"
                    "4. Aerosoldosen leer und drucklos in den Spezialcontainer, nicht in den Schrott\n"
                    "5. Bei der Übergabe an den Entsorger oder den Lkw-Fahrer auf den Begleitschein achten\n\n"
                    "Bei jedem **Begleitschein** schaust du, dass Abfallschlüssel, Menge und "
                    "Erzeuger-Nummer mit der tatsächlichen Abholung übereinstimmen. "
                    "Fälschungen oder Lückenhafte Dokumente sind kein Kavaliersdelikt — "
                    "sie sind eine **Straftat** nach § 326 StGB, nicht nur eine "
                    "Ordnungswidrigkeit.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Eine Dreherei mit 80 Mitarbeitenden hatte eine Sammeltonne für 'Metallschrott' "
                    "in der Halle, in die Aluminium, Stahl und gelegentlich auch Kupferreste "
                    "geworfen wurden. Der Schrotthändler zahlte pauschal 0,30 Euro pro Kilo. "
                    "Nach einem Audit führte der Betrieb drei farbig markierte Container ein "
                    "(silber Aluminium, grau Stahl, rot Kupfer/Buntmetall) plus eine separate "
                    "Wanne für Kühlschmierstoff-tropfende Späne. Die jährlichen "
                    "Schrott-Einnahmen verdreifachten sich, die Entsorgungskosten für "
                    "Mischabfall fielen weg. Gleichzeitig wurde das eANV-Konto aufgesetzt — "
                    "vorher war der Betrieb formal nicht ordnungsgemäß registriert, was bei "
                    "einer Prüfung mit bis zu 50.000 Euro Bußgeld geahndet worden wäre.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf Kreislaufwirtschaftsgesetz §§ 11 und 47-50 "
                    "(Stand 2025), Gewerbeabfallverordnung (GewAbfV 2017) §§ 3, 4 und 13, "
                    "Nachweisverordnung (NachwV) und eANV-Dokumentation der "
                    "Zentralen Koordinierungsstelle Abfall."
                ),
            ),
            ModulDef(
                titel="ADR-Versand & Energie/Wasser",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Sobald gefährliche Stoffe das Werksgelände auf einem Lkw verlassen, "
                    "greift das **ADR** — das Europäische Übereinkommen über die "
                    "internationale Beförderung gefährlicher Güter auf der Straße. Daneben "
                    "verlangt ISO 14001 von zertifizierten Betrieben, ihren Energie- und "
                    "Wasserverbrauch systematisch zu erfassen und zu reduzieren. Du lernst die "
                    "ADR-Basics, die du am Versand und im Wareneingang kennen musst, und "
                    "warum Energie- und Wasser-Effizienz nicht nur Kostensache, sondern "
                    "Compliance-Pflicht ist.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **ADR 2025** — Europäisches Übereinkommen, neunfache Gefahrgut-Klassen\n"
                    "- **GGVSEB** — deutsche Durchführungsverordnung zum ADR\n"
                    "- **GbV** — Gefahrgutbeauftragten-Verordnung, Pflicht ab bestimmten Mengen\n"
                    "- **ISO 14001:2015** — Umweltmanagementsystem, Kapitel 6.1 und 9.1\n"
                    "- **EnEfG** — Energieeffizienzgesetz 2023, Pflicht-Energie-Audit für KMU\n\n"
                    "## Was musst du wissen\n\n"
                    "Das **ADR** kennt neun Gefahrgut-Klassen, jede mit einem eigenen Gefahrzettel "
                    "(rautenförmiges Symbol):\n\n"
                    "| Klasse | Inhalt | Beispiel Werkstoff |\n"
                    "|---|---|---|\n"
                    "| 1 | Explosive Stoffe | Sprengmittel, Pyrotechnik |\n"
                    "| 2 | Gase | Acetylen, Propan, Argon-Flaschen |\n"
                    "| 3 | Entzündbare Flüssigkeiten | Lacke, Lösemittel, Benzin |\n"
                    "| 4 | Entzündbare Feststoffe | Magnesium-Späne, Schwefel |\n"
                    "| 5 | Entzündend wirkende Stoffe | Wasserstoffperoxid, Nitrate |\n"
                    "| 6 | Giftige und ansteckungsgefährliche Stoffe | Quecksilber, Pflanzenschutz |\n"
                    "| 7 | Radioaktive Stoffe | Prüfstrahler, Messquellen |\n"
                    "| 8 | Ätzende Stoffe | Schwefelsäure, Natronlauge |\n"
                    "| 9 | Verschiedene gefährliche Stoffe | Lithium-Akkus, Asbest |\n\n"
                    "Für kleine Mengen gibt es zwei wichtige Erleichterungen. **Begrenzte "
                    "Mengen** (Limited Quantities, LQ) erlauben den Transport in "
                    "Innenverpackungen bis zu einer stoffspezifischen Höchstmenge — das "
                    "Versandstück trägt nur das LQ-Rautensymbol, die Vorschriften zu "
                    "orangefarbenen Warntafeln und ADR-Schein entfallen.\n\n"
                    "Daneben gilt die **1000-Punkte-Regel** (ADR 1.1.3.6). Pro Beförderungseinheit "
                    "wird für jeden Stoff Menge mal Faktor (je nach Beförderungskategorie) "
                    "gerechnet. Bleibt die Summe unter 1000 Punkten, entfallen ADR-Schein "
                    "des Fahrers, orangefarbene Warntafeln und Schutzausrüstung — "
                    "Pflicht bleibt aber die Unterweisung nach ADR 1.3 und ein 2-kg-"
                    "Feuerlöscher. Mit den 2025er Änderungen wurden Freistellungen für "
                    "LQ und Privatabfälle ausgeweitet.\n\n"
                    "Ab bestimmten Mengen muss ein **Gefahrgutbeauftragter** nach GbV "
                    "bestellt sein. Im Mittelstand ist das oft eine externe Dienstleistung. "
                    "Frag nicht selbst, ob ihr einen braucht — wenn du regelmäßig Lacke, "
                    "Lösemittel oder Lithium-Akkus versendest, fast sicher ja.\n\n"
                    "**ISO 14001** verpflichtet zertifizierte Betriebe, bedeutende "
                    "Umweltaspekte zu identifizieren (Kapitel 6.1) und Kennzahlen zu erheben "
                    "(Kapitel 9.1). Konkret heißt das im Maschinenbau: Stromverbrauch pro "
                    "produzierter Einheit, Wasserverbrauch in Lackiererei und Reinigung, "
                    "Druckluft-Leckage-Quote, CO2-Bilanz aus Heizung und Logistik. Das **EnEfG** "
                    "(seit 2023) verlangt zusätzlich bei Unternehmen ab 7,5 GWh Endenergie "
                    "ein Energiemanagementsystem nach ISO 50001.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du im Versand oder Wareneingang mit Gefahrgut zu tun hast:\n\n"
                    "1. Prüfe das Versandstück auf Gefahrzettel, UN-Nummer und Versandbezeichnung\n"
                    "2. Bei LQ-Sendung den schwarz-weißen LQ-Rhombus prüfen, sonst voll-ADR-Kennzeichnung\n"
                    "3. Niemals offene oder beschädigte Gefahrgut-Packstücke annehmen oder verladen\n"
                    "4. Bei Unklarheit Annahme verweigern und Gefahrgutbeauftragten informieren\n"
                    "5. Bei einem Leck oder Unfall sofort räumen, Notruf 112, Sicherheitsdatenblatt bereithalten\n\n"
                    "Beim Energie- und Wasser-Sparen in der Werkhalle:\n\n"
                    "- Druckluftleitungen auf hörbare Lecks prüfen und melden — ein 3-mm-Leck kostet 1.000 Euro pro Jahr\n"
                    "- Maschinen am Ende der Schicht in Standby oder ganz aus, Beleuchtung nur wo gebraucht\n"
                    "- Kühlschmierstoff nicht überdosieren, Wasser-Hochdruckreiniger sparsam einsetzen\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Maschinenbauer versendete einen Karton mit drei Sprühdosen Korrosionsschutz "
                    "und einer Flasche Bremsenreiniger an einen Kunden — als normales Paket. Der "
                    "Paketdienst stellte das Gefahrgut beim Scan fest (Klasse 2.1 und 3, "
                    "LQ-Verpackung war nicht korrekt gekennzeichnet) und gab das Paket zurück "
                    "mit einer Schadensanzeige. Der Vorgang löste eine Prüfung durch das "
                    "Gewerbeaufsichtsamt aus. Ergebnis: kein Gefahrgutbeauftragter benannt, "
                    "keine UN-zugelassene Verpackung, keine Schulung der Versandmitarbeitenden. "
                    "Bußgeld 6.500 Euro plus die Auflage, binnen drei Monaten einen externen "
                    "Gefahrgutbeauftragten zu bestellen. Heute läuft jeder Gefahrgut-Versand "
                    "über eine Checkliste, und der Versand-Mitarbeiter hat einen ADR-1.3-"
                    "Lehrgang absolviert.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf ADR 2025 (Teil 1 Abschnitt 1.1.3.6 *1000-Punkte-Regel*, "
                    "Teil 3 Kapitel 3.4 *Begrenzte Mengen*), Gefahrgutverordnung Straße, "
                    "Eisenbahn und Binnenschiff (GGVSEB), Gefahrgutbeauftragten-Verordnung "
                    "(GbV), ISO 14001:2015 sowie Energieeffizienzgesetz (EnEfG 2023)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Welche Reihenfolge gibt die fünfstufige Abfallhierarchie nach KrWG § 6 vor?",
                erklaerung="§ 6 KrWG legt die Rangfolge fest: Vermeidung vor Wiederverwendung vor "
                "Recycling vor sonstiger Verwertung vor Beseitigung — Beseitigung ist letzte Option.",
                optionen=_opts(
                    ("Beseitigung - Recycling - Verwertung - Wiederverwendung - Vermeidung", False),
                    ("Vermeidung - Vorbereitung zur Wiederverwendung - Recycling - sonstige Verwertung - Beseitigung", True),
                    ("Recycling - Vermeidung - Wiederverwendung - Beseitigung - Verbrennung", False),
                    ("Trennung - Sammlung - Transport - Verwertung - Beseitigung", False),
                ),
            ),
            FrageDef(
                text="Woran erkennst du in der Abfallverzeichnis-Verordnung einen *gefährlichen* Abfall?",
                erklaerung="Gefährliche Abfälle tragen ein Sternchen hinter dem sechsstelligen "
                "Abfallschlüssel (z.B. 12 01 09* für halogenfreie Kühlschmierstoff-Emulsion).",
                optionen=_opts(
                    ("Am roten Aufkleber des Entsorgers", False),
                    ("Am Sternchen (*) hinter der sechsstelligen AVV-Nummer", True),
                    ("Am Buchstaben G im Abfallschlüssel", False),
                    ("Am Eintrag in der GHS-Liste", False),
                ),
            ),
            FrageDef(
                text="Welcher AVV-Schlüssel passt zu gebrauchten Ölfiltern aus der Werkhalle?",
                erklaerung="16 01 07* ist der korrekte AVV-Schlüssel für Ölfilter. Das Sternchen "
                "zeigt: gefährlicher Abfall, Begleitschein und sichere Lagerung Pflicht.",
                optionen=_opts(
                    ("15 01 04 (Verpackungen aus Metall)", False),
                    ("20 01 01 (Papier und Pappe)", False),
                    ("16 01 07* (Ölfilter)", True),
                    ("12 01 03 (NE-Metallspäne)", False),
                ),
            ),
            FrageDef(
                text="Welche maximale Geldbuße droht laut KrWG § 69 pro Ordnungswidrigkeit?",
                erklaerung="KrWG § 69 sieht Bußgelder bis 100.000 Euro je Ordnungswidrigkeit vor. "
                "Bei vorsätzlicher Falschdeklaration kann zusätzlich § 326 StGB greifen (Straftat).",
                optionen=_opts(
                    ("5.000 Euro", False),
                    ("25.000 Euro", False),
                    ("100.000 Euro", True),
                    ("500.000 Euro", False),
                ),
            ),
            FrageDef(
                text="Was schreibt § 11 KrWG zur Getrennthaltung vor?",
                erklaerung="§ 11 KrWG verlangt, dass verwertbare Abfälle an der Anfallstelle getrennt "
                "gesammelt werden, soweit dies technisch möglich und wirtschaftlich zumutbar ist.",
                optionen=_opts(
                    ("Abfälle müssen nur einmal pro Jahr getrennt werden", False),
                    ("Getrenntsammlung gilt nur für Haushaltsabfälle", False),
                    ("Verwertbare Abfälle sind an der Anfallstelle getrennt zu halten, soweit technisch möglich und zumutbar", True),
                    ("Die Trennung ist optional, wenn die Verwertungsquote insgesamt 50 % erreicht", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet die 50-Prozent-Quote in der Gewerbeabfallverordnung § 13?",
                erklaerung="Wer Gewerbeabfälle nicht getrennt sammelt, muss den gemischten Abfall an "
                "eine Vorbehandlungsanlage abgeben, die mindestens 50 % zur Verwertung aussortiert.",
                optionen=_opts(
                    ("Mindestens 50 % aller Mitarbeiter müssen geschult sein", False),
                    ("Mindestens 50 % der Gewerbeabfälle müssen vorbehandelt zur Verwertung gehen, wenn nicht getrennt gesammelt wurde", True),
                    ("Mindestens 50 % der Containerfläche müssen überdacht sein", False),
                    ("Mindestens 50 % der Entsorgungskosten müssen dokumentiert werden", False),
                ),
            ),
            FrageDef(
                text="Welche Plattform ist seit 2010 verpflichtend für Begleitscheine bei gefährlichen Abfällen?",
                erklaerung="Das eANV (elektronisches Nachweisverfahren) löst die Papier-Begleitscheine "
                "ab. Erzeuger, Beförderer und Entsorger signieren digital, Aufbewahrungsfrist 3-10 Jahre.",
                optionen=_opts(
                    ("Das Bundes-Abfallportal des UBA", False),
                    ("Das ELSTER-Steuerportal", False),
                    ("Das eANV (elektronisches Nachweisverfahren)", True),
                    ("Das ZEDAL-Portal des BMUV", False),
                ),
            ),
            FrageDef(
                text="Du findest in der Halle eine Tonne 'Metallschrott', in der Aluminium-Späne, "
                "Stahlspäne und ein paar Kupferreste liegen. Was tust du?",
                erklaerung="Sortenreine Sammlung ist wirtschaftlich (1,50-2,00 Euro/kg Aluminium vs. "
                "0,20-0,50 Euro/kg Mischschrott) und nach KrWG § 11 / GewAbfV gesetzliche Pflicht.",
                optionen=_opts(
                    ("Ich werfe noch meine Späne dazu, das ist ja sowieso Schrott", False),
                    ("Ich melde es dem Abfallbeauftragten oder Schichtleiter, damit getrennte Behälter aufgestellt werden", True),
                    ("Ich entsorge das Kupfer separat zu Hause", False),
                    ("Ich ignoriere es, das ist nicht meine Zuständigkeit", False),
                ),
            ),
            FrageDef(
                text="Eine Kollegin schüttet Kühlschmierstoff-Emulsion in den Bodenablauf, weil "
                "der KSS-Tank zu voll ist. Wie reagierst du?",
                erklaerung="KSS in den Bodenablauf ist eine Gewässerverunreinigung (§ 324 StGB, "
                "Straftat) und gefährdet die betriebliche Abwasser-Genehmigung. Sofort stoppen und melden.",
                optionen=_opts(
                    ("Schauen, dass niemand davon erfährt", False),
                    ("Sie auf den Verstoß hinweisen und den Vorfall umgehend dem Vorgesetzten / Umweltbeauftragten melden", True),
                    ("Auch eigene Reste auf diesem Weg entsorgen", False),
                    ("Den Bodenablauf mit Wasser nachspülen, damit sich der KSS verteilt", False),
                ),
            ),
            FrageDef(
                text="Ein Lkw-Fahrer reicht dir einen Begleitschein mit fehlender Abfallschlüssel-Nummer. "
                "Wie verhältst du dich?",
                erklaerung="Eine unvollständige Dokumentation ist nicht nur Ordnungswidrigkeit, sondern "
                "kann nach § 326 StGB als Straftat gewertet werden. Annahme/Abgabe verweigern.",
                optionen=_opts(
                    ("Ich unterschreibe trotzdem, der Fahrer hat es eilig", False),
                    ("Ich verweigere die Unterschrift und kontaktiere den Abfallbeauftragten", True),
                    ("Ich trage selbst irgendeinen Schlüssel ein, der passen könnte", False),
                    ("Ich rufe den Entsorger und lasse mir per Telefon einen Schlüssel diktieren, ohne ihn zu prüfen", False),
                ),
            ),
            FrageDef(
                text="Wie viele Gefahrgut-Klassen kennt das ADR?",
                erklaerung="ADR teilt Gefahrgut in 9 Klassen ein: 1 Explosive, 2 Gase, 3 entzündbare "
                "Flüssigkeiten, 4 entzündbare Feststoffe, 5 Oxidatoren, 6 giftig, 7 radioaktiv, 8 ätzend, 9 sonstige.",
                optionen=_opts(
                    ("5", False),
                    ("7", False),
                    ("9", True),
                    ("12", False),
                ),
            ),
            FrageDef(
                text="Zu welcher ADR-Klasse gehören brennbare Lösemittel wie Bremsenreiniger oder Lackverdünner?",
                erklaerung="Klasse 3 deckt entzündbare Flüssigkeiten ab. Gefahrzettel: Flamme auf rotem Grund.",
                optionen=_opts(
                    ("Klasse 2 (Gase)", False),
                    ("Klasse 3 (entzündbare Flüssigkeiten)", True),
                    ("Klasse 6 (Giftstoffe)", False),
                    ("Klasse 8 (ätzende Stoffe)", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'LQ' im ADR-Kontext?",
                erklaerung="LQ steht für *Limited Quantities* (begrenzte Mengen). Innenverpackungen "
                "unter einer stoffspezifischen Höchstmenge sind von vielen ADR-Vorschriften freigestellt.",
                optionen=_opts(
                    ("Liquid Quotient (Flüssigkeits-Anteil)", False),
                    ("Limited Quantities (begrenzte Mengen) — Freistellung für kleine Einheiten", True),
                    ("Load Quality (Beladungs-Qualität)", False),
                    ("Logistic Quarantine (Logistik-Sperre)", False),
                ),
            ),
            FrageDef(
                text="Was sagt die 1000-Punkte-Regel nach ADR 1.1.3.6?",
                erklaerung="Bleibt die Punktesumme (Menge x stoffspezifischer Faktor) pro Beförderungs"
                "einheit unter 1000, entfallen ADR-Schein des Fahrers, orange Warntafeln und Schutzausrüstung.",
                optionen=_opts(
                    ("Pro Tag dürfen 1000 Gefahrgut-Versandstücke verladen werden", False),
                    ("Unter einer Punktesumme von 1000 pro Beförderungseinheit gelten ADR-Erleichterungen", True),
                    ("Jeder Fahrer braucht 1000 ADR-Punkte für den Schein", False),
                    ("1000 Liter Diesel sind die Obergrenze für Werkstattanlieferungen", False),
                ),
            ),
            FrageDef(
                text="Welche Pflicht bleibt trotz 1000-Punkte-Freistellung bestehen?",
                erklaerung="Auch unter 1000 Punkten brauchen Fahrer eine Unterweisung nach ADR 1.3 "
                "und der Lkw muss einen Feuerlöscher (mind. 2 kg) an Bord haben.",
                optionen=_opts(
                    ("Vollständige ADR-Schulung mit Schein", False),
                    ("Orangefarbene Warntafeln vorne und hinten", False),
                    ("Unterweisung nach ADR 1.3 und ein 2-kg-Feuerlöscher an Bord", True),
                    ("Doppelte Begleitschein-Ausfertigung", False),
                ),
            ),
            FrageDef(
                text="Du bekommst im Wareneingang ein Paket mit sichtbar feuchtem, riechendem Karton "
                "und einem Klasse-3-Gefahrzettel. Was tust du?",
                erklaerung="Beschädigte Gefahrgut-Verpackungen niemals annehmen — Leckage-Gefahr, "
                "Brand- oder Vergiftungsrisiko. Annahme verweigern und Gefahrgutbeauftragten informieren.",
                optionen=_opts(
                    ("Annahme verweigern, Fahrer informieren, Vorgesetzten / Gefahrgutbeauftragten holen", True),
                    ("Annehmen und sofort in den Lagerregal-Hochregalbereich stellen", False),
                    ("Annehmen und in den Hof zum Auslüften stellen", False),
                    ("Den Karton öffnen, um zu prüfen, was drin ist", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage zu ISO 14001 stimmt?",
                erklaerung="ISO 14001:2015 verlangt die Identifikation bedeutender Umweltaspekte (Kap. 6.1) "
                "und das Monitoring per Kennzahlen (Kap. 9.1) — nicht eine fixe CO2-Quote.",
                optionen=_opts(
                    ("ISO 14001 schreibt eine CO2-Reduktion von 20 % pro Jahr vor", False),
                    ("ISO 14001 verlangt ein Umweltmanagementsystem mit bedeutenden Umweltaspekten und Kennzahlen-Monitoring", True),
                    ("ISO 14001 ersetzt das Kreislaufwirtschaftsgesetz", False),
                    ("ISO 14001 ist nur für Lebensmittelbetriebe verpflichtend", False),
                ),
            ),
            FrageDef(
                text="Was ist eine Druckluft-Leckage in einer Werkhalle wirtschaftlich?",
                erklaerung="Druckluft ist eine der teuersten Energieformen. Bereits ein 3-mm-Leck "
                "kostet rund 1.000 Euro Stromkosten pro Jahr — Lecks melden lohnt sich.",
                optionen=_opts(
                    ("Vernachlässigbar, Druckluft ist quasi kostenlos", False),
                    ("Ein 3-mm-Leck verursacht rund 1.000 Euro Stromkosten pro Jahr", True),
                    ("Nur bei größeren Anlagen relevant", False),
                    ("Erst ab 10 mm Durchmesser zählt eine Leckage als Verschwendung", False),
                ),
            ),
            FrageDef(
                text="Welche Behauptung zur Trennung von Metallspänen ist falsch?",
                erklaerung="Sortenreine Trennung lohnt sich immer: Aluminium bringt 1,50-2,00 Euro/kg, "
                "Mischschrott nur 0,20-0,50 Euro/kg. Zudem ist Trennung nach § 11 KrWG Pflicht.",
                optionen=_opts(
                    ("Sortenreine Späne erzielen einen höheren Verkaufspreis", False),
                    ("Kühlschmierstoff-tropfende Späne gehören in eine eigene Wanne", False),
                    ("Spänen-Trennung ist freiwillig, wenn alles zum gleichen Schrotthändler geht", True),
                    ("Aluminium und Stahl müssen sortenrein getrennt werden", False),
                ),
            ),
            FrageDef(
                text="Wer ist im Betrieb laut KrWG § 59 ab einer bestimmten Größe zu bestellen?",
                erklaerung="§ 59 KrWG verpflichtet abfallintensive Betriebe zur Bestellung eines "
                "Abfallbeauftragten — meist die Person, die auch das ISO-14001-System koordiniert.",
                optionen=_opts(
                    ("Ein externer Sachverständiger für jede Tonne Abfall", False),
                    ("Ein Abfallbeauftragter zur Überwachung und Beratung im Betrieb", True),
                    ("Ein Vertreter der örtlichen Müllabfuhr", False),
                    ("Ein Mitarbeiter des Umweltamts mit Büro im Betrieb", False),
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
                    "## Worum geht's?\n\n"
                    "Ein Qualitätsmanagementsystem nach ISO 9001 ist kein Ordner im Regal, "
                    "sondern die Art, wie ihr im Betrieb arbeitet. Wer einen Auftrag annimmt, "
                    "ein Bauteil fräst, ein Maß prüft, eine Reklamation aufnimmt — folgt einem "
                    "Prozess. Du lernst, warum die Norm auf Prozessdenken und den **PDCA-Zyklus** "
                    "setzt, was risikobasiertes Denken bedeutet und warum die Geschäftsführung "
                    "(Top-Management) explizit in der Pflicht steht.\n\n"
                    "Wichtig: ISO 9001 ist eine Kunden-Voraussetzung. Ohne gültiges Zertifikat "
                    "bekommt ein Automotive-Zulieferer oder Maschinenbauer in vielen Lieferketten "
                    "schlicht keine Aufträge mehr.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **ISO 9001:2015** — internationale Norm für Qualitätsmanagement-Systeme (QMS)\n"
                    "- **IATF 16949:2016** — Automotive-Erweiterung, baut auf ISO 9001 auf, "
                    "ergänzt rund 100 Anforderungen plus *Customer Specific Requirements* (CSR) "
                    "der OEMs (VW, BMW, Daimler, Stellantis, Ford)\n"
                    "- **Annex SL / Harmonized Structure (HS)** — gemeinsame 10-Kapitel-Struktur "
                    "aller ISO-Managementsystem-Normen seit 2012, überarbeitet 2021\n"
                    "- **ISO 9000:2015** — Grundbegriffe und Definitionen (wird in 9001 referenziert)\n\n"
                    "ISO 9001 ist kein Gesetz, sondern eine privatrechtliche Norm. Aber: viele "
                    "Kunden machen sie zur Vertragsbedingung. Wer als Zulieferer nicht zertifiziert "
                    "ist, fliegt aus dem Lieferantenpool.\n\n"
                    "## Was musst du wissen\n\n"
                    "Die Norm gliedert sich nach der Harmonized Structure in zehn Hauptkapitel. "
                    "Kapitel 1 bis 3 sind formal (Geltungsbereich, Verweise, Begriffe), die "
                    "eigentlichen Anforderungen stehen in Kapitel 4 bis 10:\n\n"
                    "| Kapitel | Inhalt | Kernfrage |\n"
                    "|---|---|---|\n"
                    "| 4 | Kontext der Organisation | Wer sind unsere interessierten Parteien? |\n"
                    "| 5 | Führung | Was macht die GF konkret für Qualität? |\n"
                    "| 6 | Planung (Risiken/Chancen) | Was kann schiefgehen, was ist die Chance? |\n"
                    "| 7 | Unterstützung (Personal, Infrastruktur) | Haben wir die Mittel? |\n"
                    "| 8 | Betrieb (Produktion, Lieferanten) | Wie liefern wir die Leistung? |\n"
                    "| 9 | Bewertung der Leistung (Audit, KPI) | Funktioniert es? |\n"
                    "| 10 | Verbesserung (KVP, Korrektur) | Wo werden wir besser? |\n\n"
                    "Das Herzstück ist der **PDCA-Zyklus** nach Deming: *Plan* (planen, Ziel "
                    "setzen, Risiken bewerten), *Do* (umsetzen), *Check* (messen, prüfen, "
                    "auditieren), *Act* (anpassen, verbessern). Jeder Prozess im Betrieb durchläuft "
                    "diesen Zyklus immer wieder — vom Wareneingang bis zur Endkontrolle.\n\n"
                    "Das **risikobasierte Denken** (Klausel 6.1) ersetzt seit 2015 die alte "
                    "Forderung nach Vorbeugemaßnahmen. Jeder Prozess wird auf Risiken und Chancen "
                    "geprüft, bevor er anläuft. Beispiel: Was passiert, wenn der Hauptlieferant "
                    "ausfällt? Was, wenn die einzige CNC-Maschine ausfällt? Welche neuen "
                    "Geschäfte wären möglich, wenn wir die Toleranz auf 5 Mikrometer drücken?\n\n"
                    "## Was musst du tun\n\n"
                    "Auch ohne formale Q-Funktion bist du am QMS beteiligt:\n\n"
                    "1. Halte dich an die freigegebene Arbeitsanweisung — nicht an 'so haben wir das immer gemacht'\n"
                    "2. Dokumentiere deine Arbeit nachvollziehbar (Prüfprotokoll, Schichtbuch, BDE-Buchung)\n"
                    "3. Melde Abweichungen sofort an Schichtleitung oder Q-Beauftragte:n, nicht nach Feierabend\n"
                    "4. Nutze KVP-Karten oder das Vorschlagswesen, wenn du eine bessere Arbeitsweise siehst\n"
                    "5. Arbeite mit aktuellen Dokumenten — gilt eine Zeichnung Rev. 03, dann nicht aus dem alten Ordner Rev. 01 ziehen\n\n"
                    "Du musst nicht die ganze Norm kennen. Du musst aber wissen, welcher Prozess "
                    "deine Arbeit betrifft und wo die zugehörige Anweisung im System steht.\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein Automotive-Zulieferer fertigt Aluminium-Druckgussteile für ein Getriebe. "
                    "In der Endkontrolle fällt auf, dass die Bohrung eines Bauteils 0,03 mm zu eng "
                    "ist — knapp außerhalb der Toleranz. Im alten Denken hätte der Prüfer "
                    "kommentarlos nachgerieben und das Teil durchgewinkt. Im PDCA-Denken: *Check* "
                    "hat die Abweichung erkannt, also *Act* — Teil sperren, Q-Beauftragte:n "
                    "rufen, Ursache am Prozess suchen (Werkzeug-Verschleiß? Programm-Drift?). "
                    "Die Q-Beauftragte stoppt die Charge, ein gemeinsam mit der Instandhaltung "
                    "definiertes *Plan* (neues Werkzeug, neue Eingangskontrolle Werkzeug-Lieferant) "
                    "geht in den nächsten Zyklus. Beim Kunden-Audit drei Monate später ist die "
                    "lückenlose Dokumentation dieser Schleife der Beweis, dass das QMS lebt.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DIN EN ISO 9001:2015 *Qualitätsmanagementsysteme — "
                    "Anforderungen* (Volltext beim Beuth-Verlag kostenpflichtig), IATF 16949:2016 "
                    "*Automotive Quality Management System Standard*, sowie Kommentierungen von "
                    "DGQ (Deutsche Gesellschaft für Qualität) und TÜV. Annex SL / Harmonized "
                    "Structure nach ISO/IEC Directives Part 1, Annex SL (Stand 2021)."
                ),
            ),
            ModulDef(
                titel="Reklamationen & Audit-Verhalten",
                inhalt_md=(
                    "## Worum geht's?\n\n"
                    "Eine Kunden-Reklamation ist kein Angriff, sondern ein Geschenk: der Kunde "
                    "gibt dir die Chance, einen Fehler zu reparieren, bevor er ein anderer "
                    "Lieferant wird. Und ein Audit ist keine Inszenierung mit Show-Tour, sondern "
                    "der externe Blick auf euer System. Du lernst, wie der **8D-Report** als "
                    "Standardprozess in der Automotive-Lieferkette funktioniert und wie du dich "
                    "richtig verhältst, wenn ein:e Auditor:in dich an deiner Maschine "
                    "anspricht.\n\n"
                    "Das wichtigste Prinzip vorab: Fehler werden nicht vertuscht, sondern offen "
                    "dokumentiert. Ein vertuschter Fehler kostet zehnmal so viel wie ein offen "
                    "behobener — und im schlimmsten Fall den Auftrag.\n\n"
                    "## Rechtsgrundlage\n\n"
                    "- **ISO 9001:2015 Klausel 10.2** — Nichtkonformität und Korrekturmaßnahme\n"
                    "- **ISO 9001:2015 Klausel 9.2** — Internes Audit (mindestens jährlich)\n"
                    "- **IATF 16949 Klausel 10.2.3** — Problemlösung mit dokumentierter Methodik "
                    "(8D oder gleichwertig)\n"
                    "- **VDA-Band 'Problemlösung in 8 Disziplinen' (Ausgabe 2018)** — VDA-konforme "
                    "Anwendung der 8D-Methode für die Automotive-Lieferkette\n\n"
                    "## Was musst du wissen\n\n"
                    "Der **8D-Report** ist die Standard-Antwort auf eine Kunden-Reklamation. "
                    "Acht Disziplinen, klar abgegrenzt:\n\n"
                    "| Schritt | Inhalt |\n"
                    "|---|---|\n"
                    "| D1 | Team zusammenstellen (Produktion, Qualität, Entwicklung, Logistik) |\n"
                    "| D2 | Problem beschreiben mit Zahlen, Daten, Fakten (5W2H) |\n"
                    "| D3 | Sofortmaßnahmen — Kunde vor Folgefehlern schützen, gesperrte Ware |\n"
                    "| D4 | Ursache(n) ermitteln, z.B. mit Ishikawa und 5x Warum |\n"
                    "| D5 | Abstellmaßnahmen planen und wirksam machen |\n"
                    "| D6 | Abstellmaßnahmen umsetzen, Wirksamkeit nachweisen |\n"
                    "| D7 | Wiederholfehler vermeiden — Prozesse, FMEA, Kontrollplan anpassen |\n"
                    "| D8 | Team anerkennen, Erfahrung dokumentieren, Bericht freigeben |\n\n"
                    "OEMs erwarten D1 bis D3 typischerweise innerhalb von 24 Stunden, den Vollbericht "
                    "innerhalb von 10 bis 15 Arbeitstagen. Wer die Frist reißt, sammelt "
                    "Lieferanten-Bewertungspunkte ab und riskiert eskalierende Stufen bis zum "
                    "*Controlled Shipping Level 2* (Zusatzprüfung beim Lieferanten auf dessen Kosten).\n\n"
                    "Bei Audits unterscheidet man drei Typen. **Internes Audit** macht ihr selbst "
                    "oder eine beauftragte Q-Person mindestens jährlich pro Prozess. **Externes "
                    "Zertifizierungsaudit** läuft in zwei Stufen: Stage 1 (Dokumenten-Review, "
                    "halber Tag) und Stage 2 (vor-Ort-Audit, je nach Größe 2-5 Tage). Danach "
                    "kommt jährlich ein **Überwachungsaudit**, alle drei Jahre die "
                    "**Rezertifizierung** mit vollem Umfang. Ein zusätzliches **Kunden-Audit** "
                    "(2nd Party) kann jederzeit anberaumt werden, gerade in der Automotive-"
                    "Lieferkette.\n\n"
                    "Auditor:innen suchen keine Schuldigen, sondern Belege, dass eure Prozesse "
                    "funktionieren. Die typische Frage lautet 'Wie machen Sie das?' oder 'Zeigen "
                    "Sie mir, wo das dokumentiert ist'. Erwartet wird eine ehrliche, knappe "
                    "Antwort — keine auswendig gelernte Show.\n\n"
                    "## Was musst du tun\n\n"
                    "Wenn du einen Fehler entdeckst oder eine Reklamation bei dir landet:\n\n"
                    "1. Teil oder Charge sperren — rote Box, Sperrlager, klare Kennzeichnung\n"
                    "2. Q-Beauftragte:n und Schichtleitung sofort informieren, nicht erst nach Schichtende\n"
                    "3. Fakten festhalten: was, wann, wo, wie viele Stück, welche Maschine, welche Werkzeuge\n"
                    "4. Keine eigenmächtige Nacharbeit, ohne dass die Q-Stelle freigegeben hat\n"
                    "5. Im 8D-Team konstruktiv mitwirken, wenn du eingeladen wirst — du kennst die Realität an der Maschine\n\n"
                    "Wenn dich ein:e Auditor:in anspricht:\n\n"
                    "1. Ruhig und ehrlich antworten — 'Das weiß ich nicht, aber meine Schichtleitung weiß es' ist eine korrekte Antwort\n"
                    "2. Nicht raten oder beschönigen, lieber den/die Q-Beauftragte:n holen\n"
                    "3. Aktuelle Arbeitsanweisung am Platz zeigen können (Rev.-Stand auf Zeichnung prüfen)\n"
                    "4. Niemals Dokumente während des Audits 'schnell aktualisieren' — das ist Manipulation und gefährdet das Zertifikat\n\n"
                    "## Praxisbeispiel\n\n"
                    "Ein OEM reklamiert 150 Pleuelstangen mit Riefen an einer Lagerfläche. D1: "
                    "Q-Beauftragte:r ruft Team aus Schleiferei, Endprüfung, Instandhaltung und "
                    "Logistik zusammen. D2: Fehlerbild fotografiert, Charge eingrenzt auf zwei "
                    "Schichten an Maschine 7. D3: Sofortmaßnahme — alle Pleuel der Charge bei Kunde "
                    "und im eigenen Lager 100 Prozent nachgeprüft, 22 betroffene Teile aussortiert. "
                    "D4: 5x-Warum-Analyse legt offen, dass ein Schleifband eines neuen Lieferanten "
                    "ohne Eingangskontrolle eingebaut wurde und unzulässige Körnungsschwankung "
                    "hatte. D5/D6: Eingangskontrolle Schleifband mit Spezifikation eingeführt, "
                    "Lieferantenfreigabe-Prozess ergänzt, Schichtprüfung mit Kontrollnaht "
                    "alle 50 Teile. D7: Eintrag in die Prozess-FMEA, Kontrollplan-Update. D8: "
                    "8D-Report nach 12 Arbeitstagen freigegeben, vom Kunden akzeptiert, keine "
                    "Eskalation. Beim nächsten Überwachungsaudit ist genau dieser 8D der Beleg, "
                    "dass eure Korrekturmaßnahmen wirksam und nachhaltig sind.\n\n"
                    "## Quelle\n\n"
                    "Inhalte gestützt auf DIN EN ISO 9001:2015 Klauseln 9.2 (Internes Audit) und "
                    "10.2 (Nichtkonformität und Korrekturmaßnahme), IATF 16949:2016 Klausel 10.2.3 "
                    "(Problemlösung) sowie VDA-Band *8D — Problemlösung in 8 Disziplinen* "
                    "(VDA QMC, 1. Ausgabe 2018). Audit-Praxis nach DAkkS-Akkreditierungsregeln "
                    "und üblichen OEM-Customer-Specific-Requirements (Stand 2025)."
                ),
            ),
        ),
        fragen=(
            FrageDef(
                text="Wofür steht der PDCA-Zyklus, der das Herzstück der ISO 9001 bildet?",
                erklaerung="Plan-Do-Check-Act ist der nach W. E. Deming benannte Verbesserungskreislauf. "
                "Er strukturiert jeden Prozess: planen, umsetzen, prüfen, anpassen.",
                optionen=_opts(
                    ("Produce-Deliver-Control-Audit", False),
                    ("Plan-Do-Check-Act", True),
                    ("Prepare-Document-Confirm-Approve", False),
                    ("Process-Develop-Care-Adjust", False),
                ),
            ),
            FrageDef(
                text="Wie viele Hauptkapitel hat die ISO 9001:2015 nach der Harmonized Structure?",
                erklaerung="Die Norm folgt der gemeinsamen 10-Kapitel-Struktur (Annex SL / HS). "
                "Die eigentlichen Anforderungen stehen in Kapitel 4 bis 10.",
                optionen=_opts(
                    ("7", False),
                    ("8", False),
                    ("10", True),
                    ("12", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet IATF 16949 im Verhältnis zur ISO 9001?",
                erklaerung="IATF 16949 ist die Automotive-Erweiterung, die auf ISO 9001 aufsetzt "
                "und rund 100 zusätzliche Anforderungen plus OEM-Customer-Specific-Requirements bringt.",
                optionen=_opts(
                    ("Ein Konkurrenz-Standard zur ISO 9001 ohne Bezug", False),
                    ("Eine Vereinfachung der ISO 9001 für kleine Betriebe", False),
                    ("Automotive-Erweiterung, die ISO 9001 voraussetzt und ergänzt", True),
                    ("Eine reine Software-Norm für ERP-Systeme", False),
                ),
            ),
            FrageDef(
                text="Wofür steht das 'D' in 8D-Report?",
                erklaerung="Die acht D stehen für 'Disziplinen' — acht klar abgegrenzte Schritte "
                "der Problemlösung von der Team-Bildung (D1) bis zur Anerkennung (D8).",
                optionen=_opts(
                    ("Daten", False),
                    ("Dimensionen", False),
                    ("Disziplinen", True),
                    ("Dokumente", False),
                ),
            ),
            FrageDef(
                text="Was ist der erste Schritt (D1) in der 8D-Methode?",
                erklaerung="D1 ist die Team-Bildung. Erst mit einem interdisziplinären Team (Produktion, "
                "Qualität, Entwicklung, Logistik) startet die strukturierte Problemlösung.",
                optionen=_opts(
                    ("Sofortmaßnahmen einleiten", False),
                    ("Team zusammenstellen", True),
                    ("Ursache analysieren", False),
                    ("Bericht an den Kunden senden", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'risikobasiertes Denken' in der ISO 9001:2015?",
                erklaerung="Klausel 6.1 verlangt seit 2015, dass jeder Prozess vorab auf Risiken UND "
                "Chancen geprüft wird. Es ersetzt die alte Forderung nach Vorbeugemaßnahmen.",
                optionen=_opts(
                    ("Versicherungspflicht für alle Prozesse", False),
                    ("Jeder Prozess wird auf Risiken und Chancen geprüft, bevor er anläuft", True),
                    ("Nur sicherheitskritische Bauteile dürfen produziert werden", False),
                    ("Risikoanalyse nur für die Geschäftsführung relevant", False),
                ),
            ),
            FrageDef(
                text="Wie oft findet typischerweise ein internes Audit pro Prozess statt?",
                erklaerung="Klausel 9.2 verlangt mindestens jährlich. In der Praxis werden kritische "
                "Prozesse häufiger auditiert, manche unkritischen Bereiche in einem 3-Jahres-Plan rotiert.",
                optionen=_opts(
                    ("Einmal alle 10 Jahre", False),
                    ("Mindestens einmal jährlich", True),
                    ("Nur wenn ein Fehler aufgetreten ist", False),
                    ("Nur durch externe Auditoren erlaubt", False),
                ),
            ),
            FrageDef(
                text="In welchem Rhythmus läuft ein externes Zertifizierungs-Audit nach ISO 9001 ab?",
                erklaerung="Erstzertifizierung in zwei Stufen (Stage 1+2), danach jährliches "
                "Überwachungsaudit, alle drei Jahre Rezertifizierung mit vollem Umfang.",
                optionen=_opts(
                    ("Einmalig — wer einmal zertifiziert ist, bleibt es", False),
                    ("Jährliche Überwachung, alle 3 Jahre Rezertifizierung", True),
                    ("Monatlich, sonst verfällt das Zertifikat", False),
                    ("Nur auf Kunden-Wunsch", False),
                ),
            ),
            FrageDef(
                text="In welchem Kapitel der ISO 9001:2015 steht 'Führung' (Top-Management-Pflichten)?",
                erklaerung="Kapitel 5 'Führung' verpflichtet die Geschäftsführung persönlich — "
                "Q-Politik, Q-Ziele und Ressourcen sind Chefsache, nicht delegierbar.",
                optionen=_opts(
                    ("Kapitel 4", False),
                    ("Kapitel 5", True),
                    ("Kapitel 8", False),
                    ("Kapitel 10", False),
                ),
            ),
            FrageDef(
                text="Du entdeckst an deiner Maschine ein Bauteil mit klar erkennbarem Maßfehler. Was tust du?",
                erklaerung="Sperren und Q-Stelle informieren ist der korrekte Weg nach Klausel 8.7. "
                "Eigenmächtige Nacharbeit ohne Freigabe ist eine schwere Abweichung.",
                optionen=_opts(
                    ("Eigenmächtig nacharbeiten und durchlaufen lassen", False),
                    ("Teil sperren, Schichtleitung und Q-Beauftragte:n sofort informieren", True),
                    ("Zum nächsten Teil weiterarbeiten und das fehlerhafte unauffällig wegwerfen", False),
                    ("Erst nach Schichtende melden, damit der Takt nicht stoppt", False),
                ),
            ),
            FrageDef(
                text="Ein:e Auditor:in fragt dich an der Maschine: 'Wie ist die aktuelle Toleranz?' Du weißt es nicht. Was tust du?",
                erklaerung="Ehrlich antworten und die zuständige Person nennen ist die korrekte "
                "Audit-Antwort. Raten oder Beschönigen führt zu Folgefragen und Abweichungen.",
                optionen=_opts(
                    ("Eine plausibel klingende Zahl raten", False),
                    ("Ehrlich antworten 'Das weiß ich nicht, meine Schichtleitung weiß es' und Hilfe holen", True),
                    ("Vorgeben, gerade keine Zeit zu haben, und wegrennen", False),
                    ("Behaupten, dass diese Frage nicht zu deinem Bereich gehört", False),
                ),
            ),
            FrageDef(
                text="Eine Kunden-Reklamation läuft auf — D1 bis D3 sind fällig. In welchem Zeitrahmen erwarten OEMs das?",
                erklaerung="Typischer OEM-Standard sind 24 Stunden für D1-D3 (Team, Problembeschreibung, "
                "Sofortmaßnahme), damit der Kunde sofort vor Folgefehlern geschützt ist.",
                optionen=_opts(
                    ("Innerhalb von 24 Stunden", True),
                    ("Innerhalb von 4 Wochen", False),
                    ("Innerhalb des nächsten Quartals", False),
                    ("Wenn der Prüfbericht fertig ist, egal wann", False),
                ),
            ),
            FrageDef(
                text="Ihr seid mitten im Zertifizierungs-Audit. Dir fällt auf, dass eine Arbeitsanweisung im Schichtbuch noch die alte Revision ist. Was tust du?",
                erklaerung="Während des Audits Dokumente nachträglich zu aktualisieren ist Manipulation "
                "und kann das Zertifikat kosten. Offen ansprechen ist der einzig korrekte Weg.",
                optionen=_opts(
                    ("Schnell die neue Revision drucken und drüberlegen", False),
                    ("Offen ansprechen und der Q-Stelle/dem Auditor zeigen, dass die Korrektur eingeleitet wird", True),
                    ("Das Dokument verstecken, bis das Audit vorbei ist", False),
                    ("Den Auditor ablenken, damit er es nicht sieht", False),
                ),
            ),
            FrageDef(
                text="Du hast eine Idee, wie man einen Rüstvorgang um 20 Minuten verkürzen könnte. Was ist der Vaeren-richtige Weg?",
                erklaerung="ISO 9001 Kapitel 10 fordert KVP — kontinuierliche Verbesserung. Vorschläge "
                "gehören ins offizielle KVP- oder Vorschlagswesen, nicht in stille Eigeninitiative.",
                optionen=_opts(
                    ("Heimlich anders rüsten und schauen, ob es niemand merkt", False),
                    ("Idee im KVP- oder Vorschlagswesen einreichen, gemeinsam prüfen und ggf. anpassen", True),
                    ("Erst pensioniert die Idee mit ins Grab nehmen", False),
                    ("Nur dem Schichtleiter privat erzählen, nicht dokumentieren", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage über die Geschäftsführung im QMS ist nach ISO 9001:2015 richtig?",
                erklaerung="Kapitel 5 macht die GF persönlich verantwortlich. Sie kann Aufgaben delegieren, "
                "aber nicht die Verantwortung für Q-Politik, Q-Ziele und Ressourcen.",
                optionen=_opts(
                    ("Die GF hat mit Qualität nichts zu tun, das macht der Q-Beauftragte", False),
                    ("Die GF ist persönlich verantwortlich für Q-Politik, Q-Ziele und Ressourcen", True),
                    ("Die GF muss nur einmal jährlich ein Statement zur Qualität schreiben", False),
                    ("Die GF darf nur formal unterschreiben, inhaltlich entscheidet der Auditor", False),
                ),
            ),
            FrageDef(
                text="Was ist eine 'Nichtkonformität' (NC) im Sinne der ISO 9001?",
                erklaerung="Eine Nichtkonformität ist jede Nichterfüllung einer Anforderung — egal ob "
                "Norm, Kundenforderung, Zeichnungs-Toleranz oder interne Vorgabe.",
                optionen=_opts(
                    ("Ein zu langsam laufender Drucker", False),
                    ("Die Nichterfüllung einer Anforderung (Norm, Kunde, Zeichnung, interne Vorgabe)", True),
                    ("Eine kleine Schramme an einer Maschine", False),
                    ("Ein vergessener Geburtstag eines Kollegen", False),
                ),
            ),
            FrageDef(
                text="Welche dieser Praktiken ist im Sinne der ISO 9001 ein klares Fehlverhalten?",
                erklaerung="Vertuschen widerspricht Klausel 10.2 fundamental. Fehler müssen dokumentiert, "
                "analysiert und abgestellt werden — sonst lernt das System nicht.",
                optionen=_opts(
                    ("Einen Fehler offen melden und in der 5x-Warum-Analyse mitarbeiten", False),
                    ("Einen kleinen Fehler vertuschen, damit der Schichtdurchsatz stimmt", True),
                    ("Eine bessere Arbeitsmethode im KVP einreichen", False),
                    ("Bei einer Audit-Frage ehrlich antworten 'Das weiß ich nicht'", False),
                ),
            ),
            FrageDef(
                text="Was ist eine typische Audit-Frage einer:s ISO-9001-Auditor:in an einen Maschinenbediener?",
                erklaerung="Auditor:innen wollen sehen, dass der Prozess gelebt wird. Die typische Frage "
                "lautet 'Wie machen Sie das?' oder 'Zeigen Sie mir, wo das dokumentiert ist'.",
                optionen=_opts(
                    ("Was verdienen Sie hier?", False),
                    ("Wie machen Sie das und wo ist das dokumentiert?", True),
                    ("Wer ist Ihr Lieblingschef?", False),
                    ("Welches Auto fahren Sie?", False),
                ),
            ),
            FrageDef(
                text="Was bedeutet 'Controlled Shipping Level 2' (CSL2), das ein OEM bei wiederholten Reklamationen verhängen kann?",
                erklaerung="CSL2 ist eine eskalierende Maßnahme: zusätzliche 100-Prozent-Kontrolle beim "
                "Lieferanten auf dessen Kosten, oft durch eine externe Prüffirma. Sehr teuer und ein Warnsignal.",
                optionen=_opts(
                    ("Ein Rabatt für besonders zuverlässige Lieferanten", False),
                    ("Zusatz-Prüfung beim Lieferanten auf dessen Kosten als Eskalationsstufe", True),
                    ("Ein Kontingent für besonders schnelle Lieferung", False),
                    ("Eine Auszeichnung für vorbildliches QMS", False),
                ),
            ),
            FrageDef(
                text="Welche Aussage über das Audit-Verhalten ist richtig?",
                erklaerung="Auditor:innen suchen Belege, dass die Prozesse funktionieren — keine Schuldigen. "
                "Eine ehrliche, knappe Antwort ist immer besser als auswendig gelernte Show-Antworten.",
                optionen=_opts(
                    ("Auditor:innen suchen Schuldige, also möglichst wenig sagen", False),
                    ("Auditor:innen suchen Belege, dass Prozesse funktionieren — ehrlich antworten", True),
                    ("Auswendig gelernte Sätze sind die beste Strategie", False),
                    ("Nur die GF darf mit Auditor:innen sprechen", False),
                ),
            ),
        ),
    ),
)


__all__ = (
    "KATALOG",
    "FrageDef",
    "KursDef",
    "ModulDef",
    "OptionDef",
)
