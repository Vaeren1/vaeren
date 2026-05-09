import { useMutation } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export type MitarbeiterAnzahl =
  | "<50"
  | "50-120"
  | "121-250"
  | "251-500"
  | ">500";

export interface DemoRequestInput {
  firma: string;
  vorname: string;
  nachname: string;
  email: string;
  telefon?: string;
  mitarbeiter_anzahl?: MitarbeiterAnzahl | "";
  nachricht?: string;
  /** Honeypot — vom Backend ignoriert, aber stillschweigend gedroppt. */
  website?: string;
}

export interface DemoRequestResponse {
  detail: string;
}

export function useSubmitDemoRequest() {
  return useMutation<DemoRequestResponse, ApiError, DemoRequestInput>({
    mutationFn: (payload) =>
      api<DemoRequestResponse>("/api/demo/", { method: "POST", json: payload }),
  });
}
