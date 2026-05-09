import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export interface Mitarbeiter {
  id: number;
  vorname: string;
  nachname: string;
  email: string;
  abteilung: string;
  externe_id: string | null;
  aktiv: boolean;
}

export interface MitarbeiterPage {
  count: number;
  next: string | null;
  previous: string | null;
  results: Mitarbeiter[];
}

export interface MitarbeiterInput {
  vorname: string;
  nachname: string;
  email: string;
  abteilung: string;
  externe_id?: string | null;
  aktiv: boolean;
}

const KEY = "mitarbeiter";

export function useMitarbeiterList() {
  return useQuery<MitarbeiterPage, ApiError>({
    queryKey: [KEY],
    queryFn: () => api<MitarbeiterPage>("/api/mitarbeiter/"),
  });
}

export function useMitarbeiter(id: number | undefined) {
  return useQuery<Mitarbeiter, ApiError>({
    queryKey: [KEY, id],
    queryFn: () => api<Mitarbeiter>(`/api/mitarbeiter/${id}/`),
    enabled: id !== undefined,
  });
}

export function useCreateMitarbeiter() {
  const qc = useQueryClient();
  return useMutation<Mitarbeiter, ApiError, MitarbeiterInput>({
    mutationFn: (payload) =>
      api<Mitarbeiter>("/api/mitarbeiter/", { method: "POST", json: payload }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useUpdateMitarbeiter(id: number) {
  const qc = useQueryClient();
  return useMutation<Mitarbeiter, ApiError, MitarbeiterInput>({
    mutationFn: (payload) =>
      api<Mitarbeiter>(`/api/mitarbeiter/${id}/`, {
        method: "PATCH",
        json: payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [KEY] });
      qc.invalidateQueries({ queryKey: [KEY, id] });
    },
  });
}

export function useDeleteMitarbeiter() {
  const qc = useQueryClient();
  return useMutation<void, ApiError, number>({
    mutationFn: (id) =>
      api<void>(`/api/mitarbeiter/${id}/`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export const ROLES_THAT_CAN_EDIT_MITARBEITER = new Set([
  "geschaeftsfuehrer",
  "qm_leiter",
  "compliance_beauftragter",
]);
