"""Management-Command: Demo-VDA-ISA-Fragebogen seeden (OEM-Fragebogen-Auswerter).

Erzeugt zur Laufzeit (kein committetes Binär-Asset) ein kleines VDA-ISA-artiges
``.xlsx`` mit ~7 typischen Lieferanten-Sicherheitsfragen (openpyxl), legt daraus
einen ``Fragebogen`` an, extrahiert die Fragen über den echten Tier-1-Pfad
(``erkenne_format_und_tier`` + ``extrahiere_fragen_xlsx``), seedet vorab ein paar
Antwort-Bibliothek-Einträge und erzeugt Antwort-Entwürfe.

WICHTIG — läuft OHNE echten LLM-Key:
    In Prod ist beim Seed evtl. kein OPENROUTER/ANTHROPIC-Key gesetzt. ``generate()``
    liefert dann den (leeren) ``static_fallback`` → ``entwerfe_antwort`` würde nur
    "Keine automatische Antwort möglich" produzieren. Damit die Demo trotzdem
    plausible Entwürfe zeigt, wird hier zuerst die Bibliothek befüllt und der
    Entwurfstext deterministisch aus dem Bibliothek-Treffer abgeleitet, wenn die
    Engine keinen echten LLM-Text liefert. Es findet KEIN echter LLM-Call statt,
    der für die Demo nötig wäre — der Pfad ist nur ein Bonus, wenn ein Key da ist.

Der Fragebogen bleibt im Status ``vorgeschlagen`` (bzw. ``in_review`` falls bereits
Seiten bestätigt) — der Mensch attestiert in der Live-Demo. Module/Export werden
bewusst NICHT automatisch ausgeführt.

Idempotent:
- Fragebogen via ``update_or_create`` auf ``dateiname=DEMO_DATEINAME``.
- Alte Fragen (→ Antworten/Quellen via CASCADE) werden vor Neuaufbau gelöscht.
- Bibliothek-Einträge via ``update_or_create`` auf ``frage_kanonisch``.
- Zweiter Lauf → genau 1 Fragebogen.

Aufruf (im Tenant-Schema):
    python manage.py seed_fragebogen_demo --schema=demo
oder ohne --schema, wenn das Schema bereits via ``schema_context`` gesetzt ist
(z.B. in Tests).
"""

from __future__ import annotations

import tempfile
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context

from fragebogen import bibliothek
from fragebogen.answer_engine import entwerfe_antwort
from fragebogen.evidence_pool import sammle_evidenz
from fragebogen.ingestion.detect import erkenne_format_und_tier
from fragebogen.ingestion.extract_xlsx import extrahiere_fragen_xlsx
from fragebogen.models import (
    Antwort,
    AntwortBibliothekEintrag,
    AntwortQuelle,
    Fragebogen,
    FragebogenStatus,
)

DEMO_DATEINAME = "demo-vda-isa.xlsx"
DEMO_OEM = "Beispiel Automotive OEM AG"

# (Nummer, Frage, Kategorie). Antwortspalte bleibt im Template leer — die füllt
# der Auswerter. Bewusst kurz gehalten (7 typische VDA-ISA-/TISAX-Fragen).
DEMO_FRAGEN: list[tuple[str, str, str]] = [
    ("1.1", "Ist ein Informationssicherheits-Managementsystem (ISMS) etabliert?", "ISMS"),
    ("1.2", "Existiert eine dokumentierte Zugriffskontrolle für IT-Systeme?", "Zugriffskontrolle"),
    ("1.3", "Werden regelmäßige Datensicherungen durchgeführt und getestet?", "Datensicherung"),
    ("1.4", "Gibt es einen Prozess für das Incident-Management (Sicherheitsvorfälle)?", "Incident-Management"),
    ("1.5", "Werden Lieferanten / Subunternehmer auf Informationssicherheit geprüft?", "Lieferantenkontrolle"),
    ("1.6", "Ist ein Datenschutzbeauftragter benannt?", "Datenschutz"),
    ("1.7", "Werden Mitarbeitende regelmäßig zur Informationssicherheit geschult?", "Awareness"),
]

