import { useQuery } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export interface AuditEntry {
  id: number;
  actor: number | null;
  actor_email: string;
  aktion: string;
  target_type: string | null;
  target_object_id: number | null;
  aenderung_diff: Record<string, unknown>;
  ip_address: string | null;
  timestamp: string;
}

export interface AuditFilters {
  actor?: number;
  aktion?: string;
  target_type?: string;
  from?: string;
  to?: string;
}

function buildQuery(filters: AuditFilters): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== "" && v !== null) params.set(k, String(v));
  }
  return params.toString();
}

export function useAuditList(filters: AuditFilters = {}) {
  const qs = buildQuery(filters);
  return useQuery<AuditEntry[], ApiError>({
    queryKey: ["audit", filters],
    queryFn: async () => {
      const res = await api<AuditEntry[] | { results: AuditEntry[] }>(
        `/api/audit/${qs ? `?${qs}` : ""}`,
      );
      return Array.isArray(res) ? res : res.results;
    },
  });
}

export function buildAuditCsvUrl(filters: AuditFilters = {}) {
  const qs = buildQuery(filters);
  return `/api/audit/export.csv/${qs ? `?${qs}` : ""}`;
}
