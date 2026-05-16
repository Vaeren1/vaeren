/**
 * Vaeren-Redaktion (Admin) API-Client.
 *
 * Tenant-scoped Auth, aber Backend switcht intern auf public-Schema
 * für NewsPost/Korrektur-Operations. Endpoints unter /api/redaktion/.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export type NewsPostStatus =
  | "pending_verify"
  | "hold"
  | "published"
  | "unpublished";

export type NewsPostKategorie =
  | "ai_act"
  | "datenschutz"
  | "hinschg"
  | "lieferkette"
  | "arbeitsrecht"
  | "geldwaesche_finanzen"
  | "it_sicherheit"
  | "esg_nachhaltigkeit";

export type NewsPostGeo = "EU" | "DE" | "EU_DE";
export type NewsPostType =
  | "gesetzgebung"
  | "urteil"
  | "leitlinie"
  | "konsultation"
  | "frist";
export type NewsPostRelevanz = "hoch" | "mittel" | "niedrig";

export interface NewsPostAdmin {
  id: number;
  slug: string;
  titel: string;
  lead: string;
  body_html: string;
  kategorie: NewsPostKategorie;
  geo: NewsPostGeo;
  type: NewsPostType;
  relevanz: NewsPostRelevanz;
  source_links: Array<{ titel: string; url: string }>;
  status: NewsPostStatus;
  verifier_confidence: number | null;
  verifier_issues: string[];
  pinned: boolean;
  published_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
  // Candidate-Kontext (rohe Crawler-Daten + Curator-Begründung)
  candidate_titel: string | null;
  candidate_excerpt: string | null;
  candidate_quelle: string | null;
  candidate_quell_url: string | null;
  candidate_fetched_at: string | null;
  candidate_published_at_source: string | null;
  curator_begruendung: string | null;
  // Computed
  lifetime_days: number | null;
  days_until_expiry: number | null;
  days_since_published: number | null;
  notbremse_url: string;
}

export interface NewsPostPatch {
  titel?: string;
  lead?: string;
  body_html?: string;
  kategorie?: NewsPostKategorie;
  geo?: NewsPostGeo;
  type?: NewsPostType;
  relevanz?: NewsPostRelevanz;
  source_links?: Array<{ titel: string; url: string }>;
  status?: NewsPostStatus;
  pinned?: boolean;
}

export interface RedaktionRunAdmin {
  id: number;
  started_at: string;
  finished_at: string | null;
  crawler_items_in: number;
  curator_items_out: number;
  writer_runs: number;
  verifier_runs: number;
  published: number;
  held: number;
  cost_eur: string;
  notes: string;
}

export const KATEGORIE_LABEL: Record<NewsPostKategorie, string> = {
  ai_act: "AI Act",
  datenschutz: "Datenschutz",
  hinschg: "HinSchG",
  lieferkette: "Lieferkette",
  arbeitsrecht: "Arbeitsrecht",
  geldwaesche_finanzen: "Geldwäsche/Finanzen",
  it_sicherheit: "IT-Sicherheit",
  esg_nachhaltigkeit: "ESG/Nachhaltigkeit",
};

export const GEO_LABEL: Record<NewsPostGeo, string> = {
  EU: "EU",
  DE: "Deutschland",
  EU_DE: "EU → DE",
};

export const STATUS_LABEL: Record<NewsPostStatus, string> = {
  pending_verify: "Wartet auf Verifier",
  hold: "Manuelle Sichtung",
  published: "Live",
  unpublished: "Zurückgezogen",
};

export const STATUS_COLOR: Record<NewsPostStatus, string> = {
  pending_verify: "bg-slate-100 text-slate-700",
  hold: "bg-amber-100 text-amber-800",
  published: "bg-emerald-100 text-emerald-800",
  unpublished: "bg-rose-100 text-rose-800",
};

export const TYPE_LABEL: Record<NewsPostType, string> = {
  gesetzgebung: "Gesetzgebung",
  urteil: "Urteil",
  leitlinie: "Leitlinie",
  konsultation: "Konsultation",
  frist: "Frist",
};

export const RELEVANZ_LABEL: Record<NewsPostRelevanz, string> = {
  hoch: "Hoch",
  mittel: "Mittel",
  niedrig: "Niedrig",
};

// ---- Queries ----------------------------------------------------------

interface ListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface NewsPostListFilters {
  status?: NewsPostStatus | "";
  kategorie?: NewsPostKategorie | "";
  search?: string;
}

function buildQs(filters: Record<string, string | undefined | null>): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v) params.set(k, v);
  }
  params.set("page_size", "200");
  return params.toString();
}

export function useNewsPostList(filters: NewsPostListFilters = {}) {
  return useQuery<NewsPostAdmin[], ApiError>({
    queryKey: ["redaktion-newsposts", filters],
    queryFn: async () => {
      const qs = buildQs(filters as Record<string, string | undefined | null>);
      const res = await api<ListResponse<NewsPostAdmin> | NewsPostAdmin[]>(
        `/api/redaktion/newsposts/?${qs}`,
      );
      return Array.isArray(res) ? res : res.results;
    },
  });
}

export function useNewsPost(slug: string | undefined) {
  return useQuery<NewsPostAdmin, ApiError>({
    queryKey: ["redaktion-newspost", slug],
    queryFn: () => api<NewsPostAdmin>(`/api/redaktion/newsposts/${slug}/`),
    enabled: !!slug,
  });
}

export function useRedaktionRuns() {
  return useQuery<RedaktionRunAdmin[], ApiError>({
    queryKey: ["redaktion-runs"],
    queryFn: async () => {
      const res = await api<ListResponse<RedaktionRunAdmin> | RedaktionRunAdmin[]>(
        "/api/redaktion/runs/",
      );
      return Array.isArray(res) ? res : res.results;
    },
  });
}

// ---- Mutations --------------------------------------------------------

export function usePatchNewsPost() {
  const qc = useQueryClient();
  return useMutation<NewsPostAdmin, ApiError, { slug: string; patch: NewsPostPatch }>({
    mutationFn: ({ slug, patch }) =>
      api<NewsPostAdmin>(`/api/redaktion/newsposts/${slug}/`, {
        method: "PATCH",
        json: patch,
      }),
    onSuccess: (data, vars) => {
      qc.invalidateQueries({ queryKey: ["redaktion-newsposts"] });
      qc.setQueryData(["redaktion-newspost", vars.slug], data);
    },
  });
}

export function usePublishNewsPost() {
  const qc = useQueryClient();
  return useMutation<NewsPostAdmin, ApiError, string>({
    mutationFn: (slug) =>
      api<NewsPostAdmin>(`/api/redaktion/newsposts/${slug}/publish/`, {
        method: "POST",
      }),
    onSuccess: (data, slug) => {
      qc.invalidateQueries({ queryKey: ["redaktion-newsposts"] });
      qc.setQueryData(["redaktion-newspost", slug], data);
    },
  });
}

export function useUnpublishNewsPost() {
  const qc = useQueryClient();
  return useMutation<NewsPostAdmin, ApiError, string>({
    mutationFn: (slug) =>
      api<NewsPostAdmin>(`/api/redaktion/newsposts/${slug}/unpublish/`, {
        method: "POST",
      }),
    onSuccess: (data, slug) => {
      qc.invalidateQueries({ queryKey: ["redaktion-newsposts"] });
      qc.setQueryData(["redaktion-newspost", slug], data);
    },
  });
}

export function useTogglePinNewsPost() {
  const qc = useQueryClient();
  return useMutation<NewsPostAdmin, ApiError, string>({
    mutationFn: (slug) =>
      api<NewsPostAdmin>(`/api/redaktion/newsposts/${slug}/toggle_pin/`, {
        method: "POST",
      }),
    onSuccess: (data, slug) => {
      qc.invalidateQueries({ queryKey: ["redaktion-newsposts"] });
      qc.setQueryData(["redaktion-newspost", slug], data);
    },
  });
}
