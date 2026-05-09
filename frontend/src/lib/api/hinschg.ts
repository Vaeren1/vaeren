/**
 * HinSchG-API-Hooks (Sprint 5).
 *
 * Public-Endpoints (kein Login):
 *  - submitMeldung
 *  - useMeldungStatus(token)
 *  - sendHinweisgeberNachricht(token, text)
 *
 * Interne Endpoints (auth):
 *  - useMeldungList / useMeldung(id)
 *  - usePatchMeldung / useBestaetigen / useAbschliessen
 *  - useAddBearbeitungsschritt
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

// --- Public ------------------------------------------------------------

export interface MeldungSubmitInput {
  titel: string;
  beschreibung: string;
  melder_kontakt?: string;
  anonym: boolean;
}

export interface MeldungSubmitResponse {
  eingangs_token: string;
  status_url: string;
  rueckmeldung_faellig_bis: string;
}

export function submitMeldung(payload: MeldungSubmitInput) {
  return api<MeldungSubmitResponse>("/api/public/hinschg/meldung/", {
    method: "POST",
    json: payload,
  });
}

export interface MeldungPublicStatusSchritt {
  timestamp: string;
  aktion: string;
}

export interface MeldungPublicStatus {
  status: string;
  eingegangen_am: string;
  bestaetigung_versandt_am: string | null;
  rueckmeldung_faellig_bis: string;
  abgeschlossen_am: string | null;
  bearbeitungsschritte: MeldungPublicStatusSchritt[];
}

export function useMeldungStatus(token: string | undefined) {
  return useQuery<MeldungPublicStatus, ApiError>({
    queryKey: ["meldung-status", token],
    queryFn: () =>
      api<MeldungPublicStatus>(`/api/public/hinschg/status/${token}/`),
    enabled: !!token,
    retry: false,
  });
}

export function sendHinweisgeberNachricht(token: string, nachricht: string) {
  return api<void>(`/api/public/hinschg/status/${token}/nachricht/`, {
    method: "POST",
    json: { nachricht },
  });
}

// --- Internal ----------------------------------------------------------

export type MeldungStatusValue =
  | "eingegangen"
  | "bestaetigt"
  | "in_pruefung"
  | "massnahme"
  | "abgeschlossen"
  | "abgewiesen";

export interface MeldungListItem {
  id: number;
  eingangs_token: string;
  anonym: boolean;
  titel: string;
  kategorie: string;
  schweregrad: string;
  status: MeldungStatusValue;
  status_display: string;
  eingegangen_am: string;
  rueckmeldung_faellig_bis: string;
}

export interface MeldungsTask {
  id: number;
  pflicht_typ: string;
  pflicht_typ_display: string;
  frist: string;
  status: string;
}

export interface BearbeitungsschrittIntern {
  id: number;
  aktion: string;
  notiz_verschluesselt: string;
  timestamp: string;
  bearbeiter: number | null;
  bearbeiter_email: string | null;
}

export interface MeldungIntern {
  id: number;
  eingangs_token: string;
  eingangs_kanal: string;
  eingangs_kanal_display: string;
  anonym: boolean;
  titel_verschluesselt: string;
  beschreibung_verschluesselt: string;
  melder_kontakt_verschluesselt: string;
  kategorie: string;
  schweregrad: string;
  status: MeldungStatusValue;
  status_display: string;
  eingegangen_am: string;
  bestaetigung_versandt_am: string | null;
  rueckmeldung_faellig_bis: string;
  abgeschlossen_am: string | null;
  archiv_loeschdatum: string | null;
  tasks: MeldungsTask[];
  bearbeitungsschritte: BearbeitungsschrittIntern[];
}

export function useMeldungList() {
  return useQuery<MeldungListItem[], ApiError>({
    queryKey: ["hinschg-meldungen"],
    queryFn: () => api<MeldungListItem[]>("/api/hinschg/meldungen/"),
  });
}

export function useMeldung(id: number | undefined) {
  return useQuery<MeldungIntern, ApiError>({
    queryKey: ["hinschg-meldung", id],
    queryFn: () => api<MeldungIntern>(`/api/hinschg/meldungen/${id}/`),
    enabled: id !== undefined,
  });
}

export interface MeldungPatchInput {
  kategorie?: string;
  schweregrad?: string;
  status?: MeldungStatusValue;
}

export function usePatchMeldung(id: number) {
  const qc = useQueryClient();
  return useMutation<MeldungIntern, ApiError, MeldungPatchInput>({
    mutationFn: (payload) =>
      api<MeldungIntern>(`/api/hinschg/meldungen/${id}/`, {
        method: "PATCH",
        json: payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["hinschg-meldung", id] });
      qc.invalidateQueries({ queryKey: ["hinschg-meldungen"] });
    },
  });
}

export function useBestaetigen(id: number) {
  const qc = useQueryClient();
  return useMutation<MeldungIntern, ApiError, void>({
    mutationFn: () =>
      api<MeldungIntern>(`/api/hinschg/meldungen/${id}/bestaetigen/`, {
        method: "POST",
        json: {},
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["hinschg-meldung", id] });
      qc.invalidateQueries({ queryKey: ["hinschg-meldungen"] });
    },
  });
}

export function useAbschliessen(id: number) {
  const qc = useQueryClient();
  return useMutation<MeldungIntern, ApiError, void>({
    mutationFn: () =>
      api<MeldungIntern>(`/api/hinschg/meldungen/${id}/abschliessen/`, {
        method: "POST",
        json: {},
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["hinschg-meldung", id] });
      qc.invalidateQueries({ queryKey: ["hinschg-meldungen"] });
    },
  });
}

export interface BearbeitungsschrittInput {
  aktion: string;
  notiz_verschluesselt: string;
}

export function useAddBearbeitungsschritt(id: number) {
  const qc = useQueryClient();
  return useMutation<
    BearbeitungsschrittIntern,
    ApiError,
    BearbeitungsschrittInput
  >({
    mutationFn: (payload) =>
      api<BearbeitungsschrittIntern>(
        `/api/hinschg/meldungen/${id}/bearbeitungsschritte/`,
        { method: "POST", json: payload },
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["hinschg-meldung", id] });
    },
  });
}
