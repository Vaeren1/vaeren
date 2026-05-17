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

export type ModulTyp =
  | "text"
  | "pdf"
  | "bild"
  | "office"
  | "video_upload"
  | "video_youtube";

export const MODUL_TYP_LABEL: Record<ModulTyp, string> = {
  text: "Text / Markdown",
  pdf: "PDF",
  bild: "Bild (PNG/JPG)",
  office: "Office (DOCX/PPTX)",
  video_upload: "Video-Upload",
  video_youtube: "YouTube-Embed",
};

export interface KursModul {
  id: number;
  kurs: number;
  titel: string;
  reihenfolge: number;
  typ: ModulTyp;
  inhalt_md: string;
  youtube_url: string;
  asset: number | null;
}

export type AssetCompressionStatus =
  | "not_needed"
  | "pending"
  | "done"
  | "skipped"
  | "failed";

export interface KursAsset {
  id: number;
  kurs: number;
  original_mime: string;
  original_size_bytes: number;
  compression_status: AssetCompressionStatus;
  compressed_size_bytes: number | null;
  konvertierung_status: "not_needed" | "pending" | "done" | "failed";
  hochgeladen_am: string;
  download_url: string | null;
}

export function useKursAsset(id: number | null | undefined) {
  return useQuery<KursAsset, ApiError>({
    queryKey: ["kurs-asset", id],
    queryFn: () => api<KursAsset>(`/api/kurs-assets/${id}/`),
    enabled: id != null,
    refetchInterval: (query) => {
      const status = query.state.data?.compression_status;
      return status === "pending" ? 2000 : false;
    },
  });
}

export async function uploadAsset(
  kursId: number,
  file: File,
): Promise<KursAsset> {
  const form = new FormData();
  form.append("kurs", String(kursId));
  form.append("file", file);
  // Direkt fetch (CSRF + Cookie wie api(), aber kein JSON-Content-Type)
  const csrfRes = await fetch("/api/auth/csrf/", { credentials: "include" });
  const { csrf_token } = (await csrfRes.json()) as { csrf_token: string };
  const res = await fetch("/api/kurs-assets/upload/", {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRFToken": csrf_token },
    body: form,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body === "object" ? JSON.stringify(body) : String(body));
  }
  return (await res.json()) as KursAsset;
}

export interface ModulInput {
  kurs: number;
  titel: string;
  reihenfolge: number;
  typ: ModulTyp;
  inhalt_md?: string;
  youtube_url?: string;
  asset?: number | null;
}

export function useCreateModul() {
  const qc = useQueryClient();
  return useMutation<KursModul, ApiError, ModulInput>({
    mutationFn: (payload) =>
      api<KursModul>("/api/kurs-module/", { method: "POST", json: payload }),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ["kurs", vars.kurs] });
    },
  });
}

export function useUpdateModul() {
  const qc = useQueryClient();
  return useMutation<
    KursModul,
    ApiError,
    { id: number; payload: Partial<ModulInput> & { kurs: number } }
  >({
    mutationFn: ({ id, payload }) =>
      api<KursModul>(`/api/kurs-module/${id}/`, {
        method: "PATCH",
        json: payload,
      }),
    onSuccess: (_d, vars) => {
      qc.invalidateQueries({ queryKey: ["kurs", vars.payload.kurs] });
    },
  });
}

export function useDeleteModul() {
  const qc = useQueryClient();
  return useMutation<void, ApiError, { id: number; kursId: number }>({
    mutationFn: ({ id }) =>
      api<void>(`/api/kurs-module/${id}/`, { method: "DELETE" }),
    onSuccess: (_d, vars) =>
      qc.invalidateQueries({ queryKey: ["kurs", vars.kursId] }),
  });
}

// --- Frage (Quiz-Pool) -------------------------------------------------

export interface AntwortOptionInput {
  text: string;
  ist_korrekt: boolean;
  reihenfolge?: number;
}

export interface FrageInput {
  kurs: number;
  text: string;
  erklaerung: string;
  reihenfolge: number;
  optionen: AntwortOptionInput[];
}

export function useCreateFrage() {
  const qc = useQueryClient();
  return useMutation<Frage, ApiError, FrageInput>({
    mutationFn: (payload) =>
      api<Frage>("/api/fragen/", { method: "POST", json: payload }),
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ["kurs", v.kurs] }),
  });
}

export function useUpdateFrage() {
  const qc = useQueryClient();
  return useMutation<
    Frage,
    ApiError,
    { id: number; payload: FrageInput }
  >({
    mutationFn: ({ id, payload }) =>
      api<Frage>(`/api/fragen/${id}/`, { method: "PATCH", json: payload }),
    onSuccess: (_d, v) =>
      qc.invalidateQueries({ queryKey: ["kurs", v.payload.kurs] }),
  });
}

