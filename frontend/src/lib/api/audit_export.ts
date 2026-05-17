/**
 * API-Client für Audit-Export (Phase 3).
 *
 * Backend-Routes:
 * - GET/POST   /api/audit-export/profiles/
 * - GET/PATCH  /api/audit-export/profiles/:id/
 * - POST       /api/audit-export/profiles/:id/runs/start/
 * - POST       /api/audit-export/profiles/:id/preview/
 * - GET        /api/audit-export/runs/
 * - GET        /api/audit-export/runs/:id/
 * - GET        /api/audit-export/runs/:id/download/zip/
 * - GET        /api/audit-export/runs/:id/download/pdf/
 * - POST       /api/audit-export/verify/  (public, kein Auth)
 */

import { api } from "./client";

export type NormScope =
  | "iso_27001"
  | "iso_42001"
  | "nis2"
  | "dsgvo"
  | "ai_act"
  | "arbeitsschutz"
  | "pflichtunterweisung"
  | "hinschg"
  | "avv"
  | "datenpannen"
  | "transparenzregister";

export type AuditTemplate =
  | "iso_27001_audit"
  | "gap_analyse"
  | "tisax_light"
  | "ai_act_konformitaet"
  | "nis2_behoerden_vorlage"
  | "bfdi_template"
  | "geschaeftsfuehrer_mappe";

export type EvidenceMode = "embed" | "reference";

export type RunStatus = "queued" | "running" | "done" | "failed" | "cancelled";

export interface AuditExportProfile {
  id: number;
  name: string;
  template: AuditTemplate;
  norm_scope: NormScope[];
  zeitraum_von: string;
  zeitraum_bis: string;
  filter_json: Record<string, unknown>;
  evidence_mode: EvidenceMode;
  anonymisieren_pii: boolean;
  watermark_draft: boolean;
  erstellt_von: number | null;
  erstellt_am: string;
  aktualisiert_am: string;
}

export interface AuditExportProfileCreate {
  name: string;
  template: AuditTemplate;
  norm_scope: NormScope[];
  zeitraum_von: string;
  zeitraum_bis: string;
  evidence_mode?: EvidenceMode;
  anonymisieren_pii?: boolean;
  watermark_draft?: boolean;
}

export interface AuditExportRunListItem {
  id: number;
  mappe_id: string;
  profile: number;
  status: RunStatus;
  started_at: string;
  finished_at: string | null;
  evidence_count: number;
  file_size_bytes: number;
  file_hash_sha256: string;
  error: string;
}

export interface AuditExportRunDetail extends AuditExportRunListItem {
  started_by: number | null;
  result_path: string;
  zip_path: string;
  pdf_path: string;
  oscal_ssp_path: string;
  oscal_assessment_path: string;
  pdf_hash_sha256: string;
  generation_log: Array<{
    ts: string;
    level: string;
    aggregator: string;
    message: string;
  }>;
}

export interface RunPreview {
  evidence_count: number;
  counts_per_aggregator: Record<string, number>;
  geschaetzte_groesse_kb: number;
}

export interface VerifyRequest {
  mappe_id: string;
  file_sha256: string;
}

export interface VerifyResponse {
  verified: boolean;
  reason?: string;
  tenant?: string;
  norm_scope?: NormScope[];
  generated_at?: string;
}

// --- Profile -------------------------------------------------------

export async function listProfiles(): Promise<{
  count: number;
  results: AuditExportProfile[];
}> {
  return api("/api/audit-export/profiles/");
}

export async function getProfile(id: number): Promise<AuditExportProfile> {
  return api(`/api/audit-export/profiles/${id}/`);
}

export async function createProfile(
  payload: AuditExportProfileCreate,
): Promise<AuditExportProfile> {
  return api("/api/audit-export/profiles/", { method: "POST", json: payload });
}

export async function updateProfile(
  id: number,
  payload: Partial<AuditExportProfile>,
): Promise<AuditExportProfile> {
  return api(`/api/audit-export/profiles/${id}/`, {
    method: "PATCH",
    json: payload,
  });
}

export async function deleteProfile(id: number): Promise<void> {
  return api(`/api/audit-export/profiles/${id}/`, { method: "DELETE" });
}

export async function startRun(profileId: number): Promise<AuditExportRunListItem> {
  return api(`/api/audit-export/profiles/${profileId}/runs/start/`, {
    method: "POST",
  });
}

export async function previewRun(profileId: number): Promise<RunPreview> {
  return api(`/api/audit-export/profiles/${profileId}/preview/`, {
    method: "POST",
  });
}

// --- Runs -----------------------------------------------------------

export async function listRuns(): Promise<{
  count: number;
  results: AuditExportRunListItem[];
}> {
  return api("/api/audit-export/runs/");
}

export async function getRun(id: number): Promise<AuditExportRunDetail> {
  return api(`/api/audit-export/runs/${id}/`);
}

export function downloadUrls(runId: number): {
  zip: string;
  pdf: string;
  oscalSsp: string;
  oscalAssessment: string;
} {
  const base = `/api/audit-export/runs/${runId}/download`;
  return {
    zip: `${base}/zip/`,
    pdf: `${base}/pdf/`,
    oscalSsp: `${base}/oscal-ssp/`,
    oscalAssessment: `${base}/oscal-assessment/`,
  };
}

// --- Verify (public) -----------------------------------------------

export async function verifyMappe(payload: VerifyRequest): Promise<VerifyResponse> {
  // Public-Route — kein Cookie nötig, aber api() schickt es trotzdem mit.
  return api("/api/audit-export/verify/", {
    method: "POST",
    json: payload,
  });
}

// --- Helper-Lookups -------------------------------------------------

export const NORM_LABEL: Record<NormScope, string> = {
  iso_27001: "ISO/IEC 27001",
  iso_42001: "ISO/IEC 42001",
  nis2: "NIS2",
  dsgvo: "DSGVO",
  ai_act: "EU AI Act",
  arbeitsschutz: "Arbeitsschutz",
  pflichtunterweisung: "Pflichtunterweisungen",
  hinschg: "HinSchG",
  avv: "AVV (Art. 28 DSGVO)",
  datenpannen: "Datenpannen",
  transparenzregister: "Transparenzregister",
};

export const TEMPLATE_LABEL: Record<AuditTemplate, string> = {
  iso_27001_audit: "ISO-27001 Annex-A Audit",
  gap_analyse: "GAP-Analyse",
  tisax_light: "TISAX-Light",
  ai_act_konformitaet: "AI-Act Konformitätsbericht",
  nis2_behoerden_vorlage: "NIS2 Behörden-Vorlage",
  bfdi_template: "BfDI/LDA Datenschutz-Anfrage",
  geschaeftsfuehrer_mappe: "GF-Mappe (Executive Summary)",
};
