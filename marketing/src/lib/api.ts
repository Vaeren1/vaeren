/**
 * Client für die public Vaeren-API.
 *
 * Build-Zeit: fetcht gegen `PUBLIC_API_BASE` (env, default localhost:8000).
 * Wenn API nicht erreichbar: Fallback auf leere Arrays, Build bricht NICHT ab.
 * Das ist bewusst, damit `bun run build` ohne laufendes Backend funktioniert
 * (Dev-Setup ohne Docker, Static-Site-Smoke-Tests).
 */

const API_BASE = import.meta.env.PUBLIC_API_BASE ?? "http://localhost:8000";

export interface NewsPostListItem {
  slug: string;
  titel: string;
  lead: string;
  kategorie: Kategorie;
  geo: Geo;
  type: NewsType;
  relevanz: Relevanz;
  published_at: string | null;
  pinned: boolean;
}

export interface NewsPostDetail extends NewsPostListItem {
  body_html: string;
  source_links: { titel: string; url: string }[];
  korrekturen: { korrigiert_am: string; was_geaendert: string; grund: string }[];
}

export interface KorrekturListItem {
  korrigiert_am: string;
  was_geaendert: string;
  grund: string;
  post_slug: string;
  post_titel: string;
}

export type Kategorie =
  | "ai_act"
  | "datenschutz"
  | "hinschg"
  | "lieferkette"
  | "arbeitsrecht"
  | "geldwaesche_finanzen"
  | "it_sicherheit"
  | "esg_nachhaltigkeit";

export type Geo = "EU" | "DE" | "EU_DE";
export type NewsType =
  | "gesetzgebung"
  | "urteil"
  | "leitlinie"
  | "konsultation"
  | "frist";
export type Relevanz = "hoch" | "mittel" | "niedrig";

export const KATEGORIE_LABELS: Record<Kategorie, string> = {
  ai_act: "AI Act",
  datenschutz: "Datenschutz",
  hinschg: "HinSchG",
  lieferkette: "Lieferkette",
  arbeitsrecht: "Arbeitsrecht",
  geldwaesche_finanzen: "Geldwäsche/Finanzen",
  it_sicherheit: "IT-Sicherheit",
  esg_nachhaltigkeit: "ESG/Nachhaltigkeit",
};

export const GEO_LABELS: Record<Geo, string> = {
  EU: "EU",
  DE: "Deutschland",
  EU_DE: "EU → Deutschland",
};

export const TYPE_LABELS: Record<NewsType, string> = {
  gesetzgebung: "Gesetzgebung",
  urteil: "Urteil",
  leitlinie: "Leitlinie",
  konsultation: "Konsultation",
  frist: "Frist",
};

export const RELEVANZ_LABELS: Record<Relevanz, string> = {
  hoch: "Hoch",
  mittel: "Mittel",
  niedrig: "Niedrig",
};

async function safeFetch<T>(url: string, fallback: T): Promise<T> {
  try {
    // X-Forwarded-Proto: https hilft beim Server-Side-Build im Docker-
    // Netzwerk (vaeren-django sieht uns sonst als plain-HTTP und schickt
    // 301 → HTTPS, was im container nicht greift).
    const res = await fetch(url, {
      headers: { "X-Forwarded-Proto": "https" },
      redirect: "follow",
    });
    if (!res.ok) {
      console.warn(`[vaeren-api] ${url} → ${res.status}`);
      return fallback;
    }
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`[vaeren-api] ${url} unreachable:`, (err as Error).message);
    return fallback;
  }
}

interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export async function fetchNewsList(
  params: URLSearchParams = new URLSearchParams(),
): Promise<NewsPostListItem[]> {
  const url = new URL(`${API_BASE}/api/public/news/`);
  params.forEach((v, k) => url.searchParams.set(k, v));
  url.searchParams.set("page_size", "200");
  const data = await safeFetch<Paginated<NewsPostListItem>>(url.toString(), {
    count: 0,
    next: null,
    previous: null,
    results: [],
  });
  return data.results;
}

export async function fetchNewsDetail(
  slug: string,
): Promise<NewsPostDetail | null> {
  return safeFetch<NewsPostDetail | null>(
    `${API_BASE}/api/public/news/${slug}/`,
    null,
  );
}

export async function fetchKorrekturen(): Promise<KorrekturListItem[]> {
  const data = await safeFetch<Paginated<KorrekturListItem>>(
    `${API_BASE}/api/public/korrekturen/?page_size=200`,
    { count: 0, next: null, previous: null, results: [] },
  );
  return data.results;
}
