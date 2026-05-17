"""Bundesanzeiger-Poll für Tenant-Stammdaten-Monitoring.

Strategie:
- Bundesanzeiger hat einen JSON-Suchendpoint (`https://www.bundesanzeiger.de/...`)
  der ohne API-Key abfragbar ist.
- Wir bauen darauf keinen full-blown Crawler — wir suchen nach dem HRB des
  Tenants und sammeln neue Treffer der letzten 30 Tage.
- Wird wöchentlich via Celery-Task aufgerufen.

YAGNI:
- Kein OCR auf PDF-Anhänge.
- Kein Diff zum letzten Poll-Zyklus (wir setzen auf Datenbank-Unique-Constraint
  über (stammblatt, quelle, url) — Duplikate werden silently ignoriert).
- Kein Fail-Hard auf einzelne Tenants: jedes Tenant pollen, Fehler einzeln loggen.
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass

import httpx
from django.utils import timezone
from django_tenants.utils import schema_context, tenant_context

from tenants.models import Tenant

from .models import RegisterBekanntmachung, Unternehmensstammblatt

logger = logging.getLogger(__name__)

BUNDESANZEIGER_SEARCH_URL = "https://www.bundesanzeiger.de/pub/de/suchergebnis"
HTTP_TIMEOUT = 10.0


@dataclass
class PollResult:
    tenant_schema: str
    treffer_neu: int
    treffer_total: int
    fehler: str = ""


def normalize_hrb(raw: str) -> str:
    """'HRB 123456 München' → 'HRB 123456'."""
    m = re.search(r"HR[AB]\s*\d+", raw or "", flags=re.IGNORECASE)
    if not m:
        return ""
    return m.group(0).upper().replace("HRA", "HRA ").replace("HRB", "HRB ").replace("  ", " ").strip()


def _suche_bundesanzeiger(hrb: str) -> list[dict]:
    """Liefert Bundesanzeiger-Suchtreffer für eine HRB-Nummer.

    Bundesanzeiger erwartet ein Multipart-Formular und liefert HTML zurück.
    Wir parsen das HTML hier nur sehr grob — Stabilität auf Free-Service-Ebene
    ist nicht garantiert. Bei Layout-Änderung müssen wir nachziehen.
    """
    try:
        resp = httpx.get(
            BUNDESANZEIGER_SEARCH_URL,
            params={"search_query": hrb},
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": "Vaeren-Compliance-Monitor/1.0"},
            follow_redirects=True,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Bundesanzeiger-Abruf für %s fehlgeschlagen: %s", hrb, exc)
        return []

    html = resp.text
    treffer: list[dict] = []
    # Einfaches Pattern für Treffer-Einträge im Bundesanzeiger-HTML.
    # Format ist über die Jahre stabil: <div class="row"><div class="info_left">...
    for m in re.finditer(
        r'<a[^>]+href="(?P<url>/pub/de/amtlicher-teil[^"]+)"[^>]*>(?P<titel>[^<]+)</a>',
        html,
    ):
        treffer.append(
            {
                "titel": re.sub(r"\s+", " ", m.group("titel")).strip(),
                "url": "https://www.bundesanzeiger.de" + m.group("url"),
            }
        )
    return treffer[:20]  # Cap, falls Pattern zu breit matched


def poll_tenant(tenant: Tenant) -> PollResult:
    """Pollt Bundesanzeiger für genau einen Tenant. Schreibt im Tenant-Schema."""
    with tenant_context(tenant):
        sb = Unternehmensstammblatt.objects.first()
        if not sb:
            return PollResult(tenant_schema=tenant.schema_name, treffer_neu=0, treffer_total=0)
        if not sb.bundesanzeiger_monitoring_aktiv:
            return PollResult(tenant_schema=tenant.schema_name, treffer_neu=0, treffer_total=0)
        hrb = normalize_hrb(sb.handelsregister_nummer)
        if not hrb:
            return PollResult(
                tenant_schema=tenant.schema_name,
                treffer_neu=0,
                treffer_total=0,
                fehler="kein gültiger HRB im Stammblatt",
            )

        rohtreffer = _suche_bundesanzeiger(hrb)
        neu = 0
        for t in rohtreffer:
            obj, created = RegisterBekanntmachung.objects.get_or_create(
                stammblatt=sb,
                quelle="bundesanzeiger",
                url=t["url"],
                defaults={
                    "titel": t["titel"][:300],
                    "veroeffentlicht_am": datetime.date.today(),
                    "raw_payload": {"_source": "html-pattern"},
                },
            )
            if created:
                neu += 1
        sb.last_polled_at = timezone.now()
        sb.save(update_fields=["last_polled_at", "updated_at"])
        return PollResult(
            tenant_schema=tenant.schema_name,
            treffer_neu=neu,
            treffer_total=len(rohtreffer),
        )


def poll_all_tenants() -> list[PollResult]:
    """Iteriert über alle non-public Tenants. Fehler werden pro Tenant abgefangen."""
    from django.db import connection

    connection.set_schema_to_public()
    with schema_context("public"):
        tenants = list(Tenant.objects.exclude(schema_name="public"))
    results: list[PollResult] = []
    for t in tenants:
        try:
            results.append(poll_tenant(t))
        except Exception as exc:  # pragma: no cover — defensive
            logger.exception("Bundesanzeiger-Poll für %s failed: %s", t.schema_name, exc)
            results.append(
                PollResult(
                    tenant_schema=t.schema_name,
                    treffer_neu=0,
                    treffer_total=0,
                    fehler=str(exc),
                )
            )
    return results