# Vorab-Bibliothek: (kanonische Frage, plausible Antwort, Quellen-Referenzen, Kategorie).
# Diese Einträge liefern die deterministischen Demo-Entwürfe (ohne LLM-Key).
DEMO_BIBLIOTHEK: list[tuple[str, str, list[str], str]] = [
    (
        "Ist ein Informationssicherheits-Managementsystem (ISMS) etabliert?",
        "Ja, ein ISMS nach ISO/IEC 27001 ist etabliert und seit 2025 in Betrieb.",
        ["iso27001:A.5.1"],
        "ISMS",
    ),
    (
        "Existiert eine dokumentierte Zugriffskontrolle für IT-Systeme?",
        "Ja, der Zugriff erfolgt rollenbasiert nach dem Least-Privilege-Prinzip; "
        "Berechtigungen werden regelmäßig überprüft.",
        ["iso27001:A.8.2"],
        "Zugriffskontrolle",
    ),
    (
        "Werden regelmäßige Datensicherungen durchgeführt und getestet?",
        "Ja, tägliche verschlüsselte Backups mit dokumentierter Aufbewahrung; "
        "Wiederherstellungstests erfolgen periodisch.",
        ["iso27001:A.8.13"],
        "Datensicherung",
    ),
    (
        "Gibt es einen Prozess für das Incident-Management (Sicherheitsvorfälle)?",
        "Ja, Sicherheitsvorfälle werden über einen dokumentierten Incident-Prozess "
        "erfasst, bewertet und nachverfolgt.",
        ["iso27001:A.5.24"],
        "Incident-Management",
    ),
    (
        "Werden Lieferanten / Subunternehmer auf Informationssicherheit geprüft?",
        "Ja, Lieferanten werden vor Beauftragung und periodisch hinsichtlich "
        "Informationssicherheit bewertet.",
        ["iso27001:A.5.19"],
        "Lieferantenkontrolle",
    ),
    (
        "Ist ein Datenschutzbeauftragter benannt?",
        "Ja, ein Datenschutzbeauftragter ist benannt und der Aufsichtsbehörde gemeldet.",
        ["profil:datenschutz"],
        "Datenschutz",
    ),
    (
        "Werden Mitarbeitende regelmäßig zur Informationssicherheit geschult?",
        "Ja, alle Mitarbeitenden absolvieren regelmäßige Awareness-Schulungen zur "
        "Informationssicherheit.",
        ["iso27001:A.6.3"],
        "Awareness",
    ),
]


