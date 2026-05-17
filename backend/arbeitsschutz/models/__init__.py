"""Arbeitsschutz-Models — aggregated from submodules.

Aufteilung pro Submodul (Spec §3 Entscheidung 1):
- stammdaten: Arbeitsbereich, Taetigkeit, MitarbeiterTaetigkeit, Gefaehrdung
- gbu: Gefaehrdungsbeurteilung, GbuGefaehrdung, GbuGefaehrdungVorschlag, GbuReviewTask
- massnahmen: Schutzmassnahme, StopHierarchie, MassnahmeStatus, MassnahmeTask, MassnahmenVorschlag
- asa: AsaSitzung, AsaBeschluss, AsaKonfig, AsaSitzungTask
- unfall: Arbeitsunfall, UnfallSchwere, UnfallMeldungTask
- beauftragte: Beauftragter, BeauftragtenTyp, BeauftragtenQuoteCheck, BeauftragterBestellungTask
- betriebsanweisung: Betriebsanweisung, BetriebsanweisungVersion, Aushang, BetriebsanweisungReviewTask
"""

from .asa import (
    AsaBeschluss,
    AsaKonfig,
    AsaSitzung,
    AsaSitzungStatus,
    AsaSitzungTask,
)
from .beauftragte import (
    Beauftragter,
    BeauftragtenQuoteCheck,
    BeauftragtenTyp,
    BeauftragterAblaufTask,
    BeauftragterBestellungTask,
)
from .betriebsanweisung import (
    Aushang,
    Betriebsanweisung,
    BetriebsanweisungReviewTask,
    BetriebsanweisungTyp,
    BetriebsanweisungVersion,
)
from .gbu import (
    Gefaehrdungsbeurteilung,
    GbuGefaehrdung,
    GbuGefaehrdungVorschlag,
    GbuReviewTask,
    GbuStatus,
)
from .massnahmen import (
    MassnahmeStatus,
    MassnahmeTask,
    MassnahmenVorschlag,
    Schutzmassnahme,
    StopHierarchie,
)
from .stammdaten import (
    Arbeitsbereich,
    ArbeitsbereichTyp,
    Gefaehrdung,
    GefaehrdungKategorie,
    MitarbeiterTaetigkeit,
    Taetigkeit,
)
from .unfall import (
    Arbeitsunfall,
    UnfallMeldungTask,
    UnfallSchwere,
)

__all__ = [
    "Arbeitsbereich",
    "ArbeitsbereichTyp",
    "Arbeitsunfall",
    "AsaBeschluss",
    "AsaKonfig",
    "AsaSitzung",
    "AsaSitzungStatus",
    "AsaSitzungTask",
    "Aushang",
    "Beauftragter",
    "BeauftragtenQuoteCheck",
    "BeauftragtenTyp",
    "BeauftragterAblaufTask",
    "BeauftragterBestellungTask",
    "Betriebsanweisung",
    "BetriebsanweisungReviewTask",
    "BetriebsanweisungTyp",
    "BetriebsanweisungVersion",
    "Gefaehrdung",
    "GefaehrdungKategorie",
    "Gefaehrdungsbeurteilung",
    "GbuGefaehrdung",
    "GbuGefaehrdungVorschlag",
    "GbuReviewTask",
    "GbuStatus",
    "MassnahmeStatus",
    "MassnahmeTask",
    "MassnahmenVorschlag",
    "MitarbeiterTaetigkeit",
    "Schutzmassnahme",
    "StopHierarchie",
    "Taetigkeit",
    "UnfallMeldungTask",
    "UnfallSchwere",
]
