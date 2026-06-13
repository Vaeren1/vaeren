"""Streaming ZIP-Bundle-Builder mit HMAC-signiertem Manifest.

Spec §8. Memory-Footprint < 200 MB für 1000-Evidence-Szenario (Test-Gate).
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import logging
import os
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auditor_export.aggregators import EvidenceRecord
    from auditor_export.models import AuditExportRun

logger = logging.getLogger(__name__)

CHUNK_SIZE = 4096


@dataclass
class ZipFileEntry:
    """Manifest-Eintrag pro File im Bundle."""

    path: str
    sha256: str
    size: int


def _canonical_json(data: dict) -> bytes:
    """Sorted-keys, no-whitespace JSON für HMAC-Input. Deterministisch."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def build_manifest(
    *,
    run: AuditExportRun,
    tenant_schema: str,
    tenant_firma: str,
    file_entries: list[ZipFileEntry],
    audit_log_chain_head: str = "",
    vaeren_version: str = "1.4.0",
) -> dict:
    """Erzeugt das Manifest-Dict (ohne Signatur)."""
    profile = run.profile
    return {
        "mappe_id": run.mappe_id,
        "generated_at": (run.started_at or run.finished_at).isoformat()
        if run.started_at
        else "",
        "tenant": tenant_schema,
        "tenant_firma": tenant_firma,
        "vaeren_version": vaeren_version,
        "profile": {
            "name": profile.name,
            "template": profile.template,
            "norm_scope": list(profile.norm_scope or []),
            "zeitraum_von": str(profile.zeitraum_von),
            "zeitraum_bis": str(profile.zeitraum_bis),
            "evidence_mode": profile.evidence_mode,
            "anonymisieren_pii": profile.anonymisieren_pii,
        },
        "files": [
            {"path": e.path, "sha256": e.sha256, "size": e.size} for e in file_entries
        ],
        "audit_log_chain_head": audit_log_chain_head,
        "evidence_count": run.evidence_count,
    }


def sign_manifest(manifest: dict, signing_key: bytes) -> dict:
    """Berechnet HMAC-SHA256 und ergänzt das `signature`-Feld.

    Signed-Fields: alle Manifest-Felder außer `signature` selbst.
    """
    canonical = _canonical_json(manifest)
    sig = hmac.new(signing_key, canonical, hashlib.sha256).hexdigest()
    return {
        **manifest,
        "signature": {
            "algorithm": "HMAC-SHA256",
            "value": sig,
            "signed_fields": sorted(manifest.keys()),
        },
    }


def verify_signature(signed_manifest: dict, signing_key: bytes) -> bool:
    """Prüft eine signierte Manifest-Struktur. Constant-Time-Compare."""
    sig_block = signed_manifest.get("signature")
    if not sig_block or sig_block.get("algorithm") != "HMAC-SHA256":
        return False
    expected_value = sig_block.get("value", "")

    # Manifest ohne signature-Block für Re-Hash
    bare = {k: v for k, v in signed_manifest.items() if k != "signature"}
    canonical = _canonical_json(bare)
    actual_value = hmac.new(signing_key, canonical, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_value, actual_value)