class Command(BaseCommand):
    help = (
        "Seedet einen Demo-VDA-ISA-Fragebogen (programmatisch erzeugte xlsx) inkl. "
        "Bibliothek-Einträgen und Antwort-Entwürfen. Läuft ohne LLM-Key. Lässt den "
        "Fragebogen in_review/vorgeschlagen — Mensch attestiert in der Demo live; "
        "Module/Export werden NICHT automatisch ausgeführt."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            default=None,
            help="Schema-Name des Tenants. Ohne Angabe läuft das Command im aktuellen Schema.",
        )

    def handle(self, *args, **opts):
        schema = opts.get("schema")
        ctx = schema_context(schema) if schema else nullcontext()
        with ctx:
            fb = self._seed()
            # Alle count()-Querys INNERHALB des Schema-Kontexts (Feature-1-Lehre:
            # außerhalb läuft es im public-Schema, wo die Tenant-Tabellen fehlen).
            n_fragen = fb.fragen.count()
            n_entwuerfe = Antwort.objects.filter(frage__fragebogen=fb).count()
            n_bib = AntwortBibliothekEintrag.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Demo-Fragebogen '{fb.dateiname}' geseedet "
                    f"(Tier {fb.tier}, Status {fb.status}): "
                    f"{n_fragen} Fragen, {n_entwuerfe} Antwort-Entwürfe, "
                    f"{n_bib} Bibliothek-Einträge. "
                    "Status in_review/vorgeschlagen — Attestierung erfolgt in der Demo."
                )
            )

    # --- Seed-Schritte --------------------------------------------------------

    def _seed(self) -> Fragebogen:
        self._seed_bibliothek()
        xlsx_bytes = self._baue_demo_xlsx()

        fb, _created = Fragebogen.objects.update_or_create(
            dateiname=DEMO_DATEINAME,
            defaults={
                "format": "xlsx",
                "tier": 1,
                "quelle_oem": DEMO_OEM,
                "status": FragebogenStatus.HOCHGELADEN,
            },
        )
        # Idempotenz: alte Datei + Fragen (→ Antworten/Quellen via CASCADE) entfernen.
        if fb.original_datei:
            fb.original_datei.delete(save=False)
        fb.fragen.all().delete()
        fb.original_datei.save(DEMO_DATEINAME, ContentFile(xlsx_bytes), save=True)

        # Format/Tier über den echten Detect-Pfad bestimmen (xlsx → Tier 1).
        fb.format, fb.tier = self._detect(xlsx_bytes)
        fb.save(update_fields=["format", "tier"])

        self._extrahiere_und_entwerfe(fb)

        fb.status = FragebogenStatus.VORGESCHLAGEN
        fb.save(update_fields=["status"])
        return fb

    def _seed_bibliothek(self) -> None:
        for frage_kanonisch, antwort_text, refs, kategorie in DEMO_BIBLIOTHEK:
            AntwortBibliothekEintrag.objects.update_or_create(
                frage_kanonisch=frage_kanonisch,
                defaults={
                    "antwort_text": antwort_text,
                    "quelle_referenzen": refs,
                    "kategorie": kategorie,
                },
            )

    def _baue_demo_xlsx(self) -> bytes:
        """Baut ein VDA-ISA-artiges xlsx im Speicher (kein committetes Asset)."""
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ISA"
        ws.append(["Nr", "Frage", "Antwort"])
        for nummer, frage, _kategorie in DEMO_FRAGEN:
            ws.append([nummer, frage, ""])
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    def _detect(self, xlsx_bytes: bytes) -> tuple[str, int]:
        """Schreibt die Bytes in eine temp .xlsx und lässt sie detecten."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp.write(xlsx_bytes)
            pfad = tmp.name
        try:
            return erkenne_format_und_tier(pfad)
        finally:
            Path(pfad).unlink(missing_ok=True)

    def _extrahiere_und_entwerfe(self, fb: Fragebogen) -> None:
        """Extrahiert Fragen aus der Original-xlsx + erzeugt Antwort-Entwürfe."""
        from fragebogen.models import AntwortStatus, Frage

        pfad = fb.original_datei.path
        roh_fragen = extrahiere_fragen_xlsx(pfad)
        # Kategorie-Lookup aus dem Seed (per Fragetext), damit die Frage-Records
        # die richtige Kategorie tragen.
        kategorie_map = {frage: kat for _nr, frage, kat in DEMO_FRAGEN}

        snippets = sammle_evidenz()

        for idx, roh in enumerate(roh_fragen, start=1):
            frage = Frage.objects.create(
                fragebogen=fb,
                reihenfolge=idx,
                seite=1,
                nummer=roh.get("nummer") or "",
                text=roh["text"],
                feld_referenz=roh.get("feld_referenz", {}),
                kategorie=kategorie_map.get(roh["text"], ""),
                extraktion_quelle="struktur",
            )

            treffer = bibliothek.finde_aehnlichen_eintrag(frage.text)
            res = entwerfe_antwort(frage.text, snippets, bibliothek_treffer=treffer)
            text, confidence, quellen, rdg_ok = self._plausibler_entwurf(res, treffer)

            antwort = Antwort.objects.create(
                frage=frage,
                entwurf_text=text,
                confidence=confidence,
                rdg_ok=rdg_ok,
                status=AntwortStatus.ENTWURF,
            )
            for snip in quellen:
                AntwortQuelle.objects.create(
                    antwort=antwort,
                    quelle_typ=snip.quelle_typ,
                    referenz=snip.referenz,
                    auszug=snip.text[:2000],
                )

            if treffer is not None:
                from django.utils import timezone

                treffer.verwendungs_count = (treffer.verwendungs_count or 0) + 1
                treffer.zuletzt_verwendet = timezone.now()
                treffer.save(
                    update_fields=[
                        "verwendungs_count",
                        "zuletzt_verwendet",
                        "aktualisiert_at",
                    ]
                )

    def _plausibler_entwurf(self, res: dict, treffer):
        """Liefert (text, confidence, quellen, rdg_ok) — auch ohne echten LLM.

        ``entwerfe_antwort`` ruft das LLM. Ohne API-Key gibt ``generate()`` den
        leeren static_fallback zurück → ``res["text"]`` ist der Platzhalter
        "Keine automatische Antwort möglich …". In dem Fall (oder bei leerem Text)
        leiten wir den Entwurf deterministisch aus dem Bibliothek-Treffer ab, damit
        die Demo plausible Antworten zeigt. Liegt ein echter LLM-Text vor, wird der
        bevorzugt (mit der von der Engine berechneten Confidence/Quellen).
        """
        text = (res.get("text") or "").strip()
        engine_hat_echte_antwort = bool(text) and not text.startswith(
            "Keine automatische Antwort möglich"
        )

        if engine_hat_echte_antwort:
            return text, res.get("confidence", 0.0), res.get("quellen", []), res.get("rdg_ok", True)

        # Deterministischer Fallback aus dem Bibliothek-Treffer.
        if treffer is not None:
            from fragebogen.evidence_pool import EvidenzSnippet

            quelle = EvidenzSnippet(
                quelle_typ="bibliothek",
                referenz=str(treffer.id),
                titel=f"Bibliothek: {treffer.frage_kanonisch[:60]}",
                text=treffer.antwort_text,
            )
            # Bibliothek ist human-bestätigtes Wissen → Confidence 0.7.
            return treffer.antwort_text, 0.7, [quelle], True

        # Weder LLM noch Bibliothek: ehrlicher Leer-Entwurf, niedrige Confidence.
        return (
            "Bitte selbst ausfüllen — keine passende Evidenz im Pool gefunden.",
            0.0,
            [],
            True,
        )
