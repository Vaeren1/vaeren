"""Tier-2-Tests (Feature 4, Phase H): OCR-Extraktion + Overlay +
Vision-Review-Loop + Celery-Task.

ALLES Externe gemockt — KEIN echter OCR/Render/Vision/LLM-Call:
- ``pdf2image.convert_from_path`` / ``convert_from_bytes``
- ``pytesseract.image_to_data``
- ``_llm_segmentiere`` (OCR-Segmentierungs-LLM)
- ``_vision_review`` (Vision-LLM-Grenze)

Geprüft:
- H2: extrahiere_fragen_ocr aggregiert Tesseract-Blöcke + LLM-Segmentierung zu
  Frage-Dicts mit feld_referenz={seite, bbox, schrift_pt}.
- H3: Overlay-Merge (reportlab+pypdf, lokal/deterministisch).
- H3: Vision-Review-Loop — Konvergenz (ok), Nachjustierung, Nicht-Konvergenz →
  Feld als unsicher markiert.
- H3: Celery-Task Status-Übergänge (laeuft→fertig / →fehler) + Notification.
"""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest
from django_tenants.utils import schema_context

from fragebogen.export import fill_unstructured
from fragebogen.export.fill_unstructured import (
    CONFIDENCE_OK,
    CONFIDENCE_UNSICHER,
    MAX_REVIEW_RUNDEN,
    platziere_antwort,
    platziere_mit_review,
)
from fragebogen.ingestion.extract_ocr import extrahiere_fragen_ocr

# --------------------------------------------------------------------------- #
# Helfer                                                                       #
# --------------------------------------------------------------------------- #


def _einfaches_pdf(seiten: int = 1) -> bytes:
    """Erzeugt ein minimales mehrseitiges PDF (lokal, kein Netz)."""
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(595, 842))  # A4 in pt
    for i in range(seiten):
        c.drawString(72, 800, f"Seite {i + 1} - Frage?")
        c.showPage()
    c.save()
    return buf.getvalue()


def _fake_tesseract_dict():
    """Simuliert pytesseract.image_to_data(output_type=DICT) für zwei Zeilen."""
    return {
        "text": ["Haben", "Sie", "ein", "ISMS?", "", "Antwort:"],
        "conf": ["90", "91", "88", "95", "-1", "80"],
        "block_num": [1, 1, 1, 1, 0, 2],
        "par_num": [1, 1, 1, 1, 0, 1],
        "line_num": [1, 1, 1, 1, 0, 1],
        "left": [100, 160, 210, 250, 0, 100],
        "top": [100, 100, 100, 100, 0, 140],
        "width": [50, 40, 30, 60, 0, 80],
        "height": [20, 20, 20, 20, 0, 20],
    }


# --------------------------------------------------------------------------- #
# H2: OCR-Extraktion                                                           #
# --------------------------------------------------------------------------- #


def test_ocr_extraktion_mockt_tesseract_und_llm():
    """OCR-Blöcke + LLM-Segmentierung → Frage-Dict mit Bbox + Schriftgröße."""
    fake_bild = object()  # PIL-Bild wird nie wirklich genutzt (alles gemockt)

    with patch("fragebogen.ingestion.extract_ocr.convert_from_path", return_value=[fake_bild]), \
         patch("pytesseract.image_to_data", return_value=_fake_tesseract_dict()), \
         patch(
             "fragebogen.ingestion.extract_ocr._llm_segmentiere",
             return_value=[
                 {"nummer": "1", "text": "Haben Sie ein ISMS?",
                  "bbox": [180, 140, 200, 24], "schrift_pt": 11},
             ],
         ):
        fragen = extrahiere_fragen_ocr("/tmp/egal.pdf")

    assert len(fragen) == 1
    f = fragen[0]
    assert f["text"] == "Haben Sie ein ISMS?"
    assert f["extraktion_quelle"] == "ocr"
    assert f["feld_referenz"]["seite"] == 1
    assert f["feld_referenz"]["bbox"] == [180, 140, 200, 24]
    assert f["feld_referenz"]["schrift_pt"] == 11


