/**
 * Gemeinsame Bausteine der drei Radar-Varianten (Feature 1, §11).
 *
 * Status-Badges, RDG-Disclaimer, Firmen-Header, Kanzlei-Siegel und die
 * Zuordnung der operativen Empfehlungen zu ihrer Pflicht. Die Varianten
 * A/B/C teilen diese Logik, unterscheiden sich nur in der Inszenierung.
 */
import type { ApiError } from "@/lib/api/client";
import {
  type Abdeckung,
  type Befund,
  type Empfehlung,
  type RadarResult,
  onboarding,
} from "@/lib/api/onboarding";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

export interface RadarProps {
  radar: RadarResult;
  firmenname?: string;
  /** Kanzlei-Name aus Settings/API (Phase G). Leer/undefined → Siegel ausgeblendet. */
  kanzleiName?: string;
  onNext?: () => void;
}

// --- Status-Gradient (🟢 / 🟡 / ⚪) ------------------------------------

export const ABDECKUNG_META: Record<
  Abdeckung,
  { icon: string; label: string; ring: string; badge: string }
> = {
  voll_modul: {
    icon: "🟢",
    label: "Voll abgedeckt",
    ring: "border-emerald-300 bg-emerald-50",
    badge: "bg-emerald-100 text-emerald-800",
  },
  basis_hinweis: {
    icon: "🟡",
    label: "Basis-Hinweis",
    ring: "border-amber-300 bg-amber-50",
    badge: "bg-amber-100 text-amber-800",
  },
  in_vorbereitung: {
    icon: "⚪",
    label: "In Vorbereitung",
    ring: "border-slate-200 bg-slate-50",
    badge: "bg-slate-100 text-slate-600",
  },
};

export function abdeckungMeta(abdeckung: string) {
  return (
    ABDECKUNG_META[abdeckung as Abdeckung] ?? {
      icon: "⚪",
      label: abdeckung,
      ring: "border-slate-200 bg-slate-50",
      badge: "bg-slate-100 text-slate-600",
    }
  );
}

export function StatusBadge({ abdeckung }: { abdeckung: string }) {
  const m = abdeckungMeta(abdeckung);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        m.badge,
      )}
    >
      <span aria-hidden>{m.icon}</span>
      {m.label}
    </span>
  );
}

// --- Relevanz-Chip (hoch / mittel / niedrig) ---------------------------

const RELEVANZ_META: Record<string, { label: string; chip: string }> = {
  hoch: { label: "hoch", chip: "bg-rose-100 text-rose-800" },
  mittel: { label: "mittel", chip: "bg-amber-100 text-amber-800" },
  niedrig: { label: "niedrig", chip: "bg-slate-100 text-slate-600" },
};

/** Kleiner Chip "Relevanz: …" pro Befund — konsistent in allen Varianten. */
export function RelevanzChip({ relevanz }: { relevanz: string }) {
  const m = RELEVANZ_META[relevanz] ?? {
    label: relevanz,
    chip: "bg-slate-100 text-slate-600",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium",
        m.chip,
      )}
    >
      Relevanz: {m.label}
    </span>
  );
}

// --- Empfehlungs-Zuordnung ---------------------------------------------

/**
 * `quelle`-Werte einer Empfehlung:
 *  - `"katalog"`    — kuratierte Katalog-Empfehlung, regulär anzeigen.
 *  - `"ki"`         — KI-Vorschlag, bereits validiert → regulär anzeigen
 *                     (kein "bitte prüfen"-Label mehr nötig).
 *  - `"ki_pending"` — KI-Vorschlag, noch nicht validiert → separat unter
 *                     "KI-Einschätzung — bitte prüfen".
 */
const REGULAERE_QUELLEN: ReadonlySet<string> = new Set(["katalog", "ki"]);

/**
 * Ordnet eine Empfehlung über `merkmal_key` einer Pflicht zu. Im aktuellen
 * Datenmodell trägt eine Empfehlung den Betriebsmerkmal-Key (z.B. "lager"),
 * nicht den Regulierungs-Code. Operative Betriebsmerkmal-Empfehlungen werden
 * deshalb der Arbeitsschutz-Pflicht (`arbschg`) zugeordnet; noch nicht
 * validierte KI-Empfehlungen (`ki_pending`) bleiben separat unter
 * "KI-Einschätzung".
 */
