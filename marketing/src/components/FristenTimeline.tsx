import { useEffect, useMemo, useRef, useState } from "react";
import { KATEGORIE_LABELS, type Kategorie } from "../lib/api";

interface Frist {
  datum: string;
  titel: string;
  kategorie: Kategorie;
  geo: "EU" | "DE";
  kurz: string;
  quelle_url: string;
}

interface Props {
  fristen: Frist[];
}

function formatDateLong(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("de-DE", { year: "numeric", month: "long", day: "numeric" });
}

export default function FristenTimeline({ fristen }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const [showPast, setShowPast] = useState(false);
  const [kategorie, setKategorie] = useState<"alle" | Kategorie>("alle");
  const pastAnchorRef = useRef<HTMLDivElement>(null);

  const sorted = useMemo(
    () => [...fristen].sort((a, b) => a.datum.localeCompare(b.datum)),
    [fristen]
  );

  const filtered = useMemo(
    () =>
      sorted.filter((f) => {
        if (kategorie !== "alle" && f.kategorie !== kategorie) return false;
        if (!showPast && f.datum < today) return false;
        return true;
      }),
    [sorted, kategorie, showPast, today]
  );

  const pastCount = useMemo(
    () => sorted.filter((f) => f.datum < today && (kategorie === "alle" || f.kategorie === kategorie)).length,
    [sorted, kategorie, today]
  );

  // Wenn user "Vergangene anzeigen" klickt, sanft zum ersten vergangenen Eintrag scrollen.
  useEffect(() => {
    if (showPast && pastAnchorRef.current) {
      pastAnchorRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [showPast]);

  const grouped = useMemo(() => {
    const map = new Map<string, Frist[]>();
    for (const f of filtered) {
      const year = f.datum.slice(0, 4);
      if (!map.has(year)) map.set(year, []);
      map.get(year)!.push(f);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [filtered]);

  const kategorienInUse = useMemo(() => {
    const s = new Set<Kategorie>();
    for (const f of sorted) s.add(f.kategorie);
    return Array.from(s);
  }, [sorted]);

  return (
    <>
      {/* Filter-Leiste */}
      <div className="border-b border-line pb-5 mb-6 flex flex-col md:flex-row md:items-center gap-3">
        <select
          value={kategorie}
          onChange={(e) => setKategorie(e.target.value as typeof kategorie)}
          className="px-4 py-2 text-sm border border-line rounded-full bg-paper focus:outline-none focus:border-brand"
        >
          <option value="alle">Alle Kategorien ({sorted.length})</option>
          {kategorienInUse.map((k) => (
            <option key={k} value={k}>
              {KATEGORIE_LABELS[k]}
            </option>
          ))}
        </select>
        <div className="text-sm text-ink-muted">
          {filtered.length} {filtered.length === 1 ? "Frist" : "Fristen"}
          {!showPast && pastCount > 0 && (
            <span className="ml-2">
              · {pastCount} vergangene ausgeblendet
            </span>
          )}
        </div>
      </div>

      {/* Vergangenheit-Toggle, immer am Anfang */}
      <div ref={pastAnchorRef} className="mb-6 -mt-2">
        {!showPast ? (
          pastCount > 0 && (
            <button
              type="button"
              onClick={() => setShowPast(true)}
              className="w-full group flex items-center justify-center gap-2 py-4 border border-dashed border-line rounded-lg hover:border-brand hover:bg-paper-soft transition-colors text-ink-muted hover:text-brand"
            >
              <span className="transition-transform group-hover:-translate-y-0.5">↑</span>
              <span className="text-sm font-medium">
                {pastCount} vergangene {pastCount === 1 ? "Frist" : "Fristen"} anzeigen
              </span>
            </button>
          )
        ) : (
          <button
            type="button"
            onClick={() => setShowPast(false)}
            className="text-xs text-ink-muted hover:text-brand underline"
          >
            Vergangene Fristen ausblenden
          </button>
        )}
      </div>

      {/* Gruppen pro Jahr */}
      {grouped.map(([year, list]) => (
        <section key={year} className="mb-12">
          <div className="flex items-center gap-4 mb-5 sticky top-16 bg-paper/95 backdrop-blur-sm py-3 z-10">
            <h2 className="font-serif text-2xl md:text-3xl text-ink">{year}</h2>
            <div className="flex-1 h-px bg-line"></div>
            <span className="text-xs text-ink-muted">
              {list.length} {list.length === 1 ? "Eintrag" : "Einträge"}
            </span>
          </div>
          <ul className="space-y-3">
            {list.map((f, i) => {
              const past = f.datum < today;
              return (
                <li
                  key={`${f.datum}-${i}`}
                  className={`grid grid-cols-1 md:grid-cols-[180px_1fr_auto] gap-4 p-5 border rounded-lg transition-colors ${
                    past
                      ? "border-line bg-paper-soft/40 opacity-75"
                      : "border-line bg-paper hover:border-brand"
                  }`}
                >
                  <div>
                    <div className="text-xs uppercase tracking-widest text-ink-muted">
                      {f.geo}
                    </div>
                    <div className="font-serif text-lg text-ink">{formatDateLong(f.datum)}</div>
                    {past && (
                      <div className="text-xs text-ink-muted mt-1">vergangen</div>
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`pill pill-${f.kategorie}`}>
                        {KATEGORIE_LABELS[f.kategorie]}
                      </span>
                    </div>
                    <div className="font-medium text-ink mb-1">{f.titel}</div>
                    <p className="text-sm text-ink-muted">{f.kurz}</p>
                  </div>
                  <div className="self-center">
                    <a
                      href={f.quelle_url}
                      className="text-sm no-underline border-b border-line hover:border-brand hover:text-brand"
                      rel="external nofollow"
                    >
                      Quelle →
                    </a>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      ))}

      {filtered.length === 0 && (
        <div className="py-16 text-center text-ink-muted border border-dashed border-line rounded-lg">
          Keine Fristen mit diesen Filtern.
        </div>
      )}
    </>
  );
}
