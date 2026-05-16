import { useMemo, useState } from "react";
import {
  GEO_LABELS,
  KATEGORIE_LABELS,
  TYPE_LABELS,
  type NewsPostListItem,
  type Kategorie,
  type Geo,
  type NewsType,
} from "../lib/api";

interface Props {
  posts: NewsPostListItem[];
}

function dateMatchesFilter(iso: string | null, zeitraum: string): boolean {
  if (!iso || zeitraum === "alle") return true;
  const now = Date.now();
  const date = new Date(iso).getTime();
  const daysAgo = (now - date) / (24 * 60 * 60 * 1000);
  if (zeitraum === "woche") return daysAgo <= 7;
  if (zeitraum === "monat") return daysAgo <= 31;
  if (zeitraum === "quartal") return daysAgo <= 92;
  if (zeitraum === "jahr") return daysAgo <= 366;
  return true;
}

export default function NewsFilter({ posts }: Props) {
  const [kategorie, setKategorie] = useState<"alle" | Kategorie>("alle");
  const [geo, setGeo] = useState<"alle" | Geo>("alle");
  const [type, setType] = useState<"alle" | NewsType>("alle");
  const [zeitraum, setZeitraum] = useState("alle");
  const [suche, setSuche] = useState("");

  const filtered = useMemo(() => {
    const s = suche.trim().toLowerCase();
    return posts.filter((p) => {
      if (kategorie !== "alle" && p.kategorie !== kategorie) return false;
      if (geo !== "alle" && p.geo !== geo) return false;
      if (type !== "alle" && p.type !== type) return false;
      if (!dateMatchesFilter(p.published_at, zeitraum)) return false;
      if (s) {
        const hay = `${p.titel} ${p.lead}`.toLowerCase();
        if (!hay.includes(s)) return false;
      }
      return true;
    });
  }, [posts, kategorie, geo, type, zeitraum, suche]);

  function reset() {
    setKategorie("alle");
    setGeo("alle");
    setType("alle");
    setZeitraum("alle");
    setSuche("");
  }

  const anyFilter =
    kategorie !== "alle" ||
    geo !== "alle" ||
    type !== "alle" ||
    zeitraum !== "alle" ||
    suche.length > 0;

  return (
    <>
      <div className="border-b border-line pb-6 mb-2 space-y-4">
        <div className="flex flex-wrap gap-3">
          <Select
            value={kategorie}
            onChange={(v) => setKategorie(v as typeof kategorie)}
            label="Kategorie"
            options={[
              ["alle", "Alle Kategorien"],
              ...(Object.entries(KATEGORIE_LABELS) as [string, string][]),
            ]}
          />
          <Select
            value={geo}
            onChange={(v) => setGeo(v as typeof geo)}
            label="Geltungsbereich"
            options={[
              ["alle", "Alle Regionen"],
              ...(Object.entries(GEO_LABELS) as [string, string][]),
            ]}
          />
          <Select
            value={type}
            onChange={(v) => setType(v as typeof type)}
            label="Beitragstyp"
            options={[
              ["alle", "Alle Typen"],
              ...(Object.entries(TYPE_LABELS) as [string, string][]),
            ]}
          />
          <Select
            value={zeitraum}
            onChange={setZeitraum}
            label="Zeitraum"
            options={[
              ["alle", "Alle Zeiträume"],
              ["woche", "Letzte Woche"],
              ["monat", "Letzter Monat"],
              ["quartal", "Letztes Quartal"],
              ["jahr", "Letztes Jahr"],
            ]}
          />
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <input
            type="search"
            value={suche}
            onChange={(e) => setSuche(e.target.value)}
            placeholder="Volltextsuche…"
            className="flex-1 min-w-[200px] px-4 py-2 text-sm border border-line rounded-full bg-paper focus:outline-none focus:border-brand"
          />
          {anyFilter && (
            <button
              type="button"
              onClick={reset}
              className="text-xs text-ink-muted hover:text-brand underline"
            >
              Filter zurücksetzen
            </button>
          )}
        </div>
        <div className="text-sm text-ink-muted">
          {filtered.length} {filtered.length === 1 ? "Beitrag" : "Beiträge"}
        </div>
      </div>
      <ul>
        {filtered.map((p) => (
          <li key={p.slug}>
            <NewsRow post={p} />
          </li>
        ))}
        {filtered.length === 0 && (
          <li className="py-12 text-center text-ink-muted">
            Keine Beiträge zu diesen Filtern.
          </li>
        )}
      </ul>
    </>
  );
}

function Select({
  value,
  onChange,
  label,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  label: string;
  options: [string, string][];
}) {
  return (
    <label className="text-sm text-ink-soft flex flex-col gap-1">
      <span className="sr-only">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-3 py-2 text-sm border border-line rounded-full bg-paper focus:outline-none focus:border-brand"
        aria-label={label}
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
}

function NewsRow({ post }: { post: NewsPostListItem }) {
  const href = `/news/${post.slug}`;
  return (
    <a href={href} className="group block py-7 border-b border-line no-underline">
      <div className="flex flex-wrap items-center gap-3 mb-3">
        <span className={`pill pill-${post.kategorie}`}>
          {KATEGORIE_LABELS[post.kategorie]}
        </span>
        <span className="text-xs uppercase tracking-wide text-ink-muted">
          {GEO_LABELS[post.geo]}
        </span>
        <span className="text-xs text-ink-muted">
          {post.published_at
            ? new Date(post.published_at).toLocaleDateString("de-DE")
            : ""}
        </span>
        {post.pinned && (
          <span className="text-xs uppercase tracking-wide text-accent-warm">
            Angepinnt
          </span>
        )}
      </div>
      <h2 className="font-serif text-2xl text-ink leading-snug group-hover:text-brand mb-2">
        {post.titel}
      </h2>
      <p className="text-base text-ink-soft leading-relaxed">{post.lead}</p>
    </a>
  );
}
