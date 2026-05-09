import { useQuery } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export type ScoreLevel = "green" | "yellow" | "red";

export interface ModuleScore {
  modul: string;
  label: string;
  score: number;
  level: ScoreLevel;
  detail: string;
}

export interface ComplianceScore {
  master: number;
  level: ScoreLevel;
  score_pflichten: number;
  score_fristen: number;
  score_module: number;
  overdue_count: number;
  due_in_7d_count: number;
  total_active_tasks: number;
  modules: ModuleScore[];
  formula: string;
}

export interface DashboardTask {
  id: number;
  titel: string;
  modul: string;
  kategorie: string;
  frist: string;
  status: string;
  ueberfaellig: boolean;
}

export interface DashboardActivity {
  id: number;
  actor_email: string;
  aktion: string;
  target_type: string;
  target_id: number | null;
  diff: Record<string, unknown>;
  timestamp: string;
}

export interface DashboardData {
  score: ComplianceScore;
  this_week_tasks: DashboardTask[];
  overdue_tasks: DashboardTask[];
  recent_activity: DashboardActivity[];
  module_summary: {
    pflichtunterweisung: { aktive_wellen: number; abgeschlossen_30d: number };
    hinschg: { offene_meldungen: number; neu_30d: number };
  };
}

export function useDashboard() {
  return useQuery<DashboardData, ApiError>({
    queryKey: ["dashboard"],
    queryFn: () => api<DashboardData>("/api/dashboard/"),
    refetchInterval: 60_000,
  });
}
