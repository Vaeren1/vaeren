import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

// --- Kurs ---------------------------------------------------------------

export type QuizModus = "quiz" | "kenntnisnahme" | "kenntnisnahme_lesezeit";

export type Kategorie =
  | "arbeitsschutz"
  | "brandschutz"
  | "gefahrstoffe"
  | "datenschutz"
  | "compliance"
  | "umwelt"
  | "sonstiges";

export const KATEGORIE_LABEL: Record<Kategorie, string> = {
  arbeitsschutz: "Arbeitsschutz",
  brandschutz: "Brand- & Erste Hilfe",
  gefahrstoffe: "Gefahrstoffe & Maschinen",
  datenschutz: "Datenschutz & IT",
  compliance: "Compliance & Recht",
  umwelt: "Umwelt & Qualität",
  sonstiges: "Sonstiges",
};

// Anzeige-Reihenfolge der Standard-Sektionen in der Bibliothek.
export const KATEGORIE_ORDER: Kategorie[] = [
  "arbeitsschutz",
  "brandschutz",
  "gefahrstoffe",
  "datenschutz",
  "compliance",
  "umwelt",
  "sonstiges",
];

export interface KursModul {
  id: number;
  kurs: number;
  titel: string;
  inhalt_md: string;
  reihenfolge: number;
}

export interface Kurs {
  id: number;
  titel: string;
  beschreibung: string;
  gueltigkeit_monate: number;
  min_richtig_prozent: number;
  fragen_pro_quiz: number;
  quiz_modus: QuizModus;
  mindest_lesezeit_s: number;
  zertifikat_aktiv: boolean;
  kategorie: Kategorie;
  eigentuemer_tenant: string;
  ist_standardkatalog: boolean;
  erstellt_von: number | null;
  erstellt_von_email: string | null;
  aktiv: boolean;
  erstellt_am: string;
  module: KursModul[];
  fragen_pool_groesse: number;
}

export interface KursInput {
  titel: string;
  beschreibung: string;
  gueltigkeit_monate: number;
  min_richtig_prozent: number;
  fragen_pro_quiz: number;
  quiz_modus: QuizModus;
  mindest_lesezeit_s: number;
  zertifikat_aktiv: boolean;
  kategorie: Kategorie;
  aktiv: boolean;
}

export interface AntwortOption {
  id: number;
  frage: number;
  text: string;
  ist_korrekt: boolean;
  reihenfolge: number;
}

export interface Frage {
  id: number;
  kurs: number;
  text: string;
  erklaerung: string;
  reihenfolge: number;
  optionen: AntwortOption[];
}

export interface KursDetail extends Kurs {
  fragen: Frage[];
}

export interface KursPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Kurs[];
}

const KURS_KEY = "kurse";

export function useKursList() {
  return useQuery<KursPage, ApiError>({
    queryKey: [KURS_KEY],
    queryFn: () => api<KursPage>("/api/kurse/"),
  });
}

export function useKurs(id: number | undefined) {
  return useQuery<KursDetail, ApiError>({
    queryKey: ["kurs", id],
    queryFn: () => api<KursDetail>(`/api/kurse/${id}/`),
    enabled: id !== undefined,
  });
}

export function useCreateKurs() {
  const qc = useQueryClient();
  return useMutation<Kurs, ApiError, KursInput>({
    mutationFn: (payload) =>
      api<Kurs>("/api/kurse/", { method: "POST", json: payload }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KURS_KEY] }),
  });
}

export function useUpdateKurs(id: number) {
  const qc = useQueryClient();
  return useMutation<Kurs, ApiError, Partial<KursInput>>({
    mutationFn: (payload) =>
      api<Kurs>(`/api/kurse/${id}/`, { method: "PATCH", json: payload }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KURS_KEY] });
      qc.invalidateQueries({ queryKey: ["kurs", id] });
    },
  });
}

export function useDeleteKurs() {
  const qc = useQueryClient();
  return useMutation<void, ApiError, number>({
    mutationFn: (id) => api<void>(`/api/kurse/${id}/`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KURS_KEY] }),
  });
}

// --- SchulungsWelle -----------------------------------------------------

export type WelleStatus = "draft" | "sent" | "in_progress" | "completed";

export interface SchulungsTaskSummary {
  id: number;
  mitarbeiter: number;
  mitarbeiter_name: string;
  abgeschlossen_am: string | null;
  richtig_prozent: number | null;
  bestanden: boolean | null;
  ablauf_datum: string | null;
}

export interface Welle {
  id: number;
  kurs: number;
  kurs_titel: string;
  titel: string;
  status: WelleStatus;
  deadline: string;
  einleitungs_text: string;
  erstellt_von: number;
  erstellt_von_email: string;
  erstellt_am: string;
  versendet_am: string | null;
  tasks: SchulungsTaskSummary[];
}

