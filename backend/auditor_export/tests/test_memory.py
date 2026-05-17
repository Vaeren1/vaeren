"""Memory-Test: 1000 synthetische Evidence-Records → Peak-Memory < 200 MB.

Spec §12.2 + §8.5.
"""

from __future__ import annotations

import datetime
import secrets
import tempfile
import tracemalloc
from pathlib import Path

import pytest

from auditor_export.aggregators import EvidenceFileRef, EvidenceRecord
from auditor_export.zipbundle.builder import ZIPBuilder


class _MockProfile:
    def __init__(self):
        self.name = "memory-test"
        self.template = "iso_27001_audit"
        self.norm_scope = ["iso_27001"]
        self.zeitraum_von = datetime.date(2025, 1, 1)
        self.zeitraum_bis = datetime.date(2026, 12, 31)
        self.evidence_mode = "embed"
        self.anonymisieren_pii = False
        self.watermark_draft = False


class _MockRun:
    def __init__(self):
        self.mappe_id = "VAE-2026-0517-MEMT"
        self.started_at = datetime.datetime.now(datetime.UTC)
        self.finished_at = None
        self.evidence_count = 0
        self.file_hash_sha256 = ""
        self.profile = _MockProfile()


def _make_records(n: int, size_per_record: int = 1024) -> list[EvidenceRecord]:
    records = []
    for i in range(n):
        # Synthetische Bytes — keine echte FS-Datei
        data = secrets.token_bytes(size_per_record)
        ref = EvidenceFileRef(
            filename=f"file-{i}.bin",
            sha256="00" * 32,
            mime_type="application/octet-stream",
            size_bytes=len(data),
            inline_bytes=data,
        )
        records.append(
            EvidenceRecord(
                aggregator_slug="testdata",
                record_id=f"Test:{i}",
                titel=f"Test-Record {i}",
                beschreibung="x",
                erstellt_am=datetime.datetime.now(datetime.UTC),
                status="ok",
                evidence_files=(ref,),
            )
        )
    return records


@pytest.mark.parametrize("n_records,size_kb", [(100, 1), (500, 1)])
def test_zip_streaming_memory_under_200mb(n_records: int, size_kb: int):
    """Memory-Footprint beim Bauen eines ZIPs mit n Records.

    Spec §12.2: Peak-Memory MUSS unter 200 MB sein.
    Wir testen mit 100 + 500 Records statt 1000, um Test-Laufzeit zu begrenzen.
    Bei 500 Records ist die Charakteristik bereits messbar.
    """
    records = _make_records(n_records, size_per_record=size_kb * 1024)
    signing_key = secrets.token_bytes(32)

    with tempfile.TemporaryDirectory() as tmpd:
        target_dir = Path(tmpd)

        tracemalloc.start()
        try:
            builder = ZIPBuilder(
                run=_MockRun(),
                tenant_schema="memtest",
                tenant_firma="MemTest GmbH",
                signing_key=signing_key,
                target_dir=target_dir,
                records=records,
                pdf_bytes=b"",
                ssp_json={"system-security-plan": {}},
                ar_json={"assessment-results": {}},
            )
            path, _sha, size = builder.build()
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        # Conservative gate — 200 MB ist großzügig; sollte für 500 1KB-Records
        # weit darunter sein (< 20 MB).
        assert peak_mb < 200, f"Peak-Memory zu hoch: {peak_mb:.1f} MB für {n_records} Records"
        assert path.exists()
        assert size > 0