def test_ocr_extraktion_blocke_aus_tesseract_gruppiert():
    """Wörter mit gleicher (block,par,line) werden zu einem Block gefasst; die
    LLM-Grenze bekommt die gruppierten Blöcke."""
    fake_bild = object()
    gesehen: list[list[dict]] = []

    def faker(seiten_nr, bloecke):
        gesehen.append(bloecke)
        return []

    with patch("fragebogen.ingestion.extract_ocr.convert_from_path", return_value=[fake_bild]), \
         patch("pytesseract.image_to_data", return_value=_fake_tesseract_dict()), \
         patch("fragebogen.ingestion.extract_ocr._llm_segmentiere", side_effect=faker):
        extrahiere_fragen_ocr("/tmp/egal.pdf")

    bloecke = gesehen[0]
    texte = {b["text"] for b in bloecke}
    assert "Haben Sie ein ISMS?" in texte  # 4 Wörter → 1 Block
    assert "Antwort:" in texte
    assert all(len(b["bbox"]) == 4 for b in bloecke)


def test_ocr_extraktion_render_fehler_gibt_leere_liste():
    """Ein PDF-Render-Fehler darf nie hochblubbern."""
    with patch(
        "fragebogen.ingestion.extract_ocr.convert_from_path",
        side_effect=OSError("poppler kaputt"),
    ):
        assert extrahiere_fragen_ocr("/tmp/kaputt.pdf") == []


def test_ocr_extraktion_ungueltige_bbox_uebersprungen():
    """LLM liefert eine kaputte Bbox → diese Frage wird verworfen, nicht crash."""
    fake_bild = object()
    with patch("fragebogen.ingestion.extract_ocr.convert_from_path", return_value=[fake_bild]), \
         patch("pytesseract.image_to_data", return_value=_fake_tesseract_dict()), \
         patch(
             "fragebogen.ingestion.extract_ocr._llm_segmentiere",
             return_value=[
                 {"text": "kaputt", "bbox": [1, 2, 3], "schrift_pt": 10},  # nur 3 Werte
                 {"text": "ok", "bbox": [1, 2, 3, 4], "schrift_pt": 999},  # Schrift out-of-range
             ],
         ):
        fragen = extrahiere_fragen_ocr("/tmp/egal.pdf")

    assert len(fragen) == 1
    assert fragen[0]["text"] == "ok"
    assert fragen[0]["feld_referenz"]["schrift_pt"] == 10.0  # Default bei out-of-range


# --------------------------------------------------------------------------- #
# H3: Overlay-Platzierung                                                      #
# --------------------------------------------------------------------------- #


def test_overlay_merge_erhoeht_nicht_seitenzahl():
    """Overlay wird auf vorhandene Seite gemerged — Seitenzahl bleibt gleich."""
    from pypdf import PdfReader

    original = _einfaches_pdf(seiten=2)
    neu = platziere_antwort(original, seiten_index=0, text="Ja, ISMS seit 2025.",
                            bbox=[100, 200, 200, 24], schrift_pt=11)
    reader = PdfReader(io.BytesIO(neu))
    assert len(reader.pages) == 2
    # Der Antwort-Text wurde tatsächlich auf Seite 1 gemerged (Original-Text bleibt).
    seite1_text = reader.pages[0].extract_text()
    assert "ISMS seit 2025" in seite1_text
    assert "Seite 1" in seite1_text
    # Seite 2 unberührt.
    assert "ISMS seit 2025" not in reader.pages[1].extract_text()


def test_overlay_leerer_text_unveraendert():
    """Leerer Text → keine Zeichnung (Seitenzahl bleibt, kein Fehler)."""
    from pypdf import PdfReader

    original = _einfaches_pdf(seiten=1)
    neu = platziere_antwort(original, seiten_index=0, text="", bbox=[0, 0, 0, 0], schrift_pt=10)
    assert len(PdfReader(io.BytesIO(neu)).pages) == 1


# --------------------------------------------------------------------------- #
# H3: Vision-Review-Loop                                                       #
# --------------------------------------------------------------------------- #