export interface WelleInput {
  kurs: number;
  titel: string;
  deadline: string;
  einleitungs_text?: string;
}

export interface WellePage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Welle[];
}

export function useWelleList() {
  return useQuery<WellePage, ApiError>({
    queryKey: ["schulungswellen"],
    queryFn: () => api<WellePage>("/api/schulungswellen/"),
  });
}

export function useWelle(id: number | undefined) {
  return useQuery<Welle, ApiError>({
    queryKey: ["schulungswellen", id],
    queryFn: () => api<Welle>(`/api/schulungswellen/${id}/`),
    enabled: id !== undefined,
  });
}

export function useCreateWelle() {
  const qc = useQueryClient();
  return useMutation<Welle, ApiError, WelleInput>({
    mutationFn: (payload) =>
      api<Welle>("/api/schulungswellen/", { method: "POST", json: payload }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["schulungswellen"] }),
  });
}

export function useUpdateWelle(id: number) {
  const qc = useQueryClient();
  return useMutation<Welle, ApiError, Partial<WelleInput>>({
    mutationFn: (payload) =>
      api<Welle>(`/api/schulungswellen/${id}/`, {
        method: "PATCH",
        json: payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["schulungswellen"] });
      qc.invalidateQueries({ queryKey: ["schulungswellen", id] });
    },
  });
}

export function useZuweisen(id: number) {
  const qc = useQueryClient();
  return useMutation<
    { zugewiesen: number; bereits_zugewiesen: number; fehlend: number },
    ApiError,
    number[]
  >({
    mutationFn: (mitarbeiter_ids) =>
      api(`/api/schulungswellen/${id}/zuweisen/`, {
        method: "POST",
        json: { mitarbeiter_ids },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["schulungswellen", id] });
    },
  });
}

export function usePersonalisieren(id: number) {
  return useMutation<
    { vorschlag: string; quelle: "llm" | "static" },
    ApiError,
    string
  >({
    mutationFn: (kontext) =>
      api(`/api/schulungswellen/${id}/personalisieren/`, {
        method: "POST",
        json: { kontext },
      }),
  });
}

export function useVersenden(id: number) {
  const qc = useQueryClient();
  return useMutation<
    { versendet_an: number; welle_status: WelleStatus },
    ApiError,
    void
  >({
    mutationFn: () =>
      api(`/api/schulungswellen/${id}/versenden/`, {
        method: "POST",
        json: {},
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["schulungswellen"] });
      qc.invalidateQueries({ queryKey: ["schulungswellen", id] });
    },
  });
}

// --- Public Quiz --------------------------------------------------------

export interface PublicAntwortOption {
  id: number;
  text: string;
  reihenfolge: number;
}

export interface PublicFrage {
  id: number;
  text: string;
  reihenfolge: number;
  optionen: PublicAntwortOption[];
}

export interface PublicSchulungActive {
  task_id: number;
  status: string;
  kurs_titel: string;
  kurs_beschreibung: string;
  deadline: string;
  einleitungs_text: string;
  min_richtig_prozent: number;
  module: {
    id: number;
    titel: string;
    inhalt_md: string;
    reihenfolge: number;
  }[];
  fragen: PublicFrage[];
}

export interface PublicSchulungAbgeschlossen {
  task_id: number;
  status: "abgeschlossen";
  bestanden: boolean | null;
  richtig_prozent: number | null;
  zertifikat_token: string | null;
}

export type PublicSchulung = PublicSchulungActive | PublicSchulungAbgeschlossen;

export function isAbgeschlossen(
  p: PublicSchulung,
): p is PublicSchulungAbgeschlossen {
  return p.status === "abgeschlossen";
}

export function usePublicSchulung(token: string | undefined) {
  return useQuery<PublicSchulung, ApiError>({
    queryKey: ["public-schulung", token],
    queryFn: () => api<PublicSchulung>(`/api/public/schulung/${token}/`),
    enabled: !!token,
    retry: false,
  });
}

export function usePublicStart(token: string) {
  return useMutation<{ status: string }, ApiError, void>({
    mutationFn: () =>
      api(`/api/public/schulung/${token}/start/`, { method: "POST", json: {} }),
  });
}

export function usePublicAntwort(token: string) {
  return useMutation<
    { war_korrekt: boolean },
    ApiError,
    { frage_id: number; option_id: number }
  >({
    mutationFn: (payload) =>
      api(`/api/public/schulung/${token}/antwort/`, {
        method: "POST",
        json: payload,
      }),
  });
}

export function usePublicAbschliessen(token: string) {
  return useMutation<
    {
      bestanden: boolean;
      richtig_prozent: number;
      zertifikat_id: string | null;
      ablauf_datum: string | null;
    },
    ApiError,
    void
  >({
    mutationFn: () =>
      api(`/api/public/schulung/${token}/abschliessen/`, {
        method: "POST",
        json: {},
      }),
  });
}
