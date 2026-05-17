"""Aggregator: HinSchG → §13, ISO-27001.A.5.4.

WICHTIG: Body bleibt encrypted! Wir lesen die rohen Fernet-Bytes direkt aus
der DB-Spalte, NICHT über die `EncryptedTextField.from_db_value()`-Schicht
(die würde entschlüsseln). Im ZIP-Bundle landen sie als `body.enc`.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from django.db import connection

from .base import (
    BaseAggregator,
    EvidenceFileRef,
    EvidenceRecord,
    REGISTRY,
    stable_uuid_v5,
)


class HinSchGAggregator(BaseAggregator):
    slug = "hinschg"
    norm_scopes = ("hinschg", "iso_27001", "nis2")

    def _read_raw_encrypted(self, meldung_pk: int) -> bytes:
        """Liest die roh-verschlüsselten Bytes der Meldung aus der DB.

        Vermeidet die `EncryptedTextField.from_db_value()`-Decryption.
        """
        with connection.cursor() as cur:
            cur.execute(
                "SELECT beschreibung_verschluesselt FROM hinschg_meldung WHERE id = %s",
                [meldung_pk],
            )
            row = cur.fetchone()
            if not row:
                return b""
            val = row[0]
            if isinstance(val, memoryview):
                return bytes(val)
            if isinstance(val, bytes):
                return val
            if isinstance(val, str):
                return val.encode("utf-8")
            return b""

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from hinschg.models import Meldung
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        qs = Meldung.objects.filter(
            eingegangen_am__gte=period_from_dt,
            eingegangen_am__lte=period_to_dt,
        )
        records = []
        for meldung in qs:
            # Body bleibt VERSCHLÜSSELT — wir lesen Raw-Bytes.
            raw_bytes = self._read_raw_encrypted(meldung.pk)
            evidence_files = ()
            if raw_bytes:
                import hashlib

                sha = hashlib.sha256(raw_bytes).hexdigest()
                evidence_files = (
                    EvidenceFileRef(
                        filename="body.enc",
                        sha256=sha,
                        mime_type="application/octet-stream",
                        size_bytes=len(raw_bytes),
                        absolute_path=None,
                        encrypted=True,
                        inline_bytes=raw_bytes,
                    ),
                )

            record = EvidenceRecord(
                aggregator_slug=self.slug,
                record_id=f"Meldung:{meldung.pk}",
                titel=f"HinSchG-Meldung {meldung.eingangs_token[:8]}",
                beschreibung=(
                    f"Eingangs-Kanal: {meldung.eingangs_kanal}, "
                    f"Status: {meldung.get_status_display()}"
                ),
                erstellt_am=meldung.eingegangen_am,
                verantwortlicher_email=None,
                status=meldung.status,
                evidence_files=evidence_files,
                oscal_control_ids=(
                    "hinschg-§13",
                    "iso-27001-a.5.4",
                ),
                raw_data={
                    "eingangs_token_prefix": meldung.eingangs_token[:8],
                    "eingangs_kanal": meldung.eingangs_kanal,
                    "anonym": meldung.anonym,
                    "kategorie": meldung.kategorie,
                    "schweregrad": meldung.schweregrad,
                    "rueckmeldung_faellig_bis": str(meldung.rueckmeldung_faellig_bis),
                },
            )
            records.append(record)
        yield from self.filter_records(records)

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=record.titel,
            description=record.beschreibung,
            methods=["INTERVIEW", "EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": cid} for cid in record.oscal_control_ids],
        )


REGISTRY.register(HinSchGAggregator())