export function useDeleteFrage() {
  const qc = useQueryClient();
  return useMutation<void, ApiError, { id: number; kursId: number }>({
    mutationFn: ({ id }) =>
      api<void>(`/api/fragen/${id}/`, { method: "DELETE" }),
    onSuccess: (_d, v) => qc.invalidateQueries({ queryKey: ["kurs", v.kursId] }),
  });
}

// --- FrageVorschlag (LLM) ---------------------------------------------

export type VorschlagStatus = "offen" | "akzeptiert" | "verworfen";

export interface FrageVorschlag {
  id: number;
  kurs: number;
  text: string;
  erklaerung: string;
  optionen: { text: string; ist_korrekt: boolean }[];
  quell_module: number[];
  erstellt_am: string;
  erstellt_von: number;
  llm_modell: string;
  llm_prompt_hash: string;
  status: VorschlagStatus;
  entschieden_am: string | null;
  entschieden_von: number | null;
  akzeptiert_als: number | null;
}

export function useVorschlaege(kursId: number) {
  return useQuery<{ results: FrageVorschlag[] } | FrageVorschlag[], ApiError>({
    queryKey: ["vorschlaege", kursId],
    queryFn: () =>
      api<{ results: FrageVorschlag[] }>(
        `/api/fragen-vorschlaege/?kurs=${kursId}`,
      ),
    refetchInterval: 5000, // Poll während Celery-Task läuft
  });
}

export function useGenerateVorschlaege() {
  const qc = useQueryClient();
  return useMutation<
    { queued: boolean; kurs: number; anzahl: number },
    ApiError,
    { kurs: number; anzahl?: number }
  >({
    mutationFn: (payload) =>
      api("/api/fragen-vorschlaege/generieren/", {
        method: "POST",
        json: payload,
      }),
    onSuccess: (_d, v) =>
      qc.invalidateQueries({ queryKey: ["vorschlaege", v.kurs] }),
  });
}

export function useAkzeptiereVorschlag() {
  const qc = useQueryClient();
  return useMutation<
    FrageVorschlag,
    ApiError,
    {
      id: number;
      kursId: number;
      payload?: {
        text?: string;
        erklaerung?: string;
        optionen?: { text: string; ist_korrekt: boolean }[];
      };
    }
  >({
    mutationFn: ({ id, payload }) =>
      api<FrageVorschlag>(`/api/fragen-vorschlaege/${id}/akzeptieren/`, {
        method: "POST",
        json: payload ?? {},
      }),
    onSuccess: (_d, v) => {
      qc.invalidateQueries({ queryKey: ["vorschlaege", v.kursId] });
      qc.invalidateQueries({ queryKey: ["kurs", v.kursId] });
    },
  });
}

export function useVerwerfeVorschlag() {
  const qc = useQueryClient();
  return useMutation<
    FrageVorschlag,
    ApiError,
    { id: number; kursId: number }
  >({
    mutationFn: ({ id }) =>
      api<FrageVorschlag>(`/api/fragen-vorschlaege/${id}/verwerfen/`, {
        method: "POST",
      }),
    onSuccess: (_d, v) =>
      qc.invalidateQueries({ queryKey: ["vorschlaege", v.kursId] }),
  });
}

export function useReorderModule() {
  const qc = useQueryClient();
  return useMutation<
    { reordered: number },
    ApiError,
    { kurs: number; modul_ids: number[] }
  >({
    mutationFn: (payload) =>
      api<{ reordered: number }>("/api/kurs-module/reorder/", {
        method: "POST",
        json: payload,
      }),
    onSuccess: (_d, vars) =>
      qc.invalidateQueries({ queryKey: ["kurs", vars.kurs] }),
  });
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
  quiz_modus: QuizModus;
  mindest_lesezeit_s: number;
  min_richtig_prozent: number;
  zertifikat_aktiv: boolean;
  module: {
    id: number;
    titel: string;
    reihenfolge: number;
    typ: ModulTyp;
    inhalt_md: string;
    youtube_url: string;
    asset_id: number | null;
    asset_url?: string | null;
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
      zertifikat_aktiv?: boolean;
    },
    ApiError,
    { besuchte_module?: number[] } | void
  >({
    mutationFn: (payload) =>
      api(`/api/public/schulung/${token}/abschliessen/`, {
        method: "POST",
        json: payload ?? {},
      }),
  });
}