def test_review_loop_konvergiert_sofort():
    """Vision-Review sagt sofort ok → CONFIDENCE_OK, ein einziger Review-Call."""
    original = _einfaches_pdf()
    feld = {"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11}

    with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
         patch.object(fill_unstructured, "_vision_review",
                      return_value={"ok": True, "korrektur_bbox": None}) as mock_vr:
        _pdf, conf = platziere_mit_review(original, "Frage?", "Antwort.", feld)

    assert conf == CONFIDENCE_OK
    assert mock_vr.call_count == 1


def test_review_loop_justiert_dann_ok():
    """Erst nicht-ok mit Korrektur-Bbox, dann ok → konvergiert (CONFIDENCE_OK)."""
    original = _einfaches_pdf()
    feld = {"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11}
    urteile = [
        {"ok": False, "korrektur_bbox": [120, 260, 200, 24]},
        {"ok": True, "korrektur_bbox": None},
    ]

    with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
         patch.object(fill_unstructured, "_vision_review", side_effect=urteile) as mock_vr:
        _pdf, conf = platziere_mit_review(original, "Frage?", "Antwort.", feld)

    assert conf == CONFIDENCE_OK
    assert mock_vr.call_count == 2


def test_review_loop_nicht_konvergent_markiert_unsicher():
    """Vision-Review sagt nie ok (immer mit Korrektur) → Abbruch nach MAX_RUNDEN,
    Feld als unsicher markiert (CONFIDENCE_UNSICHER)."""
    original = _einfaches_pdf()
    feld = {"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11}

    with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
         patch.object(
             fill_unstructured, "_vision_review",
             return_value={"ok": False, "korrektur_bbox": [10, 20, 30, 40]},
         ) as mock_vr:
        _pdf, conf = platziere_mit_review(original, "Frage?", "Antwort.", feld)

    assert conf == CONFIDENCE_UNSICHER
    assert mock_vr.call_count == MAX_REVIEW_RUNDEN


def test_review_loop_nicht_ok_ohne_korrektur_bricht_ab():
    """Nicht-ok ohne Korrektur-Bbox → keine sinnvolle Nachjustierung → Abbruch."""
    original = _einfaches_pdf()
    feld = {"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11}

    with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
         patch.object(fill_unstructured, "_vision_review",
                      return_value={"ok": False, "korrektur_bbox": None}) as mock_vr:
        _pdf, conf = platziere_mit_review(original, "Frage?", "Antwort.", feld)

    assert conf == CONFIDENCE_UNSICHER
    assert mock_vr.call_count == 1


def test_review_loop_render_fehler_markiert_unsicher():
    """Ein Render-/Vision-Fehler in einer Runde → unsicher statt Crash."""
    original = _einfaches_pdf()
    feld = {"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11}

    with patch.object(fill_unstructured, "_rendere_seite", side_effect=RuntimeError("render kaputt")):
        _pdf, conf = platziere_mit_review(original, "Frage?", "Antwort.", feld)

    assert conf == CONFIDENCE_UNSICHER


# --------------------------------------------------------------------------- #
# H3: Celery-Task (DB)                                                         #
# --------------------------------------------------------------------------- #


@pytest.fixture
def tier2_tenant(db):
    from tenants.models import Tenant

    with schema_context("public"):
        t = Tenant.objects.create(schema_name="t_tier2", firma_name="Tier2 GmbH")
    yield t
    with schema_context("public"):
        t.delete(force_drop=True)


def _baue_tier2_fragebogen(settings, tmp_path):
    """Legt einen Tier-2-Fragebogen mit Original-PDF + einer freigegebenen Antwort an."""
    from django.core.files.base import ContentFile

    from core.models import User
    from fragebogen.models import (
        Antwort,
        AntwortStatus,
        Frage,
        Fragebogen,
        FragebogenStatus,
    )

    settings.MEDIA_ROOT = str(tmp_path)
    user = User.objects.create(email="gf@tier2.de", tenant_role="geschaeftsfuehrer")

    fb = Fragebogen.objects.create(
        dateiname="oem-scan.pdf",
        format="pdf_unstrukturiert",
        tier=2,
        status=FragebogenStatus.IN_REVIEW,
        hochgeladen_von=user,
        final_attestiert_von=user,
    )
    fb.original_datei.save("oem-scan.pdf", ContentFile(_einfaches_pdf()), save=True)

    frage = Frage.objects.create(
        fragebogen=fb,
        reihenfolge=1,
        seite=1,
        text="Haben Sie ein ISMS?",
        feld_referenz={"seite": 1, "bbox": [100, 200, 200, 24], "schrift_pt": 11},
        extraktion_quelle="ocr",
    )
    Antwort.objects.create(
        frage=frage,
        entwurf_text="Nach unserer Einschätzung: Ja. Bitte prüfen.",
        bestaetigt_text="Ja, ISMS seit 2025.",
        status=AntwortStatus.EDITIERT,
        confidence=0.8,
        rdg_ok=True,
    )
    return fb, user


@pytest.mark.django_db
def test_task_erfolg_status_und_notification(tier2_tenant, settings, tmp_path):
    """Erfolgs-Pfad: laeuft→fertig, export_datei gesetzt, Notification angelegt,
    Platzierungs-Confidence auf der Antwort vermerkt."""
    from core.models import Notification
    from fragebogen.models import FragebogenStatus
    from fragebogen.tasks import fragebogen_tier2_export

    with schema_context(tier2_tenant.schema_name):
        fb, _user = _baue_tier2_fragebogen(settings, tmp_path)

        with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
             patch.object(fill_unstructured, "_vision_review",
                          return_value={"ok": True, "korrektur_bbox": None}):
            result = fragebogen_tier2_export(fb.pk)

        assert result == "fertig"
        fb.refresh_from_db()
        assert fb.tier2_job_status == "fertig"
        assert fb.status == FragebogenStatus.EXPORTIERT
        assert bool(fb.export_datei)

        antwort = fb.fragen.first().antwort
        assert antwort.platzierung_confidence == CONFIDENCE_OK

        assert Notification.objects.filter(template="fragebogen_tier2_fertig").count() == 1


@pytest.mark.django_db
def test_task_nicht_konvergenz_markiert_feld_unsicher(tier2_tenant, settings, tmp_path):
    """Vision-Review konvergiert nicht → Export trotzdem fertig, aber
    platzierung_confidence der Antwort ist niedrig (Mensch prüft)."""
    from fragebogen.tasks import fragebogen_tier2_export

    with schema_context(tier2_tenant.schema_name):
        fb, _user = _baue_tier2_fragebogen(settings, tmp_path)

        with patch.object(fill_unstructured, "_rendere_seite", return_value=object()), \
             patch.object(
                 fill_unstructured, "_vision_review",
                 return_value={"ok": False, "korrektur_bbox": [10, 20, 30, 40]},
             ):
            result = fragebogen_tier2_export(fb.pk)

        assert result == "fertig"
        antwort = fb.fragen.first().antwort
        antwort.refresh_from_db()
        assert antwort.platzierung_confidence == CONFIDENCE_UNSICHER


@pytest.mark.django_db
def test_task_fehler_setzt_status_fehler(tier2_tenant, settings, tmp_path):
    """Ein Fehler im Overlay-Schritt → Status FEHLER + tier2_job_status='fehler'."""
    from fragebogen.models import FragebogenStatus
    from fragebogen.tasks import fragebogen_tier2_export

    with schema_context(tier2_tenant.schema_name):
        fb, _user = _baue_tier2_fragebogen(settings, tmp_path)

        with patch(
            "fragebogen.tasks.platziere_mit_review",
            side_effect=RuntimeError("overlay kaputt"),
        ):
            result = fragebogen_tier2_export(fb.pk)

        assert result == "fehler"
        fb.refresh_from_db()
        assert fb.tier2_job_status == "fehler"
        assert fb.status == FragebogenStatus.FEHLER


@pytest.mark.django_db
def test_task_unbekannter_fragebogen_gibt_fehler(tier2_tenant):
    from fragebogen.tasks import fragebogen_tier2_export

    with schema_context(tier2_tenant.schema_name):
        assert fragebogen_tier2_export(999999) == "fehler"
