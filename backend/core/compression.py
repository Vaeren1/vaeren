"""Smart-Compression-Service fuer Kurs-Asset-Uploads.

Strategie:
- PDF: ghostscript -dPDFSETTINGS=/ebook (downsampled auf 150dpi, Bilder
  JPEG-recodiert q=80). Typisch 40-70 % Groessenreduktion.
- Bild (PNG/JPG): Pillow re-encode JPEG q=85, max 2048 px Kante.
- Video (MP4): ffmpeg libx264 CRF 23 preset medium, scale max 1080p,
  AAC 128k. Typisch 50-70 % Reduktion ohne sichtbare Quali-Einbusse.

Alle Funktionen sind in-place (ueberschreiben Original) und idempotent —
wenn das Ergebnis groesser/aehnlich gross als Original waere, behalten
wir das Original und melden 'skipped'.

Aufruf aus Celery-Tasks. Lokal getestet via Fixture-Files.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Skip-Kompression unterhalb dieser Groesse (kein lohnender Gewinn).
PDF_MIN_BYTES = 1 * 1024 * 1024  # 1 MB
IMAGE_MIN_BYTES = 200 * 1024  # 200 KB
VIDEO_MIN_BYTES = 5 * 1024 * 1024  # 5 MB

# Behalten Original, wenn Komprimierung weniger als X % einspart.
MIN_SAVINGS_PERCENT = 10


@dataclass
class CompressionResult:
    status: str  # 'done' | 'skipped' | 'failed'
    original_size: int
    compressed_size: int
    error: str = ""

    @property
    def savings_percent(self) -> float:
        if self.original_size == 0:
            return 0.0
        return (1.0 - self.compressed_size / self.original_size) * 100.0


def _replace_if_smaller(original: Path, candidate: Path) -> CompressionResult:
    """Tausche Original gegen candidate, wenn candidate genug kleiner ist."""
    if not candidate.exists():
        return CompressionResult("failed", original.stat().st_size, 0, "candidate fehlt")
    orig_size = original.stat().st_size
    new_size = candidate.stat().st_size
    savings = (1.0 - new_size / orig_size) * 100.0 if orig_size else 0.0
    if savings < MIN_SAVINGS_PERCENT:
        candidate.unlink(missing_ok=True)
        return CompressionResult("skipped", orig_size, new_size)
    shutil.move(str(candidate), str(original))
    return CompressionResult("done", orig_size, new_size)


def compress_pdf(path: Path) -> CompressionResult:
    """ghostscript -dPDFSETTINGS=/ebook. Idempotent."""
    if not path.exists():
        return CompressionResult("failed", 0, 0, "Datei fehlt")
    size = path.stat().st_size
    if size < PDF_MIN_BYTES:
        return CompressionResult("skipped", size, size)

    out = path.with_suffix(".compressed.pdf")
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={out}",
        str(path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError as e:
        return CompressionResult("failed", size, 0, e.stderr.decode("utf-8", "replace")[:200])
    except subprocess.TimeoutExpired:
        return CompressionResult("failed", size, 0, "timeout")
    except FileNotFoundError:
        return CompressionResult("failed", size, 0, "ghostscript nicht installiert")
    return _replace_if_smaller(path, out)


def compress_image(path: Path, max_dimension: int = 2048, jpeg_quality: int = 85) -> CompressionResult:
    """Pillow re-encode auf JPEG q=85, max 2048 px Kante."""
    if not path.exists():
        return CompressionResult("failed", 0, 0, "Datei fehlt")
    size = path.stat().st_size
    if size < IMAGE_MIN_BYTES:
        return CompressionResult("skipped", size, size)

    try:
        from PIL import Image  # type: ignore[import-not-found]
    except ImportError:
        return CompressionResult("failed", size, 0, "Pillow nicht installiert")

    out = path.with_suffix(".compressed.jpg")
    try:
        with Image.open(path) as im:
            im = im.convert("RGB") if im.mode in ("RGBA", "P", "LA") else im
            # Resize wenn groesste Kante > max_dimension
            longest = max(im.size)
            if longest > max_dimension:
                ratio = max_dimension / longest
                new_size = (int(im.size[0] * ratio), int(im.size[1] * ratio))
                im = im.resize(new_size, Image.Resampling.LANCZOS)
            im.save(out, format="JPEG", quality=jpeg_quality, optimize=True, progressive=True)
    except Exception as e:  # noqa: BLE001  # Pillow wirft viele Sub-Typen
        return CompressionResult("failed", size, 0, str(e)[:200])
    return _replace_if_smaller(path, out)


def convert_office_to_pdf(src: Path, dest_dir: Path) -> tuple[Path | None, str]:
    """Konvertiert DOCX/PPTX zu PDF via headless soffice.

    Returns (pdf_path, error). pdf_path ist None bei Fehler.
    """
    if not src.exists():
        return None, "Datei fehlt"
    dest_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "soffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "pdf",
        "--outdir", str(dest_dir),
        str(src),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError as e:
        return None, e.stderr.decode("utf-8", "replace")[:300]
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except FileNotFoundError:
        return None, "soffice nicht installiert"
    expected = dest_dir / (src.stem + ".pdf")
    if not expected.exists():
        return None, f"PDF nicht erstellt (erwartet: {expected})"
    return expected, ""


def compress_video(path: Path, max_height: int = 1080, crf: int = 23) -> CompressionResult:
    """ffmpeg libx264 CRF 23 preset medium, scale max 1080p, AAC 128k."""
    if not path.exists():
        return CompressionResult("failed", 0, 0, "Datei fehlt")
    size = path.stat().st_size
    if size < VIDEO_MIN_BYTES:
        return CompressionResult("skipped", size, size)

    out = path.with_suffix(".compressed.mp4")
    # Scale-Filter: nur runterskalieren, nie hoch; sicherstellen dass Hoehe gerade ist.
    vf = f"scale='trunc(min(iw,iw*{max_height}/ih)/2)*2':'trunc(min(ih,{max_height})/2)*2'"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(path),
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-vf", vf,
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=1800)  # 30 min max
    except subprocess.CalledProcessError as e:
        return CompressionResult("failed", size, 0, e.stderr.decode("utf-8", "replace")[:300])
    except subprocess.TimeoutExpired:
        return CompressionResult("failed", size, 0, "timeout")
    except FileNotFoundError:
        return CompressionResult("failed", size, 0, "ffmpeg nicht installiert")
    return _replace_if_smaller(path, out)