class ZIPBuilder:
    """Streaming ZIP-Builder. Erzeugt audit-mappe-<MAPPE>.zip mit Manifest."""

    def __init__(
        self,
        *,
        run: AuditExportRun,
        tenant_schema: str,
        tenant_firma: str,
        signing_key: bytes,
        target_dir: Path,
        records: list[EvidenceRecord],
        pdf_bytes: bytes | None = None,
        ssp_json: dict | None = None,
        ar_json: dict | None = None,
        audit_log_chain_head: str = "",
        audit_log_chain_entries: list[dict] | None = None,
        evidence_mode: str = "embed",
    ) -> None:
        self.run = run
        self.tenant_schema = tenant_schema
        self.tenant_firma = tenant_firma
        self.signing_key = signing_key
        self.target_dir = target_dir
        self.records = records
        self.pdf_bytes = pdf_bytes
        self.ssp_json = ssp_json
        self.ar_json = ar_json
        self.audit_log_chain_head = audit_log_chain_head
        self.audit_log_chain_entries = audit_log_chain_entries or []
        self.evidence_mode = evidence_mode

    def _write_entry(
        self, zf: zipfile.ZipFile, arcname: str, data: bytes
    ) -> ZipFileEntry:
        """Schreibt Bytes als Entry, gibt Manifest-Entry zurück."""
        zf.writestr(arcname, data)
        return ZipFileEntry(
            path=arcname,
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
        )

    def _write_stream_entry(
        self, zf: zipfile.ZipFile, arcname: str, source_path: Path
    ) -> ZipFileEntry:
        """Streamt Source-Datei chunk-weise in das ZIP."""
        sha = hashlib.sha256()
        size = 0
        with source_path.open("rb") as src:
            # zipfile.open() unterstützt streaming-Schreiben seit Python 3.6
            with zf.open(arcname, mode="w", force_zip64=True) as dst:
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sha.update(chunk)
                    dst.write(chunk)
                    size += len(chunk)
        return ZipFileEntry(path=arcname, sha256=sha.hexdigest(), size=size)

    _CHAIN_CSV_COLUMNS = (
        "id",
        "timestamp",
        "actor_email_snapshot",
        "aktion",
        "target_content_type",
        "target_object_id",
        "entry_sha256",
        "chain_hash",
    )

    def _render_chain_csv(self) -> str:
        """Serialisiert die AuditLog-Hash-Chain als CSV.

        Ermöglicht einem Auditor, `audit_log_chain_head` aus dem Manifest selbst
        nachzurechnen. Bei leerer Chain bleibt nur die Header-Zeile.
        """
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=self._CHAIN_CSV_COLUMNS, extrasaction="ignore"
        )
        writer.writeheader()
        for entry in self.audit_log_chain_entries:
            writer.writerow(entry)
        return buf.getvalue()

    def build(self) -> tuple[Path, str, int]:
        """Baut das ZIP-Bundle, signiert das Manifest, schreibt es als letzte Entry.

        Returns: (path, file_sha256, size_bytes).
        """
        self.target_dir.mkdir(parents=True, exist_ok=True)
        zip_path = self.target_dir / f"audit-mappe-{self.run.mappe_id}.zip"

        # Pass 1: Wir sammeln Entries durch Schreiben in ein ZIP.
        # Manifest wird im selben Pass am Ende geschrieben (mit aktualisierten Hashes).
        entries: list[ZipFileEntry] = []

        with zipfile.ZipFile(
            zip_path, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
        ) as zf:
            # 1. PDF
            if self.pdf_bytes:
                entries.append(self._write_entry(zf, "audit-mappe.pdf", self.pdf_bytes))

            # 2. OSCAL JSON
            if self.ssp_json:
                ssp_bytes = json.dumps(
                    self.ssp_json, indent=2, sort_keys=True, ensure_ascii=False
                ).encode("utf-8")
                entries.append(
                    self._write_entry(zf, "oscal/system-security-plan.json", ssp_bytes)
                )
            if self.ar_json:
                ar_bytes = json.dumps(
                    self.ar_json, indent=2, sort_keys=True, ensure_ascii=False
                ).encode("utf-8")
                entries.append(
                    self._write_entry(zf, "oscal/assessment-results.json", ar_bytes)
                )

            # 3. Evidence-Files
            if self.evidence_mode == "embed":
                for record in self.records:
                    for ef in record.evidence_files:
                        arc = f"evidence/{record.aggregator_slug}/{record.record_id}/{ef.filename}".replace(
                            ":", "_"
                        )
                        if ef.inline_bytes is not None:
                            entries.append(
                                self._write_entry(zf, arc, ef.inline_bytes)
                            )
                        elif ef.absolute_path:
                            src = Path(ef.absolute_path)
                            if src.exists():
                                entries.append(self._write_stream_entry(zf, arc, src))
                            else:
                                logger.warning(
                                    "Evidence-File nicht gefunden: %s", ef.absolute_path
                                )

            # 4. README für Auditoren
            readme = (
                f"Vaeren — Audit-Mappe {self.run.mappe_id}\n"
                f"=========================================\n\n"
                f"Tenant: {self.tenant_schema}\n"
                f"Firma: {self.tenant_firma}\n\n"
                f"Verify: https://app.vaeren.de/verify?mappe={self.run.mappe_id}\n\n"
                f"Inhalt:\n"
                f"- audit-mappe.pdf           — Hauptdokument (PDF/A-3-Ziel)\n"
                f"- oscal/                    — NIST-OSCAL-1.1.2-Subset JSON\n"
                f"- evidence/<modul>/<rec>/   — Original-Belege (encrypted bleibt encrypted)\n"
                f"- manifest.json             — HMAC-signiertes Inventar\n"
                f"- audit-log-chain.csv       — Hash-Chain-Auszug (verifiziert chain_head)\n\n"
            )
            entries.append(self._write_entry(zf, "README.txt", readme.encode("utf-8")))

            # 4b. AuditLog-Hash-Chain als CSV (vom README versprochen, früher nie
            # geschrieben → Chain war ohne Datenbasis nicht nachvollziehbar). Wird
            # in `entries` aufgenommen, also von der Manifest-Signatur abgedeckt.
            chain_csv = self._render_chain_csv()
            entries.append(
                self._write_entry(zf, "audit-log-chain.csv", chain_csv.encode("utf-8"))
            )

            # 5. Manifest (mit Signatur, als letzte Entry)
            manifest = build_manifest(
                run=self.run,
                tenant_schema=self.tenant_schema,
                tenant_firma=self.tenant_firma,
                file_entries=entries,
                audit_log_chain_head=self.audit_log_chain_head,
            )
            signed = sign_manifest(manifest, self.signing_key)
            manifest_bytes = json.dumps(
                signed, indent=2, sort_keys=True, ensure_ascii=False
            ).encode("utf-8")
            zf.writestr("manifest.json", manifest_bytes)

        # SHA-256 des fertigen ZIPs
        file_sha = hashlib.sha256()
        with zip_path.open("rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                file_sha.update(chunk)
        size = zip_path.stat().st_size
        return zip_path, file_sha.hexdigest(), size
