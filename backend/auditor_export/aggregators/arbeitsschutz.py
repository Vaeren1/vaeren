"""Aggregator: Arbeitsschutz → DGUV-V1 + ASiG + Arbeitsschutz-Gesetz.

Sammelt aus:
- Gefaehrdungsbeurteilung (status=freigegeben)
- Schutzmassnahme (status in wirksamkeit_geprueft, umgesetzt)
- AsaSitzung (status=durchgefuehrt)
- Arbeitsunfall (anonymisiert: Klarname/Beschreibung wird NICHT exportiert,
  Gesundheitsdaten Art. 9 DSGVO bleiben verschlüsselt im System)
- Beauftragter (aktiv=True)
- BetriebsanweisungVersion (freigegeben_am != NULL)

WICHTIG (Datenschutz): Arbeitsunfall-Records gehen NUR als anonymisierte
Statistik raus (Bereich, Schwere, Ausfalltage) — die `EncryptedTextField`-
Inhalte (betroffener_name, beschreibung, verletzungsart) werden NIE exportiert.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from typing import Any

from .base import BaseAggregator, EvidenceRecord, REGISTRY, stable_uuid_v5


class ArbeitsschutzAggregator(BaseAggregator):
    slug = "arbeitsschutz"
    norm_scopes = ("arbeitsschutz", "dguv_v1")

    def collect(
        self,
        *,
        period_from: datetime.date,
        period_to: datetime.date,
        filter_dict: dict[str, Any] | None = None,
    ) -> Iterator[EvidenceRecord]:
        try:
            from arbeitsschutz.models.asa import AsaSitzung
            from arbeitsschutz.models.beauftragte import Beauftragter
            from arbeitsschutz.models.betriebsanweisung import BetriebsanweisungVersion
            from arbeitsschutz.models.gbu import Gefaehrdungsbeurteilung
            from arbeitsschutz.models.massnahmen import Schutzmassnahme
            from arbeitsschutz.models.unfall import Arbeitsunfall
        except ImportError:
            return

        period_from_dt = datetime.datetime.combine(
            period_from, datetime.time.min, tzinfo=datetime.UTC
        )
        period_to_dt = datetime.datetime.combine(
            period_to, datetime.time.max, tzinfo=datetime.UTC
        )

        records: list[EvidenceRecord] = []

        # 1) Freigegebene Gefährdungsbeurteilungen
        for gbu in Gefaehrdungsbeurteilung.objects.filter(
            freigegeben_am__gte=period_from_dt,
            freigegeben_am__lte=period_to_dt,
            status="freigegeben",
        ).select_related("taetigkeit__arbeitsbereich", "freigegeben_von"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Gefaehrdungsbeurteilung:{gbu.pk}",
                    titel=f"GBU freigegeben: {gbu.titel}",
                    beschreibung=(
                        f"Tätigkeit: {gbu.taetigkeit.name}; "
                        f"Bereich: {gbu.taetigkeit.arbeitsbereich.name}"
                    ),
                    erstellt_am=gbu.freigegeben_am,
                    verantwortlicher_email=(
                        gbu.freigegeben_von.email if gbu.freigegeben_von else None
                    ),
                    status=gbu.status,
                    oscal_control_ids=("arbschg-§5", "dguv-v1-§3"),
                    raw_data={
                        "taetigkeit_id": gbu.taetigkeit_id,
                        "anzahl_positionen": gbu.positionen.count(),
                    },
                )
            )

        # 2) Maßnahmen mit nachgewiesener Wirksamkeit
        for m in Schutzmassnahme.objects.filter(
            wirksamkeitspruefung_am__gte=period_from,
            wirksamkeitspruefung_am__lte=period_to,
            status="wirksamkeit_geprueft",
            wirksam=True,
        ).select_related("verantwortlicher"):
            erstellt = datetime.datetime.combine(
                m.wirksamkeitspruefung_am, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Schutzmassnahme:{m.pk}",
                    titel=f"Maßnahme wirksam: {m.titel}",
                    beschreibung=(m.beschreibung or "")[:2000],
                    erstellt_am=erstellt,
                    verantwortlicher_email=(
                        m.verantwortlicher.email if m.verantwortlicher else None
                    ),
                    status="wirksam",
                    oscal_control_ids=("arbschg-§4", "dguv-v1-§3"),
                    raw_data={
                        "stop": m.hierarchie_stufe,
                        "wirksam": m.wirksam,
                    },
                )
            )

        # 3) Durchgeführte ASA-Sitzungen
        for asa in AsaSitzung.objects.filter(
            durchgefuehrt_am__gte=period_from_dt,
            durchgefuehrt_am__lte=period_to_dt,
            status="durchgefuehrt",
        ):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"AsaSitzung:{asa.pk}",
                    titel=f"ASA-Sitzung {asa.quartal}: {asa.titel}",
                    beschreibung=f"Teilnehmer-Anzahl: {asa.teilnehmer.count()}",
                    erstellt_am=asa.durchgefuehrt_am,
                    status=asa.status,
                    oscal_control_ids=("asig-§11",),
                    raw_data={
                        "quartal": asa.quartal,
                        "anzahl_beschluesse": asa.beschluesse.count(),
                    },
                )
            )

        # 4) Arbeitsunfälle — ANONYMISIERT, nur Statistik-Felder!
        # Gesundheitsdaten (Art. 9 DSGVO) bleiben verschlüsselt im System.
        for u in Arbeitsunfall.objects.filter(
            datum__gte=period_from_dt,
            datum__lte=period_to_dt,
        ).select_related("arbeitsbereich"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Arbeitsunfall:{u.pk}",
                    titel=f"Unfall #{u.pk} im Bereich {u.arbeitsbereich.name}",
                    beschreibung=(
                        f"Schwere: {u.get_schwere_display()}; "
                        f"Ausfalltage: {u.ausfalltage}; "
                        f"BG-Meldepflicht: {'ja' if u.bg_meldung_pflicht else 'nein'}; "
                        f"BG-gemeldet: {'ja' if u.bg_gemeldet_am else 'nein'}"
                    ),
                    erstellt_am=u.datum,
                    status="dokumentiert",
                    oscal_control_ids=("arbschg-§5", "dguv-v1-§24"),
                    raw_data={
                        "schwere": u.schwere,
                        "ausfalltage": u.ausfalltage,
                        "bg_meldepflicht": u.bg_meldung_pflicht,
                        "bg_gemeldet_am": str(u.bg_gemeldet_am) if u.bg_gemeldet_am else None,
                        # KEINE Klarnamen, KEINE Beschreibung, KEINE Verletzungsart!
                    },
                )
            )

        # 5) Aktive Beauftragte
        for b in Beauftragter.objects.filter(
            aktiv=True,
            bestellt_am__gte=period_from,
            bestellt_am__lte=period_to,
        ).select_related("person"):
            erstellt = datetime.datetime.combine(
                b.bestellt_am, datetime.time(12, 0), tzinfo=datetime.UTC
            )
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"Beauftragter:{b.pk}",
                    titel=f"Beauftragter bestellt: {b.get_typ_display()}",
                    beschreibung=f"Person: {b.person}; bestellt bis: {b.bestellt_bis or 'unbefristet'}",
                    erstellt_am=erstellt,
                    verantwortlicher_email=b.person.email or None,
                    status="aktiv",
                    oscal_control_ids=("arbsig", "asig-§§5-7"),
                    raw_data={
                        "typ": b.typ,
                        "bestellt_bis": str(b.bestellt_bis) if b.bestellt_bis else None,
                    },
                )
            )

        # 6) Freigegebene Betriebsanweisungs-Versionen
        for v in BetriebsanweisungVersion.objects.filter(
            freigegeben_am__gte=period_from_dt,
            freigegeben_am__lte=period_to_dt,
        ).select_related("betriebsanweisung", "freigegeben_von"):
            records.append(
                EvidenceRecord(
                    aggregator_slug=self.slug,
                    record_id=f"BetriebsanweisungVersion:{v.pk}",
                    titel=f"BA freigegeben: {v.betriebsanweisung.titel} v{v.version}",
                    beschreibung=(v.betriebsanweisung.titel or "")[:200],
                    erstellt_am=v.freigegeben_am,
                    verantwortlicher_email=(
                        v.freigegeben_von.email if v.freigegeben_von else None
                    ),
                    status="freigegeben",
                    oscal_control_ids=("arbschg-§12", "dguv-v1-§14"),
                    raw_data={
                        "version": v.version,
                        "ba_id": v.betriebsanweisung_id,
                    },
                )
            )

        yield from self.filter_records(records)

    def map_to_oscal(self, record: EvidenceRecord):
        from auditor_export.oscal.schemas import OscalObservation

        return OscalObservation(
            uuid=str(stable_uuid_v5(record.record_id)),
            title=record.titel,
            description=record.beschreibung,
            methods=["EXAMINE"],
            types=["finding"],
            collected=record.erstellt_am.isoformat(),
            props=[
                {"name": "vaeren-aggregator", "value": self.slug},
                {"name": "vaeren-record-id", "value": record.record_id},
            ]
            + [{"name": "vaeren-control-id", "value": c} for c in record.oscal_control_ids],
        )


REGISTRY.register(ArbeitsschutzAggregator())