export function empfehlungenFuerBefund(
  befund: Befund,
  empfehlungen: Empfehlung[],
): Empfehlung[] {
  if (befund.regulierung_code === "arbschg") {
    return empfehlungen.filter((e) => REGULAERE_QUELLEN.has(e.quelle));
  }
  return [];
}

export function kiPendingEmpfehlungen(
  empfehlungen: Empfehlung[],
): Empfehlung[] {
  return empfehlungen.filter((e) => e.quelle === "ki_pending");
}

// --- Wiederverwendbare UI-Bausteine ------------------------------------

export function FirmenHeader({
  firmenname,
  anzahlPflichten,
}: {
  firmenname?: string;
  anzahlPflichten: number;
}) {
  return (
    <div className="space-y-1">
      <p className="text-sm font-medium text-muted-foreground">
        Compliance-Radar
      </p>
      <h1 className="text-2xl font-semibold tracking-tight">
        {firmenname || "Ihr Unternehmen"}
      </h1>
      <p className="text-sm text-muted-foreground">
        {anzahlPflichten} potenziell relevante Pflicht
        {anzahlPflichten === 1 ? "" : "en"} erkannt.
      </p>
    </div>
  );
}

export function RdgDisclaimer() {
  return (
    <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
      <strong className="font-semibold">Rechtlicher Hinweis:</strong> Dies ist
      eine unverbindliche erste Einschätzung, keine Rechtsberatung. Die
      tatsächliche Betroffenheit bitte mit Ihrer Rechtsberatung bestätigen.
    </div>
  );
}

export function KanzleiSiegel({ name }: { name?: string }) {
  if (!name) return null;
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800">
      <span aria-hidden>⚖️</span>
      Rechtlich geprüft von {name}
    </span>
  );
}

/**
 * "Mehr erfahren"-Expander für 🟡-Basis-Hinweis-Befunde (Spec §6.3).
 *
 * Lädt den RDG-validierten Checklisten-Text erst beim Aufklappen
 * (`onboarding.hinweis(code)`, lazy via `enabled`). Für andere Abdeckungs-
 * Stufen rendert die Komponente nichts — die Varianten A/B/C können sie
 * daher bedenkenlos unter jedem Befund einsetzen.
 */
export function BasisHinweisExpander({ befund }: { befund: Befund }) {
  const [offen, setOffen] = useState(false);
  const { data, isLoading, isError } = useQuery<
    { code: string; hinweis: string },
    ApiError
  >({
    queryKey: ["onboarding-hinweis", befund.regulierung_code],
    queryFn: () => onboarding.hinweis(befund.regulierung_code),
    enabled: offen,
    staleTime: Number.POSITIVE_INFINITY,
  });

  if (befund.abdeckung !== "basis_hinweis") return null;

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setOffen((o) => !o)}
        aria-expanded={offen}
        className="inline-flex items-center gap-1 text-sm font-medium text-amber-800 hover:underline"
      >
        <span aria-hidden>{offen ? "▾" : "▸"}</span>
        {offen ? "Weniger" : "Mehr erfahren"}
      </button>
      {offen && (
        <div className="mt-2 rounded-md border border-amber-200 bg-amber-50/60 px-3 py-2 text-sm text-amber-900">
          {isLoading && (
            <p className="text-muted-foreground">Hinweis wird geladen …</p>
          )}
          {isError && (
            <p className="text-rose-700">
              Hinweis konnte nicht geladen werden. Bitte später erneut
              versuchen.
            </p>
          )}
          {data && <p className="whitespace-pre-line">{data.hinweis}</p>}
        </div>
      )}
    </div>
  );
}

export function EmpfehlungListe({
  empfehlungen,
  kiPending = false,
}: {
  empfehlungen: Empfehlung[];
  kiPending?: boolean;
}) {
  if (empfehlungen.length === 0) return null;
  return (
    <ul className="mt-2 space-y-1 border-l-2 border-slate-200 pl-3 text-sm">
      {empfehlungen.map((e, i) => (
        <li key={`${e.merkmal_key}-${e.ziel}-${i}`} className="text-slate-700">
          <span aria-hidden>{kiPending ? "🤖" : "→"}</span> {e.ziel}
          {e.rechtsgrundlage && (
            <span className="ml-1 text-xs text-muted-foreground">
              ({e.rechtsgrundlage})
            </span>
          )}
          {kiPending && (
            <span className="ml-1 rounded bg-violet-100 px-1.5 py-0.5 text-xs font-medium text-violet-700">
              KI-Einschätzung — bitte prüfen
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}
