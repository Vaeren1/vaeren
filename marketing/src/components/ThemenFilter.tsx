import { useMemo, useState } from "react";
import {
  KATEGORIE_LABELS,
  type Kategorie,
  type NewsPostListItem,
} from "../lib/api";

interface ThemaItem {
  kategorie: Kategorie;
  titel: string;
  kurz: string;
  schlagworte: string[];
  hub_slug?: string;
}

interface Props {
  themen: ThemaItem[];
  postsByKategorie: Record<string, number>;
  latestByKategorie: Record<string, { titel: string; slug: string; published_at: string | null } | null>;
}

export default function ThemenFilter({ themen, postsByKategorie, latestByKategorie }: Props) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"alle" | "mit_hub" | "in_vorbereitung">("alle");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return themen.filter((t) => {
      if (filter === "mit_hub" && !t.hub_slug) return false;
      if (filter === "in_vorbereitung" && t.hub_slug) return false;
      if (!q) return true;
      const hay = (
        t.titel +
        " " +
        t.kurz +
        " " +
        t.schlagworte.join(" ")
      ).toLowerCase();
      return hay.includes(q);
    });
  }, [themen, query, filter]);

  return (
    <>
      <div className="border-b border-line pb-5 mb-6 flex flex-col md:flex-row md:items-center gap-3">
        <div className="flex gap-2 text-sm">
          {(
            [
              ["alle", `Alle (${themen.length})`],
              ["mit_hub", `Mit Hub (${themen.filter((t) => t.hub_slug).length})`],
              ["in_vorbereitung", `In Vorbereitung (${themen.filter((t) => !t.hub_slug).length})`],
            ] as const
          ).map(([v, label]) => (
            <button
              key={v}
              type="button"
              onClick={() => setFilter(v)}
              className={`px-3 py-1.5 rounded-full text-xs uppercase tracking-wide border transition-colors ${
                filter === v
                  ? "border-brand bg-brand text-paper"
                  : "border-line text-ink-muted hover:border-brand"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Themen oder Schlagworte suchen…"
          className="flex-1 min-w-[200px] px-4 py-2 text-sm border border-line rounded-full bg-paper focus:outline-none focus:border-brand"
        />
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((t) => {
          const count = postsByKategorie[t.kategorie] ?? 0;
          const latest = latestByKategorie[t.kategorie];
          const href = t.hub_slug ? `/themen/${t.hub_slug}` : `/news?kategorie=${t.kategorie}`;
          const hubReady = !!t.hub_slug;
          return (
            <a
              key={t.kategorie}
              href={href}
              className="group no-underline h-full"
            >
              <article className="h-full p-5 bg-paper border border-line rounded-lg hover:border-brand hover:shadow-sm transition-all flex flex-col">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className={`pill pill-${t.kategorie}`}>
                    {KATEGORIE_LABELS[t.kategorie]}
                  </span>
                  {!hubReady && (
                    <span className="text-[10px] uppercase tracking-wider text-accent-warm whitespace-nowrap mt-1">
                      Hub in Vorbereitung
                    </span>
                  )}
                </div>
                <h3 className="font-serif text-xl text-ink group-hover:text-brand mb-2">
                  {t.titel}
                </h3>
                <p className="text-sm text-ink-soft leading-relaxed mb-4 flex-1">
                  {t.kurz}
                </p>
                <div className="flex flex-wrap gap-1 mb-4">
                  {t.schlagworte.slice(0, 4).map((s) => (
                    <span
                      key={s}
                      className="text-[11px] text-ink-muted bg-paper-soft px-2 py-0.5 rounded"
                    >
                      {s}
                    </span>
                  ))}
                </div>
                <div className="text-xs text-ink-muted border-t border-line pt-3 flex justify-between items-end gap-2">
                  <span>
                    {count} {count === 1 ? "Beitrag" : "Beiträge"}
                  </span>
                  <span className="text-brand">
                    {hubReady ? "Hub öffnen" : "Beiträge ansehen"} →
                  </span>
                </div>
                {latest && (
                  <div className="text-xs text-ink-muted mt-2 line-clamp-1">
                    Neueste: „{latest.titel}"
                  </div>
                )}
              </article>
            </a>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <div className="py-16 text-center text-ink-muted">
          Keine Themen passen zu „{query}".
        </div>
      )}
    </>
  );
}
